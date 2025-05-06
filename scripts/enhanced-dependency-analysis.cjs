#!/usr/bin/env node

/**
 * enhanced-dependency-analysis.cjs
 * 
 * This script provides a more thorough dependency analysis that:
 * 1. Properly handles barrel files (index.ts/js)
 * 2. Tracks re-exports and indirect dependencies
 * 3. Handles route-based component references
 * 4. Searches through all folders including client/src
 * 
 * Usage:
 *   node enhanced-dependency-analysis.cjs [--root-dir=<path>]
 */

// Setup graceful termination handler
process.on('SIGTERM', () => {
  console.log('Received SIGTERM signal. Stopping dependency analysis gracefully...');
  cleanup();
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('Received SIGINT signal. Stopping dependency analysis gracefully...');
  cleanup();
  process.exit(0);
});

/**
 * Cleanup function to be called before exiting
 */
function cleanup() {
  console.log('Cleaning up temporary files and releasing resources...');
  // Any cleanup operations can go here
}

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Parse command line arguments
const args = process.argv.slice(2);
let customRootDir = null;

// Look for --root-dir argument
for (const arg of args) {
  if (arg.startsWith('--root-dir=')) {
    customRootDir = arg.split('=')[1];
    break;
  }
}

// Detect repository root (look for .git, package.json, etc.)
function detectProjectRoot(startDir) {
  // Start from the current directory and go up
  let currentDir = startDir || process.cwd();
  
  // Define root markers (files/folders that indicate a project root)
  const rootMarkers = ['.git', 'package.json', 'package-lock.json', 'yarn.lock', '.gitignore'];
  
  // Maximum levels to go up
  const maxLevels = 5;
  let levelsUp = 0;
  
  while (levelsUp < maxLevels) {
    // Check if any root markers exist in this directory
    for (const marker of rootMarkers) {
      if (fs.existsSync(path.join(currentDir, marker))) {
        console.log(`Detected project root at: ${currentDir} (found marker: ${marker})`);
        return currentDir;
      }
    }
    
    // Go up one level
    const parentDir = path.dirname(currentDir);
    if (parentDir === currentDir) {
      // We've reached the filesystem root
      break;
    }
    
    currentDir = parentDir;
    levelsUp++;
  }
  
  // If we couldn't detect a root, default to script's parent directory
  console.log(`Could not detect project root, using default: ${path.resolve(__dirname, '..')}`);
  return path.resolve(__dirname, '..');
}

// Configuration
const config = {
  rootDir: customRootDir ? path.resolve(customRootDir) : detectProjectRoot(path.resolve(__dirname, '..')),
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
  // Add any routes-related patterns to consider special cases for component usage
  routePatterns: [
    'element={<([^>]+)',      // React Router element props
    'component={([^}]+)}',    // component props
    'render={[^}]*=>\\s*<([^>]+)' // render props with component
  ],
  // Default output location is in the project root under output
  get outputDir() {
    const dir = path.resolve(this.rootDir, 'output');
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    return dir;
  }
};

console.log(`Using project root: ${config.rootDir}`);
console.log(`Output directory: ${config.outputDir}`);

// Map to store dependency data
const dependencyMap = new Map();
// Map to store barrel file exports (index.ts/js files that re-export)
const barrelExports = new Map();
// Set to store all files in the project
const allFiles = new Set();
// Set to store all imported files (directly or indirectly)
const importedFiles = new Set();
// Map to track route component references
const routeComponentRefs = new Map();

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
  console.log('Collecting all project files...');
  
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
      importedBy: new Set(),
      reExports: new Set(), // Track what this file re-exports
      reExportedBy: new Set() // Track which files re-export this
    });
  });
  
  console.log(`Found ${allFiles.size} files to analyze`);
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
  
  // Check for barrel exports
  const isBarrelFile = path.basename(filePath).match(/^index\.(js|jsx|ts|tsx)$/);
  if (isBarrelFile) {
    analyzeBarrelFile(relativePath, fileContent);
  }
  
  // Check for route component references
  analyzeRouteComponents(relativePath, fileContent);
  
  return imports;
}

/**
 * Analyze a barrel file (index.ts/js) for re-exports
 */
