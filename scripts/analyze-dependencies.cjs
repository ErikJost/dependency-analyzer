#!/usr/bin/env node

/**
 * analyze-dependencies.js
 * 
 * This script analyzes the project's dependency graph and identifies potentially orphaned files
 * by examining import statements across the codebase.
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

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
  rootDir: path.resolve(__dirname, '..'),
  // Extensions to analyze
  extensions: ['.ts', '.tsx', '.js', '.jsx', '.json', '.css', '.scss'],
  // Directories to exclude from analysis
  excludeDirs: [
    'node_modules',
    'dist',
    'build',
    '.git',
    'archive',
    'coverage',
    '.cursor'
  ],
  // Files that should never be reported as orphaned (entry points, configuration files, etc.)
  nonOrphanableFiles: [
    'package.json',
    'tsconfig.json',
    'vite.config.ts',
    'index.html',
    'main.ts',
    'main.tsx',
    'index.ts',
    'index.tsx',
    'App.tsx',
    'global.d.ts',
    'vite-env.d.ts',
    'README.md',
    '.gitignore',
    '.env',
    'staticwebapp.config.json'
  ],
  outputDir: outputDir
};

// Map to store dependency data
const dependencyMap = new Map();
// Set to store all files in the project
const allFiles = new Set();
// Set to store all imported files
const importedFiles = new Set();

/**
 * Check if a path should be excluded from analysis
 */
function shouldExcludePath(filePath) {
  return config.excludeDirs.some(dir => 
    filePath.includes(`/${dir}/`) || filePath.includes(`\\${dir}\\`)
  );
}

/**
 * Get all project files that match our criteria
 */
function getAllFiles() {
  console.error('Collecting all project files...');
  
  const pattern = `**/*+(${config.extensions.join('|')})`;
  const files = glob.sync(pattern, { 
    cwd: config.rootDir,
    ignore: config.excludeDirs.map(dir => `**/${dir}/**`),
    absolute: true,
    nodir: true
  });
  
  files.forEach(file => {
    const relativePath = path.relative(config.rootDir, file);
    allFiles.add(relativePath);
    dependencyMap.set(relativePath, {
      imports: new Set(),
      importedBy: new Set()
    });
  });
  
  console.error(`Found ${allFiles.size} files to analyze`);
  return files;
}

/**
 * Extract imports from a file
 */
function extractImports(filePath, fileContent) {
  const relativePath = path.relative(config.rootDir, filePath);
  const imports = new Set();
  
  // Match different types of imports
  const importPatterns = [
    // ES6 imports
    /import\s+(?:[\w*{}\n\r\t, ]+from\s+)?['"](\.\/[^'"]+|\.\.\/[^'"]+)['"];?/g,
    // Require statements
    /(?:const|let|var)\s+.*?require\(['"](.\/[^'"]+|\.\.\/[^'"]+)['"]\)/g,
    // Dynamic imports
    /import\(['"](.\/[^'"]+|\.\.\/[^'"]+)['"]\)/g,
    // CSS/SCSS imports
    /@import\s+['"](.\/[^'"]+|\.\.\/[^'"]+)['"];?/g
  ];
  
  for (const pattern of importPatterns) {
    let match;
    while ((match = pattern.exec(fileContent)) !== null) {
      let importPath = match[1];
      
      // Resolve the import path relative to the current file
      const resolvedPath = resolveImportPath(importPath, filePath);
      if (resolvedPath) {
        imports.add(resolvedPath);
        importedFiles.add(resolvedPath);
        
        // Update the dependency map
        if (dependencyMap.has(relativePath)) {
          dependencyMap.get(relativePath).imports.add(resolvedPath);
        }
        
        if (dependencyMap.has(resolvedPath)) {
          dependencyMap.get(resolvedPath).importedBy.add(relativePath);
        }
      }
    }
  }
  
  return imports;
}

/**
 * Resolve an import path to a file path
 */
function resolveImportPath(importPath, currentFilePath) {
  try {
    const dir = path.dirname(currentFilePath);
    let resolved = path.resolve(dir, importPath);
    
    // Check if the path exists directly
    if (fs.existsSync(resolved)) {
      return path.relative(config.rootDir, resolved);
    }
    
    // Try adding extensions
    for (const ext of config.extensions) {
      if (fs.existsSync(resolved + ext)) {
        return path.relative(config.rootDir, resolved + ext);
      }
    }
    
    // Try resolving as a directory (index file)
    for (const ext of config.extensions) {
      const indexPath = path.join(resolved, `index${ext}`);
      if (fs.existsSync(indexPath)) {
        return path.relative(config.rootDir, indexPath);
      }
    }
    
    // If still not found, it might be a node module or an alias
    return null;
  } catch (error) {
    console.error(`Error resolving import: ${importPath} from ${currentFilePath}`, error);
    return null;
  }
}

/**
 * Analyze a single file for dependencies
 */
function analyzeFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const imports = extractImports(filePath, content);
    return imports;
  } catch (error) {
    console.error(`Error analyzing file: ${filePath}`, error);
    return new Set();
  }
}

