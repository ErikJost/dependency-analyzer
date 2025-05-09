#!/usr/bin/env node

/**
 * batch-archive-orphaned.cjs
 * 
 * This script reads the list of confirmed orphaned files from the final analysis
 * and archives each one using the archive-orphaned-file.cjs script.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const config = {
  rootDir: path.resolve(__dirname, '..'),
  finalAnalysisFile: path.resolve(__dirname, '..', 'output', 'final-orphaned-files.md'),
  archiveScript: path.join(__dirname, 'archive-orphaned-file.cjs'),
  reportFile: path.resolve(__dirname, '..', 'output', 'FILE_CLEANUP_REPORT.md')
};

/**
 * Extract orphaned files from the final analysis
 */
function extractOrphanedFiles() {
  console.log(`Reading final analysis from ${config.finalAnalysisFile}...`);
  
  if (!fs.existsSync(config.finalAnalysisFile)) {
    console.error(`Error: Final analysis file not found at ${config.finalAnalysisFile}`);
    process.exit(1);
  }
  
  const content = fs.readFileSync(config.finalAnalysisFile, 'utf-8');
  
  // Extract confirmed orphaned files (all entries with "- " prefix in the relevant sections)
  const orphanedFiles = [];
  
  // Define the sections we want to extract files from
  const sections = [
    "### Scripts and Utilities",
    "### Duplicated Files (Old Structure)",
    "### Test Files"
  ];
  
  let currentSection = null;
  
  // Parse the document line by line
  const lines = content.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Check if we've reached one of our target sections
    if (sections.includes(line)) {
      currentSection = line;
      continue;
    }
    
    // If we're in a relevant section and this is a file entry
    if (currentSection && line.startsWith('- ')) {
      // Extract the file path, ignoring any wildcards or comments
      let filePath = line.substring(2).trim();
      
      // Handle entries with wildcards or comments
      if (filePath.includes(' ')) {
        filePath = filePath.split(' ')[0];
      }
      
      // Skip entries that are directory patterns like "src/auth/*"
      if (filePath.endsWith('*')) {
        // Get all actual files in this directory
        try {
          const dirPath = filePath.replace(/\/\*$/, '');
          if (fs.existsSync(path.join(config.rootDir, dirPath)) && 
              fs.statSync(path.join(config.rootDir, dirPath)).isDirectory()) {
            
            const dirFiles = fs.readdirSync(path.join(config.rootDir, dirPath))
              .filter(file => !fs.statSync(path.join(config.rootDir, dirPath, file)).isDirectory())
              .map(file => `${dirPath}/${file}`);
            
            orphanedFiles.push(...dirFiles);
          }
        } catch (error) {
          console.warn(`Warning: Error processing directory pattern ${filePath}:`, error.message);
        }
      } else {
        orphanedFiles.push(filePath);
      }
    }
    
    // If we've reached a new section heading, reset currentSection
    if (currentSection && line.startsWith('##') && !sections.includes(line)) {
      currentSection = null;
    }
  }
  
  console.log(`Found ${orphanedFiles.length} files to archive.`);
  return orphanedFiles;
}

/**
 * Archive a single file
 */
function archiveFile(filePath) {
  console.log(`Archiving file: ${filePath}`);
  
  try {
    // Check if file exists
    const fullPath = path.join(config.rootDir, filePath);
    if (!fs.existsSync(fullPath)) {
      console.warn(`Warning: File not found: ${filePath}`);
      return {
        success: false,
        filePath,
        error: 'File not found'
      };
    }
    
    // Run the archive script
    execSync(`node ${config.archiveScript} ${filePath}`, { 
      stdio: 'inherit', 
      cwd: config.rootDir 
    });
    
    return {
      success: true,
      filePath
    };
  } catch (error) {
    console.error(`Error archiving file ${filePath}:`, error.message);
    return {
      success: false,
      filePath,
      error: error.message
    };
  }
}

/**
 * Generate a report of the archival process
 */
function generateReport(results) {
  console.log('Generating report...');
  
  const successfulArchivals = results.filter(r => r.success);
  const failedArchivals = results.filter(r => !r.success);
  
  const report = `# Orphaned Files Archival Report

## Overview
This report documents the archival of orphaned files identified through dependency analysis.

- **Date:** ${new Date().toISOString().split('T')[0]}
- **Total files processed:** ${results.length}
- **Successfully archived:** ${successfulArchivals.length}
- **Failed to archive:** ${failedArchivals.length}

## Successfully Archived Files

${successfulArchivals.map(r => `- \`${r.filePath}\` → \`archived_orphan/${path.basename(r.filePath)}\``).join('\n')}

## Files That Failed to Archive

${failedArchivals.length === 0 ? 'No failures.' : failedArchivals.map(r => `- \`${r.filePath}\`: ${r.error}`).join('\n')}

## Next Steps

1. Review any failed archival attempts
2. Verify application functionality after archival
3. Continue refining the orphaned files list with further analysis

This archival process is part of the ongoing effort to improve codebase organization while adhering to the "never-delete-files" policy.
`;

  fs.writeFileSync(config.reportFile, report);
  console.log(`Report written to ${config.reportFile}`);
}

/**
 * Main function
 */
async function main() {
  try {
    // Extract orphaned files
    const orphanedFiles = extractOrphanedFiles();
    
    // Confirm with user
    console.log('\nThe following files will be archived:');
    orphanedFiles.forEach(file => console.log(`- ${file}`));
    console.log('\nProceeding with archival...\n');
    
    // Archive each file
    const results = [];
    for (const file of orphanedFiles) {
      results.push(archiveFile(file));
    }
    
    // Generate report
    generateReport(results);
    
    console.log('\nArchival process complete!');
    console.log(`${results.filter(r => r.success).length} files successfully archived.`);
    console.log(`${results.filter(r => !r.success).length} files failed to archive.`);
    
  } catch (error) {
    console.error('Error in batch archival script:', error);
    process.exit(1);
  }
}

// Run the script
main().catch(console.error); 