#!/usr/bin/env node

/**
 * check-dynamic-imports.cjs
 * 
 * This script analyzes the codebase for dynamic imports, lazy-loaded components,
 * and string literal references that might not be detected by static analysis.
 * 
 * It checks for:
 * 1. Dynamic imports (import(), require())
 * 2. React.lazy() references
 * 3. Route definitions with string component paths 
 * 4. Webpack/Vite dynamic requires
 * 5. Other patterns that might reference files indirectly
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Parse command line arguments
const args = process.argv.slice(2);
let customRootDir = null;
let outputDir = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--root-dir' && args[i + 1]) {
    customRootDir = args[i + 1];
    i++;
  } else if (args[i].startsWith('--root-dir=')) {
    customRootDir = args[i].split('=')[1];
  }
  if (args[i] === '--output-dir' && args[i + 1]) {
    outputDir = path.resolve(args[i + 1]);
    i++;
  } else if (args[i].startsWith('--output-dir=')) {
    outputDir = path.resolve(args[i].split('=')[1]);
  }
}
if (!customRootDir || !fs.existsSync(customRootDir)) {
  console.error('❌ You must specify --root-dir with an existing directory.');
  process.exit(1);
}
const rootDir = path.resolve(customRootDir);

// Configuration
const config = {
  rootDir: rootDir,
  extensions: ['.ts', '.tsx', '.js', '.jsx'],
  excludeDirs: [
    'node_modules',
    'dist',
    'build',
    '.git',
    'archive',
    'coverage',
    '.cursor'
  ],
  // The list of potentially orphaned files
  orphanedFilesReport: path.join(outputDir, 'confirmed-orphaned-files.md'),
  // Output file for the results
  outputFile: path.join(outputDir, 'dynamic-references.md')
};

// Patterns to search for
const patterns = {
  dynamicImport: /import\s*\(\s*(['"])(.*?)\1\s*\)/g,
  reactLazy: /(?:React\.lazy|lazy)\s*\(\s*\(\s*\)\s*=>\s*import\s*\(\s*(['"])(.*?)\1\s*\)/g,
  require: /require\s*\(\s*(['"])(.*?)\1\s*\)/g,
  routeComponent: /component\s*:\s*(['"])(.*?)\1/g,
  routeElement: /element\s*:\s*<\s*([A-Z][a-zA-Z0-9]*)/g,
  routePath: /path\s*:\s*(['"])(.*?)\1/g,
  lazyImport: /const\s+([A-Z][a-zA-Z0-9]*)\s*=\s*(?:React\.lazy|lazy)/g,
  stringLiteral: /(['"])((?:\.{1,2}\/)?[a-zA-Z0-9_\-\/]+)\1/g
};

/**
 * Extract orphaned file list from the report
 */
function extractOrphanedFiles() {
  console.error(`Reading orphaned files report from ${config.orphanedFilesReport}...`);
  if (!fs.existsSync(config.orphanedFilesReport)) {
    console.error(`Error: Orphaned files report not found at ${config.orphanedFilesReport}`);
    process.exit(1);
  }
  
  const report = fs.readFileSync(config.orphanedFilesReport, 'utf-8');
  const orphanedFiles = [];
  const fileRegex = /^- (.+?)(?:\s+|$)/gm;
  let match;
  
  while ((match = fileRegex.exec(report)) !== null) {
    orphanedFiles.push(match[1]);
  }
  
  console.error(`Found ${orphanedFiles.length} potentially orphaned files in the report.`);
  return orphanedFiles;
}

/**
 * Get all source files in the project
 */
function getAllSourceFiles() {
  console.error('Finding all source files...');
  
  const pattern = `**/*+(${config.extensions.join('|')})`;
  const files = glob.sync(pattern, { 
    cwd: config.rootDir,
    ignore: config.excludeDirs.map(dir => `**/${dir}/**`),
    absolute: true,
    nodir: true
  });
  
  console.error(`Found ${files.length} source files to analyze.`);
  return files;
}

/**
 * Check a file for dynamic references
 */
