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

// Create the destination path in the archive directory
const archiveFilePath = path.join(rootDir, 'archive', relativeFilePath);
const archiveDir = path.dirname(archiveFilePath);

// Create the directory structure if it doesn't exist
if (!fs.existsSync(archiveDir)) {
  fs.mkdirSync(archiveDir, { recursive: true });
  console.log(`Created directory: ${path.relative(rootDir, archiveDir)}`);
}

// Move the file to the archive directory
try {
  // Read the file content
  const fileContent = fs.readFileSync(resolvedFilePath);
  
  // Write the file to the archive directory
  fs.writeFileSync(archiveFilePath, fileContent);
  
  // Delete the original file
  fs.unlinkSync(resolvedFilePath);
  
  console.log(`Successfully archived file:`);
  console.log(`  - From: ${relativeFilePath}`);
  console.log(`  - To:   archive/${relativeFilePath}`);
  
  // Add an entry to FILE_CLEANUP_CHECKLIST.md
  const cleanupFilePath = path.join(rootDir, 'docs', 'FILE_CLEANUP_CHECKLIST.md');
  if (fs.existsSync(cleanupFilePath)) {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const entry = `\n## ${date} - Archived ${relativeFilePath}\n\n- **File**: \`${relativeFilePath}\`\n- **Reason**: Identified as orphaned by dependency analysis\n- **Action**: Moved to \`archive/${relativeFilePath}\`\n`;
    
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