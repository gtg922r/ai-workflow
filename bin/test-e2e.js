#!/usr/bin/env node

/**
 * End-to-end test for the AI Workflow Installer
 * 
 * Tests actual file copy/symlink operations to a temporary directory.
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
      if (fs.existsSync(dest)) {
        fs.rmSync(dest, { recursive: true, force: true });
      }
      fs.symlinkSync(src, dest, fs.statSync(src).isDirectory() ? 'dir' : 'file');
      return 'symlink';
    } catch {
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

// Create a temporary test directory
const TEST_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'ai-workflow-test-'));
console.log(`${style.dim(`Test directory: ${TEST_DIR}`)}`);

try {
  // Test 1: Copy a command file
  testSection('Command Installation (Copy)');
  
  const srcCommand = path.join(REPO_ROOT, 'commands', 'gemini', 'workflow', 'create-pr.toml');
  const destCommand = path.join(TEST_DIR, '.gemini', 'commands', 'workflow', 'create-pr.toml');
  
  const copyMethod = linkOrCopy(srcCommand, destCommand, false);
  test('Command copied successfully', fs.existsSync(destCommand));
  test('Copy method used', copyMethod === 'copy');
  
  const srcContent = fs.readFileSync(srcCommand, 'utf-8');
  const destContent = fs.readFileSync(destCommand, 'utf-8');
  test('Content matches', srcContent === destContent);
  
  // Test 2: Symlink a skill directory
  testSection('Skill Installation (Symlink)');
  
  const srcSkill = path.join(REPO_ROOT, 'skills', 'command-creator');
  const destSkill = path.join(TEST_DIR, '.gemini', 'skills', 'command-creator');
  
  const symlinkMethod = linkOrCopy(srcSkill, destSkill, true);
  test('Skill symlinked/copied successfully', fs.existsSync(destSkill));
  test('Is directory', fs.statSync(destSkill).isDirectory() || fs.lstatSync(destSkill).isSymbolicLink());
  
  // Verify skill content is accessible
  const skillMd = path.join(destSkill, 'SKILL.md');
  test('SKILL.md accessible', fs.existsSync(skillMd));
  
  // Test 3: Copy a script directory
  testSection('Script Installation (Copy)');
  
  const srcScript = path.join(REPO_ROOT, 'scripts', 'runner-wiggum');
  const destScript = path.join(TEST_DIR, '.gemini', 'scripts', 'runner-wiggum');
  
  const scriptMethod = linkOrCopy(srcScript, destScript, false);
  test('Script directory copied', fs.existsSync(destScript));
  test('Script contains expected files', fs.existsSync(path.join(destScript, 'ralph.py')));
  
  // Test 4: Multiple agent targets
  testSection('Multi-Agent Installation');
  
  const srcSkill2 = path.join(REPO_ROOT, 'skills', 'skill-creator');
  
  // Install to Claude target
  const destClaude = path.join(TEST_DIR, '.claude', 'skills', 'skill-creator');
  linkOrCopy(srcSkill2, destClaude, false);
  test('Claude skill installed', fs.existsSync(destClaude));
  
  // Install to Codex target
  const destCodex = path.join(TEST_DIR, '.codex', 'skills', 'skill-creator');
  linkOrCopy(srcSkill2, destCodex, false);
  test('Codex skill installed', fs.existsSync(destCodex));
  
  // Verify each has independent copy
  test('Claude has SKILL.md', fs.existsSync(path.join(destClaude, 'SKILL.md')));
  test('Codex has SKILL.md', fs.existsSync(path.join(destCodex, 'SKILL.md')));
  
  // Test 5: Overwrite existing installation
  testSection('Overwrite Behavior');
  
  // Modify the existing file
  fs.writeFileSync(destCommand, '# modified');
  
  // Reinstall
  linkOrCopy(srcCommand, destCommand, false);
  const newContent = fs.readFileSync(destCommand, 'utf-8');
  test('Overwrite replaces content', newContent === srcContent);
  
} finally {
  // Cleanup
  testSection('Cleanup');
  fs.rmSync(TEST_DIR, { recursive: true, force: true });
  test('Test directory cleaned up', !fs.existsSync(TEST_DIR));
}

// Summary
console.log();
console.log(style.bold('Summary'));
console.log(style.dim('─'.repeat(40)));
console.log(`  ${style.green('Passed')}: ${passed}`);
console.log(`  ${style.red('Failed')}: ${failed}`);
console.log();

process.exit(failed > 0 ? 1 : 0);
