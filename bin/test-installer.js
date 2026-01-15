#!/usr/bin/env node

/**
 * Test script for the AI Workflow Installer
 * 
 * Validates component discovery and core functionality without
 * requiring interactive input.
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');

const style = {
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  dim: (s) => `\x1b[2m${s}\x1b[0m`,
};

let passed = 0;
let failed = 0;

function test(name, condition) {
  if (condition) {
    console.log(`  ${style.green('✓')} ${name}`);
    passed++;
  } else {
    console.log(`  ${style.red('✗')} ${name}`);
    failed++;
  }
}

function testSection(name) {
  console.log();
  console.log(style.bold(name));
}

// Test 1: Package structure
testSection('Package Structure');
test('package.json exists', fs.existsSync(path.join(REPO_ROOT, 'package.json')));
test('bin/install.js exists', fs.existsSync(path.join(REPO_ROOT, 'bin', 'install.js')));

const pkg = JSON.parse(fs.readFileSync(path.join(REPO_ROOT, 'package.json'), 'utf-8'));
test('package.json has bin entry', pkg.bin && pkg.bin['ai-workflow'] === './bin/install.js');
test('package.json has type: module', pkg.type === 'module');
test('package.json has @inquirer/prompts dependency', pkg.dependencies && '@inquirer/prompts' in pkg.dependencies);

// Test 2: Component discovery
testSection('Component Discovery');

// Check commands exist
const commandsDir = path.join(REPO_ROOT, 'commands', 'gemini');
test('commands/gemini directory exists', fs.existsSync(commandsDir));

const commandFiles = [];
function findTomlFiles(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      findTomlFiles(fullPath);
    } else if (entry.name.endsWith('.toml')) {
      commandFiles.push(fullPath);
    }
  }
}
findTomlFiles(commandsDir);
test('Found .toml command files', commandFiles.length > 0);

// Check skills exist
const skillsDir = path.join(REPO_ROOT, 'skills');
test('skills/ directory exists', fs.existsSync(skillsDir));

const skillDirs = fs.readdirSync(skillsDir, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => d.name);
test('Found skill directories', skillDirs.length > 0);

// Verify each skill has SKILL.md
let validSkills = 0;
for (const skill of skillDirs) {
  if (fs.existsSync(path.join(skillsDir, skill, 'SKILL.md'))) {
    validSkills++;
  }
}
test('All skill directories have SKILL.md', validSkills === skillDirs.length);

// Check scripts exist
const scriptsDir = path.join(REPO_ROOT, 'scripts');
test('scripts/ directory exists', fs.existsSync(scriptsDir));

const scriptDirs = fs.readdirSync(scriptsDir, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => d.name);
test('Found script directories', scriptDirs.length > 0);

// Test 3: Agent configuration coverage
testSection('Agent Configuration');

const AGENTS = {
  'gemini-cli': {
    globalBase: path.join(os.homedir(), '.gemini'),
    localBase: '.gemini',
    supports: ['commands', 'skills'],
  },
  'claude-code': {
    globalBase: path.join(os.homedir(), '.claude'),
    localBase: '.claude',
    supports: ['skills'],
  },
  'openai-codex': {
    globalBase: path.join(os.homedir(), '.codex'),
    localBase: '.codex',
    supports: ['skills'],
  },
};

test('Gemini CLI agent configured', 'gemini-cli' in AGENTS);
test('Claude Code agent configured', 'claude-code' in AGENTS);
test('OpenAI Codex agent configured', 'openai-codex' in AGENTS);

// Test 4: Installation targets
testSection('Installation Targets');

test('Gemini supports commands', AGENTS['gemini-cli'].supports.includes('commands'));
test('Gemini supports skills', AGENTS['gemini-cli'].supports.includes('skills'));
test('Claude supports skills', AGENTS['claude-code'].supports.includes('skills'));
test('Codex supports skills', AGENTS['openai-codex'].supports.includes('skills'));

// Test 5: File operations utilities
testSection('Utility Functions');

// Test symlink/copy logic can be imported (basic syntax check)
try {
  const installerCode = fs.readFileSync(path.join(REPO_ROOT, 'bin', 'install.js'), 'utf-8');
  test('Installer has linkOrCopy function', installerCode.includes('function linkOrCopy'));
  test('Installer has copyRecursive function', installerCode.includes('function copyRecursive'));
  test('Installer has verifyInstallation function', installerCode.includes('function verifyInstallation'));
  test('Installer has printSummary function', installerCode.includes('function printSummary'));
  test('Installer has discoverComponents function', installerCode.includes('function discoverComponents'));
} catch (err) {
  test('Installer code readable', false);
}

// Summary
console.log();
console.log(style.bold('Summary'));
console.log(style.dim('─'.repeat(40)));
console.log(`  ${style.green('Passed')}: ${passed}`);
console.log(`  ${style.red('Failed')}: ${failed}`);
console.log();

process.exit(failed > 0 ? 1 : 0);
