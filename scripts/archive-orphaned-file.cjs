#!/usr/bin/env node

/**
 * archive-orphaned-file.cjs
 * 
 * This script helps to archive orphaned files following the project's 
 * never-delete-files rule by moving them to the archive directory.
 * 
 * Usage:
 *   node scripts/archive-orphaned-file.cjs <file-path>
 * 
 * Example:
 *   node scripts/archive-orphaned-file.cjs src/components/unused-component.tsx
 */

const fs = require('fs');
const path = require('path');

// Get the file path from command line arguments
const filePath = process.argv[2];

if (!filePath) {
  console.error('Error: File path is required');
  console.log('Usage: node scripts/archive-orphaned-file.cjs <file-path>');
  process.exit(1);
}

// Resolve the file path relative to the project root
const rootDir = path.resolve(__dirname, '..');
const resolvedFilePath = path.resolve(rootDir, filePath);
const relativeFilePath = path.relative(rootDir, resolvedFilePath);

// Check if the file exists
if (!fs.existsSync(resolvedFilePath)) {
  console.error(`Error: File '${relativeFilePath}' does not exist`);
  process.exit(1);
}

// Create the destination path in the archived_orphan directory
const archiveRoot = path.join(rootDir, 'archived_orphan');
const archiveDir = path.dirname(path.join(archiveRoot, relativeFilePath));

// Create the directory structure if it doesn't exist
if (!fs.existsSync(archiveDir)) {
  fs.mkdirSync(archiveDir, { recursive: true });
  console.log(`Created directory: ${path.relative(rootDir, archiveDir)}`);
}

// Determine the destination file name, handling duplicates
const baseName = path.basename(relativeFilePath, path.extname(relativeFilePath));
const ext = path.extname(relativeFilePath);
let destFileName = baseName + ext;
let destFilePath = path.join(archiveDir, destFileName);
let counter = 1;
while (fs.existsSync(destFilePath)) {
  destFileName = `${baseName}-${counter}${ext}`;
  destFilePath = path.join(archiveDir, destFileName);
  counter++;
}

// Move the file to the archived_orphan directory (do not delete, just move)
try {
  fs.renameSync(resolvedFilePath, destFilePath);
  console.log(`Successfully archived file:`);
  console.log(`  - From: ${relativeFilePath}`);
  console.log(`  - To:   ${path.relative(rootDir, destFilePath)}`);

  // Add an entry to FILE_CLEANUP_CHECKLIST.md
  const cleanupFilePath = path.join(rootDir, 'docs', 'FILE_CLEANUP_CHECKLIST.md');
  if (fs.existsSync(cleanupFilePath)) {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const entry = `\n## ${date} - Archived ${relativeFilePath}\n\n- **File**: \`${relativeFilePath}\`\n- **Reason**: Identified as orphaned by dependency analysis\n- **Action**: Moved to \`${path.relative(rootDir, destFilePath)}\`\n`;
    fs.appendFileSync(cleanupFilePath, entry);
    console.log(`Updated FILE_CLEANUP_CHECKLIST.md with the archived file entry`);
  } else {
    console.warn(`Warning: FILE_CLEANUP_CHECKLIST.md does not exist, skipping update`);
  }

} catch (error) {
  console.error(`Error archiving file: ${error.message}`);
  process.exit(1);
}

console.log('\nRemember to commit these changes with a descriptive message!'); 