function analyzeBarrelFile(relativePath, fileContent) {
  console.log(`Analyzing barrel file: ${relativePath}`);
  const exportPatterns = [
    // Named re-exports
    /export\s+{\s*([^}]+)\s*}\s+from\s+['"](\.\/[^'"]+|\.\.\/[^'"]+)['"]/g,
    // Default re-exports
    /export\s+{\s*default\s+as\s+([^}]+)\s*}\s+from\s+['"](\.\/[^'"]+|\.\.\/[^'"]+)['"]/g,
    // Direct re-exports
    /export\s+\*\s+from\s+['"](\.\/[^'"]+|\.\.\/[^'"]+)['"]/g
  ];
  
  barrelExports.set(relativePath, new Set());
  
  for (const pattern of exportPatterns) {
    let match;
    while ((match = pattern.exec(fileContent)) !== null) {
      const importPath = match[match.length - 1]; // Last group is always the path
      const dir = path.dirname(path.join(config.rootDir, relativePath));
      let resolvedPath;
      
      try {
        // Normalize and resolve the path
        resolvedPath = path.normalize(path.join(dir, importPath));
        
        // Try to find the actual file with extension
        for (const ext of ['.ts', '.tsx', '.js', '.jsx']) {
          if (fs.existsSync(resolvedPath + ext)) {
            resolvedPath = resolvedPath + ext;
            break;
          }
          
          // Check if it's a directory with an index file
          const indexPath = path.join(resolvedPath, `index${ext}`);
          if (fs.existsSync(indexPath)) {
            resolvedPath = indexPath;
            break;
          }
        }
        
        // Make the path relative to root
        resolvedPath = path.relative(config.rootDir, resolvedPath);
        
        // If we have an export clause with names, track each exported name
        if (match[1]) {
          const exportNames = match[1].split(',').map(name => name.trim());
          exportNames.forEach(name => {
            barrelExports.get(relativePath).add({
              name,
              source: resolvedPath
            });
            
            // Update the re-export relationships
            if (dependencyMap.has(relativePath) && dependencyMap.has(resolvedPath)) {
              dependencyMap.get(relativePath).reExports.add(resolvedPath);
              dependencyMap.get(resolvedPath).reExportedBy.add(relativePath);
            }
          });
        } else {
          // For * exports, we just track the source file
          barrelExports.get(relativePath).add({
            name: '*',
            source: resolvedPath
          });
          
          // Update the re-export relationships
          if (dependencyMap.has(relativePath) && dependencyMap.has(resolvedPath)) {
            dependencyMap.get(relativePath).reExports.add(resolvedPath);
            dependencyMap.get(resolvedPath).reExportedBy.add(relativePath);
          }
        }
      } catch (error) {
        console.error(`Error resolving re-export in ${relativePath}:`, error.message);
      }
    }
  }
}

/**
 * Analyze for React Router or similar component references in route definitions
 */
function analyzeRouteComponents(relativePath, fileContent) {
  for (const pattern of config.routePatterns) {
    const regex = new RegExp(pattern, 'g');
    let match;
    
    while ((match = regex.exec(fileContent)) !== null) {
      const componentRef = match[1].trim();
      
      // Skip self-closing tags or HTML elements
      if (componentRef.includes('/') || componentRef.match(/^[a-z]/)) {
        continue;
      }
      
      // Add to the route component references
      if (!routeComponentRefs.has(componentRef)) {
        routeComponentRefs.set(componentRef, new Set());
      }
      routeComponentRefs.get(componentRef).add(relativePath);
      
      console.log(`Found route component reference: ${componentRef} in ${relativePath}`);
    }
  }
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
 * Process barrel file dependencies to handle re-exports
 */
function processBarrelDependencies() {
  console.log('Processing barrel file dependencies...');
  
  // Iterate through files imported via barrels and make sure they're marked as imported
  let changes = true;
  let iterations = 0;
  const maxIterations = 10; // Prevent infinite loops
  
  while (changes && iterations < maxIterations) {
    changes = false;
    iterations++;
    
    barrelExports.forEach((exports, barrelFile) => {
      const barrelImporters = Array.from(dependencyMap.get(barrelFile)?.importedBy || []);
      
      exports.forEach(exportEntry => {
        const sourceFile = exportEntry.source;
        
        // Skip if source file isn't in our dependency map
        if (!dependencyMap.has(sourceFile)) return;
        
        // For each file that imports the barrel, mark it as importing the source file
        barrelImporters.forEach(importerFile => {
          if (!dependencyMap.has(importerFile)) return;
          
          const importer = dependencyMap.get(importerFile);
          const wasAdded = !importer.imports.has(sourceFile);
          
          if (wasAdded) {
            importer.imports.add(sourceFile);
            dependencyMap.get(sourceFile).importedBy.add(importerFile);
            importedFiles.add(sourceFile);
            changes = true;
            
            console.log(`Added indirect dependency: ${importerFile} -> ${sourceFile} via ${barrelFile}`);
          }
        });
      });
    });
    
    console.log(`Barrel processing iteration ${iterations} completed, changes made: ${changes}`);
  }
}

/**
 * Process route component references
 */
function processRouteReferences() {
  console.log('Processing route component references...');
  
  // Find component files matching the route references
  routeComponentRefs.forEach((referencingFiles, componentName) => {
    // Try to find files that might match this component
    const potentialMatches = Array.from(allFiles).filter(file => {
      const fileName = path.basename(file, path.extname(file));
      return fileName === componentName;
    });
    
    if (potentialMatches.length > 0) {
      console.log(`Found ${potentialMatches.length} potential matches for route component: ${componentName}`);
      
      potentialMatches.forEach(componentFile => {
        referencingFiles.forEach(referencingFile => {
          // Ensure the dependency map has both files
          if (!dependencyMap.has(referencingFile) || !dependencyMap.has(componentFile)) return;
          
          // Add the relationship
          dependencyMap.get(referencingFile).imports.add(componentFile);
          dependencyMap.get(componentFile).importedBy.add(referencingFile);
          importedFiles.add(componentFile);
          
          console.log(`Added route reference dependency: ${referencingFile} -> ${componentFile}`);
        });
      });
    } else {
      console.log(`No matches found for route component: ${componentName}`);
    }
  });
}

/**
 * Find potentially orphaned files
 */
function findOrphanedFiles() {
  console.log('Identifying potentially orphaned files...');
  
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
      // Check if it's re-exported by a barrel
      if (dependencyMap.get(file).reExportedBy.size === 0) {
        orphanedFiles.push({
          file,
          imports: Array.from(dependencyMap.get(file).imports),
          reExports: Array.from(dependencyMap.get(file).reExports)
        });
      }
    }
  }
  
  return orphanedFiles;
}