/**
 * Find potentially orphaned files
 */
function findOrphanedFiles() {
  console.error('Identifying potentially orphaned files...');
  
  const orphanedFiles = [];
  
  for (const file of allFiles) {
    // Skip non-orphanable files
    if (config.nonOrphanableFiles.some(nonOrphanable => 
      file.endsWith(nonOrphanable) || path.basename(file) === nonOrphanable
    )) {
      continue;
    }
    
    // Check if this file is imported by any other file
    if (dependencyMap.has(file) && dependencyMap.get(file).importedBy.size === 0) {
      orphanedFiles.push({
        file,
        imports: Array.from(dependencyMap.get(file).imports)
      });
    }
  }
  
  return orphanedFiles;
}

/**
 * Generate HTML report of dependency graph and orphaned files
 */
function generateReport(orphanedFiles) {
  console.error('Generating dependency analysis report...');
  
  // Ensure output directory exists
  if (!fs.existsSync(config.outputDir)) {
    fs.mkdirSync(config.outputDir, { recursive: true });
  }
  
  // Generate orphaned files report
  const orphanedReport = `# Potentially Orphaned Files
  
## Overview
This report identifies files in the codebase that are not imported by any other files and may be orphaned.

Total files analyzed: ${allFiles.size}
Potentially orphaned files: ${orphanedFiles.length}

## Files that may be orphaned

${orphanedFiles.map(item => `- ${item.file}${
  item.imports.length ? 
    `\n  - Imports: ${item.imports.join(', ')}` : 
    ''
}`).join('\n\n')}

## Note
Some files may be legitimately unused directly (e.g., types, utilities called via dynamic imports, 
files referenced via webpack/vite plugins, etc.). Further investigation may be required.

Generated on: ${new Date().toISOString()}
`;

  fs.writeFileSync(path.join(config.outputDir, 'orphaned-files.md'), orphanedReport);
  console.error(`[DEBUG] Wrote output file: ${path.join(config.outputDir, 'orphaned-files.md')}`);
  
  // Generate a simple dependency list
  const dependencyReport = `# Dependency Analysis Report

## File Dependencies
${Array.from(dependencyMap.entries()).map(([file, deps]) => `
### ${file}
Imports:
${Array.from(deps.imports).map(i => `- ${i}`).join('\n') || '- None'}

Imported by:
${Array.from(deps.importedBy).map(i => `- ${i}`).join('\n') || '- None'}
`).join('\n')}

Generated on: ${new Date().toISOString()}
`;

  fs.writeFileSync(path.join(config.outputDir, 'dependency-analysis.md'), dependencyReport);
  console.error(`[DEBUG] Wrote output file: ${path.join(config.outputDir, 'dependency-analysis.md')}`);
  
  console.error(`Reports generated in ${config.outputDir}`);
}

/**
 * Main function to run the analysis
 */
async function main() {
  console.error('Starting dependency analysis...');
  
  // Get all files
  const files = getAllFiles();
  
  // Analyze each file
  console.error('Analyzing file dependencies...');
  let count = 0;
  for (const file of files) {
    if (!shouldExcludePath(file)) {
      analyzeFile(file);
      count++;
      if (count % 100 === 0) {
        console.error(`Analyzed ${count} files...`);
      }
    }
  }
  
  // Find orphaned files
  const orphanedFiles = findOrphanedFiles();
  console.error(`Found ${orphanedFiles.length} potentially orphaned files`);
  
  // Generate report
  generateReport(orphanedFiles);
  
  console.error('Dependency analysis complete!');
}

// Run the script
main().catch(error => {
  console.error('Error running dependency analysis:', error);
  process.exit(1);
}); 