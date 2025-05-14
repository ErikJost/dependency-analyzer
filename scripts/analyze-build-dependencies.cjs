#!/usr/bin/env node

/**
 * analyze-build-dependencies.cjs
 * 
 * This script analyzes the build log to identify which potentially orphaned files
 * are actually used during the build process.
 */

const fs = require('fs');
const path = require('path');

// Parse --output-dir argument
let outputDir = null;
for (const arg of process.argv.slice(2)) {
  if (arg.startsWith('--output-dir=')) {
    outputDir = path.resolve(arg.split('=')[1]);
  }
}
if (!outputDir) outputDir = path.resolve(__dirname, '..', 'output');

// Configuration
const config = {
  buildLogFile: path.resolve(__dirname, '..', 'build_log.txt'),
  orphanedFilesReport: path.join(outputDir, 'orphaned-files.md'),
  outputFile: path.join(outputDir, 'build-dependencies.md')
};

// Main function to run the analysis
async function main() {
  console.error('Starting build dependency analysis...');
  
  // Read the build log
  console.error(`Reading build log from ${config.buildLogFile}...`);
  if (!fs.existsSync(config.buildLogFile)) {
    console.error(`Error: Build log file not found at ${config.buildLogFile}`);
    process.exit(1);
  }
  const buildLog = fs.readFileSync(config.buildLogFile, 'utf-8');
  
  // Read the orphaned files report
  console.error(`Reading orphaned files report from ${config.orphanedFilesReport}...`);
  if (!fs.existsSync(config.orphanedFilesReport)) {
    console.error(`Error: Orphaned files report not found at ${config.orphanedFilesReport}`);
    process.exit(1);
  }
  const orphanedFilesReport = fs.readFileSync(config.orphanedFilesReport, 'utf-8');
  
  // Extract the list of potentially orphaned files
  const orphanedFiles = [];
  const fileRegex = /^- (.+?)(?:\s+|$)/gm;
  let match;
  while ((match = fileRegex.exec(orphanedFilesReport)) !== null) {
    orphanedFiles.push(match[1]);
  }
  
  console.error(`Found ${orphanedFiles.length} potentially orphaned files in the report.`);
  
  // Check which orphaned files are actually used during build
  const usedFiles = [];
  const notUsedFiles = [];
  
  for (const file of orphanedFiles) {
    // Skip configuration files that are likely used but not directly referenced
    if (
      file.endsWith('.json') || 
      file.endsWith('.js') && (
        file.includes('config') || 
        file.includes('vite') || 
        file.includes('eslint') || 
        file.includes('tailwind') || 
        file.includes('postcss')
      )
    ) {
      usedFiles.push({
        file,
        reason: 'Configuration file, likely used indirectly'
      });
      continue;
    }
    
    // Check if the file is mentioned in the build log
    if (buildLog.includes(file)) {
      usedFiles.push({
        file,
        reason: 'Mentioned in build log'
      });
    } else {
      // Check if it's a TypeScript type definition file
      if (file.endsWith('.d.ts')) {
        usedFiles.push({
          file,
          reason: 'TypeScript type definition, used for type checking'
        });
      } else {
        notUsedFiles.push(file);
      }
    }
  }
  
  console.error(`Found ${usedFiles.length} files used during build.`);
  console.error(`Found ${notUsedFiles.length} files not used during build.`);
  
  // Generate a report
  const report = `# Build Dependency Analysis

## Overview
This report identifies which potentially orphaned files are actually used during the build process.

Total orphaned files: ${orphanedFiles.length}
Files used during build: ${usedFiles.length}
Files not used during build: ${notUsedFiles.length}

## Files Used During Build

${usedFiles.map(item => `- ${item.file}\n  - Reason: ${item.reason}`).join('\n\n')}

## Files Not Used During Build

${notUsedFiles.map(file => `- ${file}`).join('\n\n')}

## Recommendation

The files listed in the "Files Not Used During Build" section are good candidates for archiving according to the project's never-delete-files rule. They aren't imported by other files and don't appear to be used during the build process.

Generated on: ${new Date().toISOString()}
`;

  // Write the report
  console.error(`Writing report to ${config.outputFile}...`);
  const outputDir = path.dirname(config.outputFile);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  fs.writeFileSync(config.outputFile, report);
  console.error(`[DEBUG] Wrote output file: ${config.outputFile}`);
  
  console.error('Build dependency analysis complete!');
}

// Run the script
main().catch(error => {
  console.error('Error running build dependency analysis:', error);
  process.exit(1);
}); 