/**
 * Find potentially duplicated files
 */
function findDuplicateFiles() {
  console.log('Identifying potentially duplicated files...');
  
  const filesByBasename = new Map();
  const duplicateGroups = [];
  
  // Group files by their basename (ignoring directories)
  for (const file of allFiles) {
    const basename = path.basename(file);
    
    if (!filesByBasename.has(basename)) {
      filesByBasename.set(basename, []);
    }
    
    filesByBasename.get(basename).push(file);
  }
  
  console.log(`Found ${filesByBasename.size} unique file basenames`);
  
  // Find basenames with multiple occurrences
  const potentialDuplicates = Array.from(filesByBasename.entries())
    .filter(([_, files]) => files.length > 1);
  
  console.log(`Found ${potentialDuplicates.length} basenames with multiple occurrences`);
  
  // Process each potential duplicate group
  for (const [basename, files] of potentialDuplicates) {
    console.log(`Analyzing potential duplicates for ${basename} (${files.length} files)`);
    
    // Verify content similarity to confirm they are true duplicates
    const fileContents = new Map();
    const fileHashes = new Map();
    let hashComparisonSuccessful = true;
    
    try {
      // Read the content of each file
      for (const file of files) {
        const fullPath = path.join(config.rootDir, file);
        
        if (fs.existsSync(fullPath)) {
          try {
            const content = fs.readFileSync(fullPath, 'utf-8');
            fileContents.set(file, content);
            
            // Calculate a strong hash of the content
            const hash = require('crypto')
              .createHash('md5')
              .update(content)
              .digest('hex');
            
            fileHashes.set(file, hash);
            console.log(`  - ${file}: Hash ${hash.substring(0, 8)}...`);
          } catch (readError) {
            console.error(`  - Error reading ${file}: ${readError.message}`);
            hashComparisonSuccessful = false;
          }
        } else {
          console.error(`  - File not found: ${fullPath}`);
          hashComparisonSuccessful = false;
        }
      }
      
      if (!hashComparisonSuccessful) {
        console.log(`  Skipping ${basename} due to read errors`);
        continue;
      }
      
      // Group files by their content hash
      const filesByHash = new Map();
      
      for (const [file, hash] of fileHashes.entries()) {
        if (!filesByHash.has(hash)) {
          filesByHash.set(hash, []);
        }
        filesByHash.get(hash).push(file);
      }
      
      // Check if we found any duplicates (files with the same hash)
      let duplicatesFound = false;
      
      for (const [hash, hashFiles] of filesByHash.entries()) {
        if (hashFiles.length > 1) {
          duplicatesFound = true;
          
          console.log(`  Found duplicate group: ${hashFiles.join(', ')}`);
          
          duplicateGroups.push({
            basename,
            files: hashFiles,
            hash
          });
        }
      }
      
      if (!duplicatesFound) {
        console.log(`  No duplicate content found for ${basename}`);
      }
    } catch (error) {
      console.error(`Error analyzing duplicate files for ${basename}:`, error);
    }
  }
  
  console.log(`Found ${duplicateGroups.length} groups of duplicate files`);
  
  // Print summary of duplicates found
  if (duplicateGroups.length > 0) {
    console.log('Duplicate file groups:');
    duplicateGroups.forEach((group, index) => {
      console.log(`Group ${index + 1}: ${group.basename} (${group.files.length} files)`);
      group.files.forEach(file => console.log(`  - ${file}`));
    });
  }
  
  return duplicateGroups;
}

