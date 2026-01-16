#!/usr/bin/env node

/**
 * AI Workflow Installer
 * 
 * Interactive CLI for installing AI workflow components (commands, skills, scripts)
 * to different AI agent targets (Gemini, Claude, Codex).
 * 
 * Usage:
 *   npx --yes --package github:gtg922r/ai-workflow ai-workflow
 */

import { select, checkbox, confirm } from '@inquirer/prompts';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

// Agent configuration: defines target directories for each agent
const AGENTS = {
  'gemini-cli': {
    name: 'Gemini CLI',
    globalBase: path.join(os.homedir(), '.gemini'),
    localBase: '.gemini',
    supports: ['commands', 'skills', 'extensions'],
    paths: {
      commands: 'commands',
      skills: 'skills',
      extensions: 'extensions',
    },
  },
  'claude-code': {
    name: 'Claude Code',
    globalBase: path.join(os.homedir(), '.claude'),
    localBase: '.claude',
    supports: ['skills'],
    paths: {
      skills: 'skills',
    },
  },
  'openai-codex': {
    name: 'OpenAI Codex',
    globalBase: path.join(os.homedir(), '.codex'),
    localBase: '.codex',
    supports: ['skills'],
    paths: {
      skills: 'skills',
    },
  },
};

// Styling helpers for console output
const style = {
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
  dim: (s) => `\x1b[2m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  cyan: (s) => `\x1b[36m${s}\x1b[0m`,
};

const icons = {
  success: style.green('✓'),
  warning: style.yellow('⚠'),
  error: style.red('✗'),
  arrow: style.cyan('→'),
  bullet: style.dim('•'),
};

/**
 * Discovers available components from the repository
 */
function discoverComponents() {
  const components = {
    commands: [],
    skills: [],
    extensions: [],
    scripts: [],
  };

  // Discover commands (Gemini-specific, organized by category)
  const commandsDir = path.join(REPO_ROOT, 'commands', 'gemini');
  if (fs.existsSync(commandsDir)) {
    discoverCommandsRecursive(commandsDir, '', components.commands);
  }

  // Discover skills
  const skillsDir = path.join(REPO_ROOT, 'skills');
  if (fs.existsSync(skillsDir)) {
    const skillNames = fs.readdirSync(skillsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);
    
    for (const name of skillNames) {
      const skillPath = path.join(skillsDir, name);
      const skillMd = path.join(skillPath, 'SKILL.md');
      if (fs.existsSync(skillMd)) {
        const description = extractSkillDescription(skillMd);
        components.skills.push({
          name,
          path: skillPath,
          description,
        });
      }
    }
  }

  // Discover extensions
  const extensionsDir = path.join(REPO_ROOT, 'extensions');
  if (fs.existsSync(extensionsDir)) {
    const extensionNames = fs.readdirSync(extensionsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);
    
    for (const name of extensionNames) {
      const extensionPath = path.join(extensionsDir, name);
      const readmePath = path.join(extensionPath, 'README.md');
      let description = 'Agent extension';
      if (fs.existsSync(readmePath)) {
        description = extractFirstLine(readmePath) || description;
      }
      components.extensions.push({
        name,
        path: extensionPath,
        description,
      });
    }
  }

  // Discover scripts
  const scriptsDir = path.join(REPO_ROOT, 'scripts');
  if (fs.existsSync(scriptsDir)) {
    const scriptNames = fs.readdirSync(scriptsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);
    
    for (const name of scriptNames) {
      const scriptPath = path.join(scriptsDir, name);
      const readmePath = path.join(scriptPath, 'README.md');
      let description = 'Standalone script';
      if (fs.existsSync(readmePath)) {
        description = extractFirstLine(readmePath) || description;
      }
      components.scripts.push({
        name,
        path: scriptPath,
        description,
      });
    }
  }

  return components;
}

/**
 * Recursively discovers commands in nested directories
 */
function discoverCommandsRecursive(dir, prefix, results) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      discoverCommandsRecursive(fullPath, prefix ? `${prefix}/${entry.name}` : entry.name, results);
    } else if (entry.name.endsWith('.toml')) {
      const cmdName = entry.name.replace('.toml', '');
      const fullName = prefix ? `${prefix}/${cmdName}` : cmdName;
      const description = extractTomlDescription(fullPath);
      results.push({
        name: fullName,
        path: fullPath,
        relativePath: prefix ? path.join(prefix, entry.name) : entry.name,
        description,
      });
    }
  }
}

/**
 * Extracts description from TOML file
 */
function extractTomlDescription(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const match = content.match(/description\s*=\s*"([^"]+)"/);
    return match ? match[1] : 'Custom command';
  } catch {
    return 'Custom command';
  }
}

/**
 * Extracts description from SKILL.md frontmatter
 */
function extractSkillDescription(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const match = content.match(/description:\s*(.+)/);
    return match ? match[1].trim() : 'Agent skill';
  } catch {
    return 'Agent skill';
  }
}

/**
 * Extracts first meaningful line from a markdown file
 */
function extractFirstLine(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        return trimmed.slice(0, 80);
      }
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Copies a file or directory recursively
 */
function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    const entries = fs.readdirSync(src);
    for (const entry of entries) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

/**
 * Creates a symlink, with fallback to copy on failure
 */
function linkOrCopy(src, dest, useSymlink) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  
  if (useSymlink) {
    try {
      // Remove existing symlink/file if present
      if (fs.existsSync(dest)) {
        fs.rmSync(dest, { recursive: true, force: true });
      }
      fs.symlinkSync(src, dest, fs.statSync(src).isDirectory() ? 'dir' : 'file');
      return 'symlink';
    } catch (err) {
      // Fallback to copy on symlink failure (e.g., Windows without admin)
      copyRecursive(src, dest);
      return 'copy';
    }
  } else {
    if (fs.existsSync(dest)) {
      fs.rmSync(dest, { recursive: true, force: true });
    }
    copyRecursive(src, dest);
    return 'copy';
  }
}

/**
 * Verifies that a component was installed correctly
 */
function verifyInstallation(destPath, srcPath) {
  if (!fs.existsSync(destPath)) {
    return { success: false, reason: 'Destination does not exist' };
  }
  
  const srcStat = fs.statSync(srcPath);
  const destStat = fs.lstatSync(destPath);
  
  // If it's a symlink, verify it points to the right place
  if (destStat.isSymbolicLink()) {
    const linkTarget = fs.readlinkSync(destPath);
    if (path.resolve(path.dirname(destPath), linkTarget) !== path.resolve(srcPath)) {
      return { success: false, reason: 'Symlink points to wrong location' };
    }
  }
  
  return { success: true };
}

/**
 * Prints a formatted header
 */
function printHeader() {
  console.log();
  console.log(style.bold('  AI Workflow Installer'));
  console.log(style.dim('  Install commands, skills, and scripts for AI agents'));
  console.log();
}

/**
 * Prints installation summary
 */
function printSummary(results) {
  console.log();
  console.log(style.bold('Installation Summary'));
  console.log(style.dim('─'.repeat(50)));
  
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);
  
  if (successful.length > 0) {
    console.log();
    console.log(`${icons.success} ${style.green(`${successful.length} component(s) installed successfully`)}`);
    for (const result of successful) {
      console.log(`  ${icons.bullet} ${result.name} ${icons.arrow} ${style.dim(result.dest)} ${style.dim(`(${result.method})`)}`);
    }
  }
  
  if (failed.length > 0) {
    console.log();
    console.log(`${icons.error} ${style.red(`${failed.length} component(s) failed`)}`);
    for (const result of failed) {
      console.log(`  ${icons.bullet} ${result.name}: ${style.dim(result.reason)}`);
    }
  }
  
  console.log();
  console.log(style.dim('─'.repeat(50)));
  
  if (failed.length === 0) {
    console.log(style.green('All installations completed successfully!'));
  } else {
    console.log(style.yellow('Some installations failed. Check the errors above.'));
  }
  console.log();
}

/**
 * Main installer flow
 */
async function main() {
  printHeader();
  
  // Discover available components
  const components = discoverComponents();
  
  const hasComponents = 
    components.commands.length > 0 || 
    components.skills.length > 0 || 
    components.extensions.length > 0 || 
    components.scripts.length > 0;
  
  if (!hasComponents) {
    console.log(`${icons.warning} No installable components found in repository.`);
    process.exit(0);
  }
  
  // Step 1: Select target agent
  const agent = await select({
    message: 'Select target agent:',
    choices: Object.entries(AGENTS).map(([key, config]) => ({
      value: key,
      name: config.name,
      description: `Installs to ${config.globalBase}`,
    })),
  });
  
  const agentConfig = AGENTS[agent];
  
  // Step 2: Select installation scope
  const scope = await select({
    message: 'Select installation scope:',
    choices: [
      {
        value: 'global',
        name: 'Global (user profile)',
        description: `Installs to ${agentConfig.globalBase}`,
      },
      {
        value: 'local',
        name: 'Local (current project)',
        description: `Installs to ./${agentConfig.localBase}`,
      },
    ],
  });
  
  const baseDir = scope === 'global' 
    ? agentConfig.globalBase 
    : path.resolve(process.cwd(), agentConfig.localBase);
  
  // Step 3: Select components to install
  const selectedComponents = [];
  
  // Commands
  if (agentConfig.supports.includes('commands') && components.commands.length > 0) {
    const selectedCommands = await checkbox({
      message: 'Select commands to install:',
      choices: components.commands.map(cmd => ({
        value: cmd,
        name: cmd.name,
        description: cmd.description,
        checked: true,
      })),
    });
    selectedComponents.push(...selectedCommands.map(c => ({ ...c, type: 'command' })));
  }
  
  // Skills
  if (agentConfig.supports.includes('skills') && components.skills.length > 0) {
    const selectedSkills = await checkbox({
      message: 'Select skills to install:',
      choices: components.skills.map(skill => ({
        value: skill,
        name: skill.name,
        description: skill.description,
        checked: true,
      })),
    });
    selectedComponents.push(...selectedSkills.map(s => ({ ...s, type: 'skill' })));
  }

  // Extensions
  if (agentConfig.supports.includes('extensions') && components.extensions.length > 0) {
    const selectedExtensions = await checkbox({
      message: 'Select extensions to install:',
      choices: components.extensions.map(ext => ({
        value: ext,
        name: ext.name,
        description: ext.description,
        checked: true,
      })),
    });
    selectedComponents.push(...selectedExtensions.map(e => ({ ...e, type: 'extension' })));
  }
  
  // Scripts (available for all agents, but install to custom location)
  if (components.scripts.length > 0) {
    const selectedScripts = await checkbox({
      message: 'Select scripts to install:',
      choices: components.scripts.map(script => ({
        value: script,
        name: script.name,
        description: script.description,
        checked: false,
      })),
    });
    selectedComponents.push(...selectedScripts.map(s => ({ ...s, type: 'script' })));
  }
  
  if (selectedComponents.length === 0) {
    console.log();
    console.log(`${icons.warning} No components selected. Nothing to install.`);
    process.exit(0);
  }
  
  // Step 4: Select installation method
  const method = await select({
    message: 'Installation method:',
    choices: [
      {
        value: 'symlink',
        name: 'Symlink (recommended)',
        description: 'Creates links to source files - updates automatically',
      },
      {
        value: 'copy',
        name: 'Copy',
        description: 'Copies files - requires reinstall to update',
      },
    ],
  });
  
  const useSymlink = method === 'symlink';
  
  // Confirm installation
  console.log();
  console.log(style.bold('Installation Plan:'));
  console.log(`  ${icons.bullet} Agent: ${agentConfig.name}`);
  console.log(`  ${icons.bullet} Scope: ${scope === 'global' ? 'Global' : 'Local'}`);
  console.log(`  ${icons.bullet} Base directory: ${baseDir}`);
  console.log(`  ${icons.bullet} Components: ${selectedComponents.length}`);
  console.log(`  ${icons.bullet} Method: ${useSymlink ? 'Symlink' : 'Copy'}`);
  console.log();
  
  const proceed = await confirm({
    message: 'Proceed with installation?',
    default: true,
  });
  
  if (!proceed) {
    console.log(`${icons.warning} Installation cancelled.`);
    process.exit(0);
  }
  
  // Step 5: Perform installation
  console.log();
  console.log(style.bold('Installing...'));
  
  const results = [];
  
  for (const component of selectedComponents) {
    let destPath;
    
    switch (component.type) {
      case 'command':
        // Commands go to commands/<relative-path>
        destPath = path.join(baseDir, agentConfig.paths.commands, component.relativePath);
        break;
      case 'skill':
        // Skills go to skills/<skill-name>/
        destPath = path.join(baseDir, agentConfig.paths.skills, component.name);
        break;
      case 'extension':
        // Extensions go to extensions/<extension-name>/
        destPath = path.join(baseDir, agentConfig.paths.extensions, component.name);
        break;
      case 'script':
        // Scripts go to scripts/<script-name>/
        destPath = path.join(baseDir, 'scripts', component.name);
        break;
    }
    
    try {
      const actualMethod = linkOrCopy(component.path, destPath, useSymlink);
      const verification = verifyInstallation(destPath, component.path);
      
      if (verification.success) {
        console.log(`  ${icons.success} ${component.name}`);
        results.push({
          name: component.name,
          type: component.type,
          dest: destPath,
          method: actualMethod,
          success: true,
        });
      } else {
        console.log(`  ${icons.error} ${component.name} - ${verification.reason}`);
        results.push({
          name: component.name,
          type: component.type,
          dest: destPath,
          success: false,
          reason: verification.reason,
        });
      }
    } catch (err) {
      console.log(`  ${icons.error} ${component.name} - ${err.message}`);
      results.push({
        name: component.name,
        type: component.type,
        dest: destPath,
        success: false,
        reason: err.message,
      });
    }
  }
  
  // Step 6: Print summary
  printSummary(results);
  
  // Exit with appropriate code
  const anyFailed = results.some(r => !r.success);
  process.exit(anyFailed ? 1 : 0);
}

// Run the installer
main().catch(err => {
  console.error(`${icons.error} ${style.red('Installation failed:')} ${err.message}`);
  process.exit(1);
});
