#!/usr/bin/env node

/**
 * update-orphaned-files-report.cjs
 * 
 * This script updates the orphaned files report by removing files
 * that are actually used during the build process.
 */

const fs = require('fs');
const path = require('path');

// Parse --output-dir argument
let outputDir = null;
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--output-dir' && args[i + 1]) {
    outputDir = path.resolve(args[i + 1]);
    i++;
  } else if (args[i].startsWith('--output-dir=')) {
    outputDir = path.resolve(args[i].split('=')[1]);
  }
}
if (!outputDir) outputDir = path.resolve(__dirname, '..', 'output');

// Configuration
const config = {
  orphanedFilesReport: path.join(outputDir, 'orphaned-files.md'),
  buildDependenciesReport: path.join(outputDir, 'build-dependencies.md'),
  updatedReportFile: path.join(outputDir, 'confirmed-orphaned-files.md')
};

// Main function to run the update
async function main() {
  console.error('Updating orphaned files report...');
  
  // Read the original orphaned files report
  console.error(`Reading orphaned files report from ${config.orphanedFilesReport}...`);
  if (!fs.existsSync(config.orphanedFilesReport)) {
    console.error(`Error: Orphaned files report not found at ${config.orphanedFilesReport}`);
    process.exit(1);
  }
  const orphanedFilesReport = fs.readFileSync(config.orphanedFilesReport, 'utf-8');
  
  // Read the build dependencies report
  console.error(`Reading build dependencies report from ${config.buildDependenciesReport}...`);
  if (!fs.existsSync(config.buildDependenciesReport)) {
    console.warn(`Warning: Build dependencies report not found at ${config.buildDependenciesReport}`);
    console.warn('Proceeding without build analysis. All orphaned files will be considered as confirmed.');
    // Just copy the orphaned files report to the confirmed report
    fs.writeFileSync(config.updatedReportFile, orphanedFilesReport);
    console.error(`Confirmed orphaned files report written to ${config.updatedReportFile} (no build analysis performed)`);
    process.exit(0);
  }
  const buildDependenciesReport = fs.readFileSync(config.buildDependenciesReport, 'utf-8');
  
  // Extract the list of files used during build
  const usedFiles = [];
  const usedFilesSectionMatch = buildDependenciesReport.match(/## Files Used During Build\s+([\s\S]+?)(?=##)/);
  
  if (usedFilesSectionMatch) {
    const usedFilesSection = usedFilesSectionMatch[1];
    const fileRegex = /^- ([^\n]+?)(?:\n|$)/gm;
    let match;
    
    while ((match = fileRegex.exec(usedFilesSection)) !== null) {
      const fileLine = match[1].trim();
      const fileNameMatch = fileLine.match(/^([^\s]+)/);
      if (fileNameMatch) {
        usedFiles.push(fileNameMatch[1]);
      }
    }
  }
  
  console.error(`Found ${usedFiles.length} files used during build: ${usedFiles.join(', ')}`);
  
  // Split the orphaned files report into sections
  const headerMatch = orphanedFilesReport.match(/([\s\S]+?)(?=## Files that may be orphaned)/);
  const filesListMatch = orphanedFilesReport.match(/## Files that may be orphaned\s+([\s\S]+?)(?=## Note)/);
  const footerMatch = orphanedFilesReport.match(/(## Note[\s\S]+)$/);
  
  if (!headerMatch || !filesListMatch || !footerMatch) {
    console.error('Error: Could not parse the orphaned files report.');
    process.exit(1);
  }
  
  const header = headerMatch[1];
  const filesList = filesListMatch[1];
  const footer = footerMatch[1];
  
  // Process the files list to remove files used during build
  const fileEntries = filesList.split('\n\n- ').map((entry, index) => 
    index === 0 ? entry.trim() : `- ${entry.trim()}`
  );
  
  const updatedFilesList = [];
  let removedFiles = 0;
  
  for (const entry of fileEntries) {
    const fileMatch = entry.match(/^- ([^\s\n]+)/);
    if (!fileMatch) continue;
    
    const fileName = fileMatch[1];
    
    if (usedFiles.includes(fileName)) {
      removedFiles++;
      console.error(`Removing file from report: ${fileName}`);
      continue;
    }
    
    updatedFilesList.push(entry);
  }
  
  // Update the total count in the header
  const updatedFileCount = fileEntries.length - removedFiles;
  const updatedHeader = header.replace(/Potentially orphaned files: \d+/, `Potentially orphaned files: ${updatedFileCount}`);
  
  // Generate the updated report
  const updatedReport = `${updatedHeader}## Files that may be orphaned\n\n${updatedFilesList.join('\n\n')}\n\n${footer}`;
  
  // Write the updated report
  console.error(`Writing updated report to ${config.updatedReportFile}...`);
  fs.writeFileSync(config.updatedReportFile, updatedReport);
  
  console.error(`Update complete! Removed ${removedFiles} files from the orphaned files report.`);
}

// Run the script
main().catch(error => {
  console.error('Error updating orphaned files report:', error);
  process.exit(1);
}); 