/**
 * Generate detailed reports of dependency graph and orphaned files
 */
function generateReports(orphanedFiles) {
  console.log('Generating dependency analysis reports...');
  
  // Ensure output directory exists
  if (!fs.existsSync(config.outputDir)) {
    fs.mkdirSync(config.outputDir, { recursive: true });
  }
  
  // Find duplicate files first
  const duplicateGroups = findDuplicateFiles();
  
  // Generate orphaned files report
  const orphanedReport = `# Potentially Orphaned Files
  
## Overview
This report identifies files in the codebase that are not imported by any other files and may be orphaned.
This enhanced analysis includes barrel file (index.ts) re-exports and route component references.

Total files analyzed: ${allFiles.size}
Potentially orphaned files: ${orphanedFiles.length}

## Files that may be orphaned

${orphanedFiles.map(item => {
  const imports = item.imports.length 
    ? `\n  - Imports: ${item.imports.join(', ')}` 
    : '';
  const reExports = item.reExports.length 
    ? `\n  - Re-exports: ${item.reExports.join(', ')}` 
    : '';
  return `- ${item.file}${imports}${reExports}`;
}).join('\n\n')}

## Note
Some files may be legitimately unused directly (e.g., types, utilities called via dynamic imports, 
files referenced via webpack/vite plugins, etc.). Further investigation may be required.

## Barrel Files Analysis
The following barrel files (index.ts/js) were analyzed for re-exports:

${Array.from(barrelExports.entries()).map(([barrelFile, exports]) => `
### ${barrelFile}
${Array.from(exports).map(exp => `- Exports ${exp.name} from ${exp.source}`).join('\n')}
`).join('\n')}

## Route Component References
The following component references were found in route definitions:

${Array.from(routeComponentRefs.entries()).map(([component, references]) => `
### ${component}
Referenced in: ${Array.from(references).join(', ')}
`).join('\n')}

Generated on: ${new Date().toISOString()}
`;

  fs.writeFileSync(path.join(config.outputDir, 'enhanced-orphaned-files.md'), orphanedReport);
  
  // Generate a dependency graph for visualization
  const dependencyGraph = {
    nodes: [],
    links: []
  };
  
  // Add nodes for all files
  Array.from(allFiles).forEach(file => {
    dependencyGraph.nodes.push({
      id: file,
      group: file.startsWith('client/src') ? 1 : file.startsWith('src') ? 2 : 3
    });
  });
  
  // Add links for imports
  Array.from(dependencyMap.entries()).forEach(([file, deps]) => {
    deps.imports.forEach(importedFile => {
      dependencyGraph.links.push({
        source: file,
        target: importedFile,
        value: 1
      });
    });
    
    // Add links for re-exports
    deps.reExports.forEach(reExportedFile => {
      dependencyGraph.links.push({
        source: file,
        target: reExportedFile,
        value: 2  // Different value to distinguish re-exports
      });
    });
  });
  
  // Add duplicate file connections to the graph
  console.log(`Adding ${duplicateGroups.length} duplicate groups to the graph...`);
  duplicateGroups.forEach(group => {
    // Create "duplicate" links between files in the same group
    for (let i = 0; i < group.files.length; i++) {
      for (let j = i + 1; j < group.files.length; j++) {
        console.log(`Adding duplicate link: ${group.files[i]} <-> ${group.files[j]}`);
        dependencyGraph.links.push({
          source: group.files[i],
          target: group.files[j],
          value: 3  // Special value for duplicate links
        });
      }
    }
  });
  
  fs.writeFileSync(
    path.join(config.outputDir, 'dependency-graph.json'), 
    JSON.stringify(dependencyGraph, null, 2)
  );
  
  // Generate a simple HTML visualizer for the dependency graph
  const visualizerHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dependency Graph Visualization</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    html, body { 
      margin: 0; 
      padding: 0; 
      width: 100%; 
      height: 100%; 
      font-family: Arial, sans-serif; 
      overflow: hidden; 
    }
    
    svg {
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
    }
    
    .links line { stroke: #999; stroke-opacity: 0.6; }
    .links line.duplicate { stroke: #9932cc; stroke-width: 2px; stroke-opacity: 0.8; }
    .nodes circle { stroke: #fff; stroke-width: 1.5px; }
    .node-label { font-size: 10px; }
    
    /* Missing node styling */
    .missing-node line {
      stroke: #d62728;
      stroke-width: 2px;
    }
    
    .missing-link {
      stroke: #d62728;
      stroke-dasharray: 5,5;
      stroke-width: 1.5px;
    }
    
    /* Panel styling */
    .widget {
      position: absolute;
      background: rgba(255,255,255,0.95);
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      max-height: 80vh;
      overflow-y: auto;
      transition: all 0.3s ease;
    }
    
    .widget-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      padding-bottom: 5px;
      border-bottom: 1px solid #ddd;
      cursor: move;
    }
    
    .widget-title {
      font-weight: bold;
      margin: 0;
    }
    
    .widget-controls {
      display: flex;
    }
    
    .widget-control {
      cursor: pointer;
      margin-left: 8px;
      user-select: none;
    }
    
    .widget-content {
      overflow: hidden;
      transition: max-height 0.3s ease;
    }
    
    .legend { 
      top: 10px; 
      left: 10px; 
      z-index: 100;
    }
    
    .tools {
      top: 10px;
      right: 10px;
      z-index: 100;
    }
    
    .minimized .widget-content {
      max-height: 0;
      padding: 0;
      overflow: hidden;
    }
    
    .duplicate-group { stroke: #9932cc; stroke-width: 2px; }
    
    /* Error container */
    #error-container {
      display: none;
      position: fixed;
      bottom: 10px;
      left: 10px;
      background: rgba(255,70,70,0.9);
      color: white;
      padding: 10px;
      border-radius: 5px;
      max-width: 80%;
      z-index: 1000;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    
    /* Input styling */
    input, select, button {
      margin: 5px 0;
      padding: 6px 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 14px;
    }
    
    button {
      background: #4a90e2;
      color: white;
      border: none;
      cursor: pointer;
      padding: 6px 12px;
    }
    
    button:hover {
      background: #3a70b2;
    }
    
    .filter-group {
      margin-bottom: 10px;
    }
    
    .filter-title {
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    .search-result {
      margin-top: 10px;
      padding: 8px;
      background: #f0f0f0;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <!-- Legend Widget -->
  <div class="widget legend" id="legend-widget">
    <div class="widget-header">
      <h3 class="widget-title">Legend</h3>
      <div class="widget-controls">
        <span class="widget-control minimize-btn" title="Minimize">−</span>
      </div>
    </div>
    <div class="widget-content">
      <div><span style="color: #1f77b4;">●</span> client/src</div>
      <div><span style="color: #ff7f0e;">●</span> src</div>
      <div><span style="color: #2ca02c;">●</span> other</div>
      <div><span style="color: #d62728;">✕</span> missing files</div>
      <div><span style="color: #999;">—</span> imports</div>
      <div><span style="color: #ff0000;">—</span> re-exports</div>
      <div><span style="color: #9932cc;">—</span> duplicates (${duplicateGroups.length} groups)</div>
      <div><span style="color: #d62728; stroke-dasharray: 5,5;">- -</span> missing dependency</div>
    </div>
  </div>
  
  <!-- Tools Widget -->
  <div class="widget tools" id="tools-widget">
    <div class="widget-header">
      <h3 class="widget-title">Tools</h3>
      <div class="widget-controls">
        <span class="widget-control minimize-btn" title="Minimize">−</span>
      </div>
    </div>
    <div class="widget-content">
      <div class="filter-group">
        <div class="filter-title">Filter by Folder</div>
        <select id="folder-filter">
          <option value="">All Folders</option>
          <option value="client/src">client/src</option>
          <option value="src">src</option>
          <option value="shared">shared</option>
          <option value="functions">functions</option>
          <option value="scripts">scripts</option>
        </select>
        <div>
          <label><input type="checkbox" id="show-missing" checked> Show missing nodes</label>
        </div>
        <div>
          <label><input type="checkbox" id="show-labels" checked> Show node labels</label>
        </div>
        <div>
          <label><input type="checkbox" id="show-duplicates" checked> Show duplicate connections</label>
        </div>
      </div>
      
      <div class="filter-group">
        <div class="filter-title">Search Nodes</div>
        <input type="text" id="search-input" placeholder="Enter file name...">
        <button id="search-btn">Search</button>
        <div id="search-results" class="search-result" style="display: none;"></div>
      </div>
      
      <div class="filter-group">
        <div class="filter-title">Debug</div>
        <button id="center-btn">Reset View</button>
        <button id="inspect-data-btn">Inspect Data</button>
      </div>
    </div>
  </div>
  
  <!-- Error message container -->
  <div id="error-container"></div>
  
  <svg></svg>
  
  <script>
    // Make widgets draggable
    function makeWidgetDraggable(widgetId) {
      const widget = document.getElementById(widgetId);
      const header = widget.querySelector('.widget-header');
      let isDragging = false;
      let offsetX, offsetY;
      
      header.addEventListener('mousedown', (e) => {
        isDragging = true;
        offsetX = e.clientX - widget.getBoundingClientRect().left;
        offsetY = e.clientY - widget.getBoundingClientRect().top;
        widget.style.cursor = 'grabbing';
      });
      
      document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const x = e.clientX - offsetX;
        const y = e.clientY - offsetY;
        
        // Keep widget within window bounds
        const maxX = window.innerWidth - widget.offsetWidth;
        const maxY = window.innerHeight - widget.offsetHeight;
        
        widget.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
        widget.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
      });
      
      document.addEventListener('mouseup', () => {
        isDragging = false;
        widget.style.cursor = 'default';
      });
    }
    
    // Add minimize/maximize functionality
    function setupMinimizeButtons() {
      document.querySelectorAll('.minimize-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const widget = btn.closest('.widget');
          widget.classList.toggle('minimized');
          
          // Update button text
          if (widget.classList.contains('minimized')) {
            btn.textContent = '+';
            btn.title = 'Maximize';
          } else {
            btn.textContent = '−';
            btn.title = 'Minimize';
          }
        });
      });
    }
    
    // Display error messages
    function showError(message) {
      console.error(message);
      const errorContainer = document.getElementById('error-container');
      if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        
        // Hide after 10 seconds
        setTimeout(() => {
          errorContainer.style.display = 'none';
        }, 10000);
      }
    }
    
    // Initialize widgets
    document.addEventListener('DOMContentLoaded', () => {
      makeWidgetDraggable('legend-widget');
      makeWidgetDraggable('tools-widget');
      setupMinimizeButtons();
    });
  
    fetch('dependency-graph.json')
      .then(response => response.json())
      .then(data => {
        const svg = d3.select("svg");
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // Store the original data
        const originalData = JSON.parse(JSON.stringify(data));
        let filteredData = JSON.parse(JSON.stringify(data));
        
        // Create a map of node IDs for quick lookup
        const nodeMap = new Map();
        data.nodes.forEach(node => {
          nodeMap.set(node.id, node);
        });
        console.log(\`Created node map with \${nodeMap.size} entries\`);
        
        // Find missing nodes in the links
        const missingNodes = new Set();
        const missingLinks = [];
        
        // Identify missing nodes referenced in links
        data.links.forEach(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
          
          if (!nodeMap.has(sourceId)) {
            missingNodes.add(sourceId);
            // Don't add the link, just track it
            missingLinks.push({source: sourceId, target: targetId, missing: 'source'});
          } else if (!nodeMap.has(targetId)) {
            missingNodes.add(targetId);
            // Don't add the link, just track it
            missingLinks.push({source: sourceId, target: targetId, missing: 'target'});
          }
        });
        
        // Add missing nodes to the visualization with a different style
        if (missingNodes.size > 0) {
          console.log(\`Found \${missingNodes.size} missing nodes, adding them to visualization\`);
          
          // Create new nodes for missing files
          missingNodes.forEach(missingId => {
            const parts = missingId.split('/');
            const group = missingId.startsWith('client/') ? 1 : 
                        missingId.startsWith('src/') ? 2 : 0;
            
            // Add the missing node to data
            data.nodes.push({
              id: missingId,
              group: group,
              missing: true
            });
            
            // Also add to the original data for filtering
            originalData.nodes.push({
              id: missingId,
              group: group,
              missing: true
            });
          });
          
          // Add filtered links back
          missingLinks.forEach(link => {
            data.links.push({
              source: link.source,
              target: link.target,
              value: 1,
              missing: true
            });
            
            // Also add to the original data for filtering
            originalData.links.push({
              source: link.source,
              target: link.target,
              value: 1,
              missing: true
            });
          });
          
          // Show error message about missing nodes
          showError(\`Found \${missingNodes.size} missing nodes referenced in the dependencies. These are shown with red X marks.\`);
        }
        
        // Setup visualization
        function createVisualization(data) {
          // Clear the SVG
          svg.selectAll("*").remove();
          svg.attr("width", width)
             .attr("height", height);
             
          // Create a container for all content
          const container = svg.append("g")
            .attr("class", "container");
          
          // Add a background for pan/zoom
          container.append("rect")
            .attr("width", width * 10)
            .attr("height", height * 10)
            .attr("x", -width * 5)
            .attr("y", -height * 5)
            .attr("fill", "none")
            .attr("pointer-events", "all");
  
          const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(d => {
              // Make duplicate links shorter to pull duplicate files closer together
              return d.value === 3 ? 30 : 100;
            }))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(width / 2, height / 2));
  
          const link = container.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("class", d => {
              if (d.value === 3) return "duplicate";
              if (d.missing) return "missing-link";
              return "";
            })
            .attr("stroke", d => {
              if (d.missing) return "#d62728"; // Red for missing links
              if (d.value === 3) return "#9932cc"; // Purple for duplicates
              if (d.value === 2) return "#ff0000"; // Red for re-exports
              return "#999"; // Gray for regular imports
            })
            .attr("stroke-width", d => Math.sqrt(d.value || 1))
            .attr("stroke-dasharray", d => d.missing ? "5,5" : null);
  
          // Set initial display of duplicates based on checkbox
          const showDuplicates = document.getElementById('show-duplicates').checked;
          link.filter(d => d.value === 3) // Filter for duplicate connections
              .style("display", showDuplicates ? "inline" : "none");

          const node = container.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(data.nodes)
            .enter().append("g");
  
          // Add circles or X marks based on whether node is missing
          node.each(function(d) {
            const el = d3.select(this);
            if (d.missing) {
              // Create an X for missing nodes
              const size = 5;
              el.append("line")
                .attr("x1", -size)
                .attr("y1", -size)
                .attr("x2", size)
                .attr("y2", size)
                .attr("stroke", "#d62728")
                .attr("stroke-width", 2);
              
              el.append("line")
                .attr("x1", -size)
                .attr("y1", size)
                .attr("x2", size)
                .attr("y2", -size)
                .attr("stroke", "#d62728")
                .attr("stroke-width", 2);
            } else {
              // Regular node circle
              el.append("circle")
                .attr("r", 5)
                .attr("fill", d => {
                  if (d.group === 1) return "#1f77b4";
                  if (d.group === 2) return "#ff7f0e";
                  return "#2ca02c";
                });
            }
          });
  
          node.append("title")
            .text(d => d.missing ? \`Missing: \${d.id}\` : d.id);
  
          // Add text labels to nodes
          const nodeLabels = node.append("text")
            .attr("class", "node-label")
            .attr("dx", 8)
            .attr("dy", ".35em")
            .text(d => {
              const parts = d.id.split('/');
              return parts[parts.length - 1];
            })
            .style("fill", d => d.missing ? "#d62728" : "black")
            .style("font-style", d => d.missing ? "italic" : "normal");
          
          // Set initial display of labels based on checkbox
          const showLabels = document.getElementById('show-labels').checked;
          nodeLabels.style("display", showLabels ? "inline" : "none");
  
          simulation.on("tick", () => {
            link
              .attr("x1", d => d.source.x)
              .attr("y1", d => d.source.y)
              .attr("x2", d => d.target.x)
              .attr("y2", d => d.target.y);
  
            node.attr("transform", d => \`translate(\${d.x},\${d.y})\`);
          });
  
          // Add zoom functionality
          const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", e => {
              container.attr("transform", e.transform);
            });
  
          svg.call(zoom);
          
          // Store current transform
          let currentTransform = d3.zoomIdentity;
          
          // Center button functionality
          document.getElementById('center-btn').addEventListener('click', () => {
            svg.transition().duration(750).call(
              zoom.transform,
              d3.zoomIdentity
            );
          });
          
          // Return key components for later use
          return {
            simulation,
            container,
            zoom,
            nodeLabels,
            links: link
          };
        }
        
        // Create initial visualization
        const viz = createVisualization(data);
        
        // Setup folder filter
        document.getElementById('folder-filter').addEventListener('change', function() {
          const folderPrefix = this.value;
          
          // Filter nodes
          let filteredNodes = originalData.nodes;
          if (folderPrefix) {
            filteredNodes = originalData.nodes.filter(node => 
              node.id.startsWith(folderPrefix) || (node.missing && document.getElementById('show-missing').checked)
            );
          } else if (!document.getElementById('show-missing').checked) {
            filteredNodes = originalData.nodes.filter(node => !node.missing);
          }
          
          // Get node IDs for link filtering
          const nodeIds = new Set(filteredNodes.map(n => n.id));
          
          // Filter links
          const filteredLinks = originalData.links.filter(link => {
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
            return nodeIds.has(sourceId) && nodeIds.has(targetId);
          });
          
          // Update visualization
          filteredData = {
            nodes: filteredNodes,
            links: filteredLinks
          };
          
          // Recreate visualization with filtered data
          createVisualization(filteredData);
        });
        
        // Show/hide missing nodes
        document.getElementById('show-missing').addEventListener('change', function() {
          // Re-trigger the folder filter to apply the missing nodes filter
          document.getElementById('folder-filter').dispatchEvent(new Event('change'));
        });
        
        // Show/hide node labels
        document.getElementById('show-labels').addEventListener('change', function() {
          const showLabels = this.checked;
          d3.selectAll(".node-label").style("display", showLabels ? "inline" : "none");
        });
        
        // Show/hide duplicate connections
        document.getElementById('show-duplicates').addEventListener('change', function() {
          const showDuplicates = this.checked;
          d3.selectAll(".links line.duplicate").style("display", showDuplicates ? "inline" : "none");
        });
        
        // Search functionality
        document.getElementById('search-btn').addEventListener('click', function() {
          const searchTerm = document.getElementById('search-input').value.toLowerCase();
          if (!searchTerm) return;
          
          const results = originalData.nodes.filter(node => 
            node.id.toLowerCase().includes(searchTerm)
          );
          
          const resultsContainer = document.getElementById('search-results');
          resultsContainer.style.display = results.length ? 'block' : 'none';
          
          if (results.length === 0) {
            resultsContainer.textContent = 'No results found';
          } else {
            resultsContainer.innerHTML = \`Found \${results.length} results: <br>\`;
            results.slice(0, 10).forEach(node => {
              const resultItem = document.createElement('div');
              resultItem.textContent = node.id;
              resultItem.style.cursor = 'pointer';
              resultItem.style.padding = '3px';
              resultItem.style.marginTop = '2px';
              resultItem.addEventListener('click', () => {
                // Find the node in the visualization and center on it
                const nodeInViz = filteredData.nodes.find(n => n.id === node.id);
                if (nodeInViz) {
                  // Center on this node
                  const transform = d3.zoomIdentity
                    .translate(width / 2, height / 2)
                    .scale(1.5)
                    .translate(-nodeInViz.x, -nodeInViz.y);
                  
                  svg.transition().duration(750).call(
                    viz.zoom.transform,
                    transform
                  );
                } else {
                  showError(\`Node \${node.id} is not in the current filtered view.\`);
                }
              });
              resultsContainer.appendChild(resultItem);
            });
            
            if (results.length > 10) {
              const more = document.createElement('div');
              more.textContent = \`...and \${results.length - 10} more\`;
              more.style.fontStyle = 'italic';
              more.style.marginTop = '5px';
              resultsContainer.appendChild(more);
            }
          }
        });
        
        // Allow pressing Enter in search box
        document.getElementById('search-input').addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
            document.getElementById('search-btn').click();
          }
        });
        
        // Debug functionality
        document.getElementById('inspect-data-btn').addEventListener('click', function() {
          console.log('Original data:', originalData);
          console.log('Filtered data:', filteredData);
          console.log('Missing nodes:', missingNodes);
          alert('Check the browser console for data inspection');
        });
      })
      .catch(error => {
        showError(\`Error loading dependency data: \${error.message}\`);
        console.error('Error:', error);
      });
  </script>
</body>
</html>`;

  fs.writeFileSync(path.join(config.outputDir, 'dependency-visualizer.html'), visualizerHtml);
  
  // Generate duplicate files report
  const duplicateFilesReport = `# Duplicate Files Report

## Overview
This report identifies identical files that exist in multiple locations throughout the codebase.
These are files that have the same name AND the same content.

Total duplicate file groups found: ${duplicateGroups.length}

## Duplicate File Groups

${duplicateGroups.map(group => {
  return `### ${group.basename} (${group.files.length} duplicates)
${group.files.map(file => `- ${file}`).join('\n')}
`;
}).join('\n')}

## Recommendation
Consider consolidating these duplicate files to reduce redundancy and maintenance overhead.
Possible strategies:
1. Move shared code to a common location and import it
2. Use symbolic links if separate copies are necessary
3. Delete redundant copies if they're part of an incomplete migration

Generated on: ${new Date().toISOString()}
`;

  fs.writeFileSync(path.join(config.outputDir, 'duplicate-files.md'), duplicateFilesReport);
  
  console.log(`Reports generated in ${config.outputDir}`);
}

/**
 * Main function to run the analysis
 */
async function main() {
  console.log('Starting enhanced dependency analysis...');
  
  // Get all files
  const files = getAllFiles();
  
  // Analyze each file
  console.log('Analyzing file dependencies...');
  let count = 0;
  for (const file of files) {
    if (!shouldExcludePath(file)) {
      analyzeFile(file);
      count++;
      if (count % 100 === 0) {
        console.log(`Analyzed ${count} files...`);
      }
    }
  }
  
  // Process barrel dependencies
  processBarrelDependencies();
  
  // Process route component references
  processRouteReferences();
  
  // Find orphaned files
  const orphanedFiles = findOrphanedFiles();
  console.log(`Found ${orphanedFiles.length} potentially orphaned files`);
  
  // Generate reports
  generateReports(orphanedFiles);
  
  console.log('Enhanced dependency analysis complete!');
}

// Run the script
main().catch(error => {
  console.error('Error running enhanced dependency analysis:', error);
  process.exit(1);
}); 