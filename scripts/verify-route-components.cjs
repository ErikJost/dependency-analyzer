#!/usr/bin/env node

/**
 * verify-route-components.cjs
 * 
 * This script analyzes React application routes to identify which orphaned components
 * might be referenced in route definitions. It checks for common React Router patterns
 * and dynamic imports in route configurations.
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Configuration
const config = {
  rootDir: path.resolve(__dirname, '..'),
  extensions: ['.ts', '.tsx', '.js', '.jsx'],
  // Files likely to contain route definitions
  routeFiles: [
    '**/routes.tsx',
    '**/Routes.tsx',
    '**/router.tsx',
    '**/Router.tsx',
    '**/App.tsx',
    '**/index.tsx',
    '**/main.tsx'
  ],
  // Orphaned files report
  orphanedFilesReport: path.resolve(__dirname, '..', 'docs', 'dependency-analysis', 'confirmed-orphaned-files.md'),
  // Output file
  outputFile: path.resolve(__dirname, '..', 'docs', 'dependency-analysis', 'route-component-verification.md')
};

/**
 * Extract orphaned files from the report
 */
function getOrphanedFiles() {
  try {
    if (!fs.existsSync(config.orphanedFilesReport)) {
      console.error(`Orphaned files report not found: ${config.orphanedFilesReport}`);
      process.exit(1);
    }
    
    const content = fs.readFileSync(config.orphanedFilesReport, 'utf-8');
    const orphanedFiles = [];
    const fileRegex = /^- (.+?)(?:\s+|$)/gm;
    let match;
    
    while ((match = fileRegex.exec(content)) !== null) {
      orphanedFiles.push(match[1]);
    }
    
    console.log(`Found ${orphanedFiles.length} orphaned files in the report`);
    return orphanedFiles;
  } catch (error) {
    console.error('Error reading orphaned files report:', error);
    process.exit(1);
  }
}

/**
 * Find all potential route definition files
 */
function findRouteFiles() {
  const patterns = config.routeFiles.map(pattern => `**/${pattern}`);
  const routeFiles = new Set();
  
  patterns.forEach(pattern => {
    const matches = glob.sync(pattern, {
      cwd: config.rootDir,
      ignore: ['**/node_modules/**', '**/build/**', '**/dist/**', '**/archive/**'],
      absolute: true
    });
    
    matches.forEach(file => routeFiles.add(file));
  });
  
  console.log(`Found ${routeFiles.size} potential route definition files`);
  return Array.from(routeFiles);
}

/**
 * Extract component names from orphaned files
 */
function extractComponentNames(orphanedFiles) {
  return orphanedFiles.map(file => {
    const basename = path.basename(file, path.extname(file));
    return {
      file,
      component: basename
    };
  });
}

/**
 * Analyze route files for references to orphaned components
 */
function analyzeRouteFiles(routeFiles, orphanedComponents) {
  const results = {};
  
  orphanedComponents.forEach(component => {
    results[component.file] = [];
  });
  
  routeFiles.forEach(routeFile => {
    try {
      const content = fs.readFileSync(routeFile, 'utf-8');
      const relativeRoutePath = path.relative(config.rootDir, routeFile);
      
      // Check for each component
      orphanedComponents.forEach(({ file, component }) => {
        // React Router v6 patterns
        const elementPattern = new RegExp(`element\\s*=\\s*{\\s*<\\s*${component}\\s*`, 'g');
        const componentPattern = new RegExp(`component\\s*=\\s*{\\s*${component}\\s*}`, 'g');
        
        // React Router v5 patterns
        const v5ComponentPattern = new RegExp(`component\\s*=\\s*{\\s*${component}\\s*}`, 'g');
        const v5RenderPattern = new RegExp(`render\\s*=\\s*{\\s*\\(?\\s*\\)?\\s*=>\\s*<\\s*${component}\\b`, 'g');
        
        // Lazy loading patterns
        const lazyPattern = new RegExp(`const\\s+${component}\\s*=\\s*(?:React\\.)?lazy\\s*\\(`, 'g');
        
        // Dynamic import patterns
        const dynamicImportPattern = new RegExp(`import\\s*\\(\\s*['"].*?${component}['"]\\s*\\)`, 'g');
        
        // String literal component references
        const stringComponentPattern = new RegExp(`['"]${component}['"]`, 'g');
        
        // Check each pattern
        const patterns = [
          { type: 'element prop', regex: elementPattern },
          { type: 'component prop', regex: componentPattern },
          { type: 'v5 component prop', regex: v5ComponentPattern },
          { type: 'v5 render prop', regex: v5RenderPattern },
          { type: 'lazy loaded', regex: lazyPattern },
          { type: 'dynamic import', regex: dynamicImportPattern },
          { type: 'string reference', regex: stringComponentPattern }
        ];
        
        patterns.forEach(({ type, regex }) => {
          let match;
          while ((match = regex.exec(content)) !== null) {
            const lineNumber = content.substring(0, match.index).split('\n').length;
            
            results[file].push({
              routeFile: relativeRoutePath,
              lineNumber,
              matchType: type,
              context: content.split('\n')[lineNumber - 1].trim()
            });
          }
        });
      });
    } catch (error) {
      console.error(`Error analyzing route file ${routeFile}:`, error);
    }
  });
  
  return results;
}

/**
 * Generate report from analysis results
 */
function generateReport(results) {
  const componentsWithReferences = Object.keys(results).filter(file => results[file].length > 0);
  const componentsWithoutReferences = Object.keys(results).filter(file => results[file].length === 0);
  
  const report = `# Route Component Verification

## Overview
This report identifies orphaned components that might be referenced in route definitions
or loaded dynamically, which wouldn't be detected by static import analysis.

## Components Referenced in Routes

${componentsWithReferences.length === 0 ? 'No components found referenced in routes.' : 
  componentsWithReferences.map(file => `
### ${file}

${results[file].map(ref => `
- **Referenced in**: ${ref.routeFile}:${ref.lineNumber}
- **Pattern**: ${ref.matchType}
- **Context**: \`${ref.context}\`
`).join('')}

`).join('')}

## Components Not Found in Routes

These components were not found in any routing configuration and are more likely to be truly orphaned:

${componentsWithoutReferences.map(file => `- ${file}`).join('\n')}

## Recommendation

1. Components referenced in routes should be preserved even if they appear orphaned in static analysis
2. Components not found in routes should be further verified for dynamic imports or consider archiving them
3. Some components might be loaded through a dynamic mechanism not detected by this script (e.g., eval, reflection)

Generated on: ${new Date().toISOString()}
`;

  return report;
}

/**
 * Main function
 */
async function main() {
  try {
    // Get orphaned files
    const orphanedFiles = getOrphanedFiles();
    
    // Find potential route files
    const routeFiles = findRouteFiles();
    
    // Extract component names from orphaned files
    const orphanedComponents = extractComponentNames(orphanedFiles);
    
    // Analyze route files
    console.log('Analyzing route files...');
    const results = analyzeRouteFiles(routeFiles, orphanedComponents);
    
    // Generate report
    const report = generateReport(results);
    
    // Write report
    const outputDir = path.dirname(config.outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    fs.writeFileSync(config.outputFile, report);
    console.log(`Report written to ${config.outputFile}`);
    
  } catch (error) {
    console.error('Error in verification script:', error);
    process.exit(1);
  }
}

// Run the script
main().catch(console.error); 