function checkFileForDynamicReferences(filePath, orphanedFiles) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const references = [];
    const relativePath = path.relative(config.rootDir, filePath);
    
    // Check for each pattern
    for (const [type, regex] of Object.entries(patterns)) {
      regex.lastIndex = 0; // Reset regex state
      let match;
      
      while ((match = regex.exec(content)) !== null) {
        // Get the captured reference (usually in group 2, but can be in group 1 for some patterns)
        const reference = match[2] || match[1];
        
        if (reference) {
          // Check if this reference might be to an orphaned file
          const possibleMatches = orphanedFiles.filter(file => {
            // Convert paths to a comparable format
            const normalizedReference = reference.replace(/\\/g, '/');
            const normalizedFile = file.replace(/\\/g, '/');
            
            // Extract filename for component name comparison
            const refFileName = path.basename(normalizedReference, path.extname(normalizedReference));
            const fileBaseName = path.basename(normalizedFile, path.extname(normalizedFile));
            
            return (
              // Direct path match
              normalizedReference.includes(normalizedFile) ||
              // Filename match (for component references)
              (type === 'routeElement' && refFileName === fileBaseName) ||
              // Check if reference is a partial path to the file
              normalizedFile.endsWith(normalizedReference)
            );
          });
          
          if (possibleMatches.length > 0) {
            references.push({
              type,
              reference,
              matches: possibleMatches,
              context: match[0],
              location: `${relativePath}:${getLineNumber(content, match.index)}`
            });
          }
        }
      }
    }
    
    return references;
  } catch (error) {
    console.error(`Error checking file ${filePath}:`, error);
    return [];
  }
}

/**
 * Get the line number for a given index in text
 */
function getLineNumber(text, index) {
  return text.substring(0, index).split('\n').length;
}

/**
 * Main function
 */
async function main() {
  try {
    const orphanedFiles = extractOrphanedFiles();
    const sourceFiles = getAllSourceFiles();
    
    console.error('Analyzing files for dynamic references...');
    
    // Map to store references by orphaned file
    const referencesByFile = {};
    // Initialize map for each orphaned file
    orphanedFiles.forEach(file => {
      referencesByFile[file] = [];
    });
    
    // Check each source file
    let totalReferences = 0;
    for (const sourceFile of sourceFiles) {
      const references = checkFileForDynamicReferences(sourceFile, orphanedFiles);
      
      if (references.length > 0) {
        references.forEach(ref => {
          ref.matches.forEach(match => {
            referencesByFile[match].push(ref);
            totalReferences++;
          });
        });
      }
    }
    
    console.error(`Found ${totalReferences} potential dynamic references to orphaned files.`);
    
    // Generate a report
    const filesWithReferences = Object.keys(referencesByFile)
      .filter(file => referencesByFile[file].length > 0);
    
    const report = `# Dynamic References to Potentially Orphaned Files

## Overview
This report shows potential dynamic references to files previously identified as orphaned.
These files might be used through dynamic imports, lazy loading, or string literals.

Found ${filesWithReferences.length} orphaned files with potential dynamic references.

## Files with Dynamic References

${filesWithReferences.map(file => `
### ${file}

${referencesByFile[file].map(ref => `
- **Type**: ${ref.type}
- **Referenced as**: \`${ref.reference}\`
- **Location**: ${ref.location}
- **Context**: \`${ref.context}\`
`).join('\n')}
`).join('\n')}

## Files Still Likely Orphaned

The following files have no detected dynamic references:

${orphanedFiles
  .filter(file => !filesWithReferences.includes(file))
  .map(file => `- ${file}`)
  .join('\n')}

## Note

This analysis looks for common patterns for dynamic references, but may not catch all cases.
Manual verification is still recommended for critical files.

Generated on: ${new Date().toISOString()}
`;

    // Write the report
    console.error(`Writing report to ${config.outputFile}`);
    const outputDir = path.dirname(config.outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    fs.writeFileSync(config.outputFile, report);
    
    console.error('Dynamic reference analysis complete!');
  } catch (error) {
    console.error('Error during analysis:', error);
    process.exit(1);
  }
}

// Run the script
main().catch(console.error); 