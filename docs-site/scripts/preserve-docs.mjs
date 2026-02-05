#!/usr/bin/env node
/**
 * Preserve/restore important files in docs/ that should survive Astro builds.
 * 
 * Usage:
 *   node preserve-docs.mjs --save    # Copy files to temp before build
 *   node preserve-docs.mjs --restore # Restore files after build
 */

import { existsSync, mkdirSync, copyFileSync, rmSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..', '..');
const DOCS_DIR = join(ROOT, 'docs');
const TEMP_DIR = join(__dirname, '.preserve-temp');

// Files to preserve (relative to docs/)
const PRESERVE_FILES = [
  'llms.txt',
  'llms-full.txt',
  '.nojekyll',
  'foundry-docs-manifest.json'
];

const mode = process.argv[2];

if (mode === '--save') {
  console.log('📦 Preserving docs files before build...');
  
  // Create temp directory
  if (!existsSync(TEMP_DIR)) {
    mkdirSync(TEMP_DIR, { recursive: true });
  }
  
  // Copy files to temp
  for (const file of PRESERVE_FILES) {
    const src = join(DOCS_DIR, file);
    const dest = join(TEMP_DIR, file);
    
    if (existsSync(src)) {
      copyFileSync(src, dest);
      console.log(`  ✓ Saved ${file}`);
    } else {
      console.log(`  ⚠ Skipped ${file} (not found)`);
    }
  }
  
  console.log('✅ Files preserved to temp directory');
  
} else if (mode === '--restore') {
  console.log('📦 Restoring preserved docs files...');
  
  if (!existsSync(TEMP_DIR)) {
    console.log('⚠ No temp directory found, skipping restore');
    process.exit(0);
  }
  
  // Ensure docs directory exists
  if (!existsSync(DOCS_DIR)) {
    mkdirSync(DOCS_DIR, { recursive: true });
  }
  
  // Restore files from temp
  for (const file of PRESERVE_FILES) {
    const src = join(TEMP_DIR, file);
    const dest = join(DOCS_DIR, file);
    
    if (existsSync(src)) {
      copyFileSync(src, dest);
      console.log(`  ✓ Restored ${file}`);
    }
  }
  
  // Clean up temp directory
  rmSync(TEMP_DIR, { recursive: true, force: true });
  console.log('✅ Files restored and temp cleaned up');
  
} else {
  console.error('Usage: node preserve-docs.mjs --save|--restore');
  process.exit(1);
}
