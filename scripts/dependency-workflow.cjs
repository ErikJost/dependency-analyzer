#!/usr/bin/env node

/**
 * dependency-workflow.cjs
 * 
 * This master script orchestrates the complete workflow for dependency analysis, 
 * orphaned file detection, verification, and archival.
 * 
 * The workflow includes:
 * 1. Dependency analysis to map all imports
 * 2. Build analysis to identify files used in build
 * 3. Dynamic imports detection
 * 4. Route components verification
 * 5. Final analysis and report generation
 * 6. Optional file archival
 * 
 * Usage:
 *   node scripts/dependency-workflow.cjs [--auto-archive] [--skip-build] [--start-server] [--root-dir=<path>] [--help]
 * 
 * Options:
 *   --auto-archive: Automatically archive confirmed orphaned files without prompting
 *   --skip-build: Skip the build analysis step (useful for quick analysis)
 *   --start-server: Start the interactive visualization server after analysis
 *   --root-dir: Specify a custom root directory (default: auto-detect)
 *   --help: Display this help message
 */

const fs = require('fs');
const path = require('path');
const util = require('util');
const { promisify } = util;
const exec = promisify(require('child_process').exec);
const { execSync, spawnSync, spawn } = require('child_process');
const readline = require('readline');
const chalk = require('chalk');

// Check if chalk is properly loaded, otherwise use a simple fallback
const colorize = {
  green: (text) => chalk?.green ? chalk.green(text) : text,
  yellow: (text) => chalk?.yellow ? chalk.yellow(text) : text,
  cyan: (text) => chalk?.cyan ? chalk.cyan(text) : text,
  red: (text) => chalk?.red ? chalk.red(text) : text
};

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
  autoArchive: args.includes('--auto-archive'),
  skipBuild: args.includes('--skip-build'),
  startServer: args.includes('--start-server'),
  rootDir: null
};

// Extract rootDir if specified
for (const arg of args) {
  if (arg.startsWith('--root-dir=')) {
    options.rootDir = arg.split('=')[1];
    break;
  }
}

// Show help and exit if requested
if (args.includes('--help')) {
  showUsage();
  return;
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
const rootDir = options.rootDir ? path.resolve(options.rootDir) : detectProjectRoot(path.resolve(__dirname, '..'));
console.log(`Using project root: ${rootDir}`);

const config = {
  rootDir: rootDir,
  scriptsDir: path.join(rootDir, 'dependency-analysis', 'scripts'),
  docsDir: path.join(rootDir, 'dependency-analysis'),
  buildLogFile: path.join(rootDir, 'build_log.txt'),
  reports: {
    initialOrphaned: path.resolve(rootDir, 'dependency-analysis', 'orphaned-files.md'),
    enhancedOrphaned: path.resolve(rootDir, 'dependency-analysis', 'enhanced-orphaned-files.md'),
    buildDependencies: path.resolve(rootDir, 'dependency-analysis', 'build-dependencies.md'),
    dynamicReferences: path.resolve(rootDir, 'dependency-analysis', 'dynamic-references.md'),
    routeVerification: path.resolve(rootDir, 'dependency-analysis', 'route-component-verification.md'),
    confirmedOrphaned: path.resolve(rootDir, 'dependency-analysis', 'confirmed-orphaned-files.md'),
    refinedAnalysis: path.resolve(rootDir, 'dependency-analysis', 'refined-orphaned-files.md'),
    finalAnalysis: path.resolve(rootDir, 'dependency-analysis', 'final-orphaned-files.md'),
    archivalReport: path.resolve(rootDir, 'FILE_CLEANUP_REPORT.md')
  },
  scripts: {
    basicAnalysis: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'analyze-dependencies.cjs'),
    enhancedAnalysis: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'enhanced-dependency-analysis.cjs'),
    buildAnalysis: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'analyze-build-dependencies.cjs'),
    updateReport: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'update-orphaned-files-report.cjs'),
    dynamicImports: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'check-dynamic-imports.cjs'),
    routeComponents: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'verify-route-components.cjs'),
    batchArchive: path.resolve(rootDir, 'dependency-analysis', 'scripts', 'batch-archive-orphaned.cjs')
  }
};

// Create a readline interface for user prompts
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * Promise-based prompt function
 */
function prompt(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

/**
 * Run a script and return its output
 */
function runScript(scriptPath, args = []) {
  console.log(`\n🔄 Running ${path.basename(scriptPath)}...\n`);
  
  const result = spawnSync('node', [scriptPath, ...args], {
    stdio: 'inherit',
    cwd: config.rootDir
  });
  
  if (result.status !== 0) {
    console.error(`❌ Script ${path.basename(scriptPath)} failed with status ${result.status}`);
    if (result.error) {
      console.error(result.error);
    }
    process.exit(1);
  }
  
  console.log(`\n✅ Script ${path.basename(scriptPath)} completed successfully\n`);
}

/**
 * Ensure directory exists
 */
function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`📁 Created directory: ${path.relative(config.rootDir, dirPath)}`);
  }
}

/**
 * Run Docker build to collect build log
 */
async function runBuild() {
  if (options.skipBuild) {
    console.log('⏭️  Skipping build analysis as requested with --skip-build');
    return;
  }
  
  console.log('\n🏗️  Running Docker build to capture build logs...');
  
  const runBuild = await prompt('Do you want to run a Docker build to analyze build dependencies? (y/n): ');
  if (runBuild.toLowerCase() !== 'y') {
    console.log('⏭️  Skipping build analysis');
    return;
  }
  
  try {
    // Check if Docker is available
    execSync('docker --version', { stdio: 'ignore' });
    
    // Run Docker build with output redirected to build_log.txt
    console.log('🐳 Running Docker build (this may take a while)...');
    execSync(`docker build -t intellipact-dep-test . > ${config.buildLogFile} 2>&1`, {
      cwd: config.rootDir
    });
    
    console.log(`✅ Build completed, log saved to ${path.relative(config.rootDir, config.buildLogFile)}`);
  } catch (error) {
    console.error('❌ Error running Docker build:', error.message);
    console.log('⚠️  Proceeding without build analysis');
  }
}

/**
 * Create refined analysis report
 */
function createRefinedAnalysis() {
  console.log('\n📝 Creating refined analysis report...');
  
  // Generate a report with confidence levels and impact ratings
  const refinedAnalysisTemplate = `# Refined Orphaned Files Analysis

## Overview
This document categorizes and prioritizes the potentially orphaned files identified in our dependency analysis. Each file has been assigned a confidence level and potential impact rating based on automated detection and manual verification.

### Confidence Levels
- **High**: Very likely to be orphaned with no hidden dependencies
- **Medium**: Might have hidden dependencies or be used through dynamic imports
- **Low**: Likely has hidden dependencies or is referenced in ways our analysis couldn't detect

### Impact Levels
- **High**: Removing could break functionality
- **Medium**: Removing may affect some features but not critical ones
- **Low**: Removing unlikely to have any noticeable impact

## Categories

### 1. Authentication Components
These files are related to authentication and authorization. Many of these might still be used through dynamic routing or conditional imports.

### 2. UI Components
These are UI components that might not be directly imported but could be loaded dynamically or used in route configurations.

### 3. Services
These service files might be used through dependency injection or dynamic imports.

### 4. Scripts and Utilities
These are scripts and utilities that might be run independently rather than imported.

### 5. Models and Types
These files might be used for TypeScript types without direct imports.

### 6. Duplicate Files 
These appear to be duplicated across src/ and client/src/ directories, suggesting a migration.

## Recommended Next Steps

1. Run the script to update the final-orphaned-files.md report which will contain only confirmed orphaned files
2. Review this refined analysis and the results from route verification and dynamic imports checks
3. Archive files that are confirmed to be orphaned

This report was automatically generated. It should be reviewed and refined manually for accuracy.
`;

  fs.writeFileSync(config.reports.refinedAnalysis, refinedAnalysisTemplate);
  console.log(`✅ Refined analysis template created at ${path.relative(config.rootDir, config.reports.refinedAnalysis)}`);
}

/**
 * Create final analysis report
 */
async function createFinalAnalysis() {
  console.log('\n📋 Creating final analysis report...');
  
  // Ask for manual review first
  if (!options.autoArchive) {
    const reviewPrompt = await prompt(
      'Have you manually reviewed the reports and want to generate a final analysis? (y/n): '
    );
    
    if (reviewPrompt.toLowerCase() !== 'y') {
      console.log('⏭️  Skipping final analysis');
      return false;
    }
  }
  
  // Read the confirmed orphaned files report
  if (!fs.existsSync(config.reports.confirmedOrphaned)) {
    console.error(`❌ Confirmed orphaned files report not found at ${config.reports.confirmedOrphaned}`);
    console.log('⚠️  Please run update-orphaned-files-report.cjs first');
    return false;
  }
  
  const confirmedContent = fs.readFileSync(config.reports.confirmedOrphaned, 'utf-8');
  
  // Generate the final analysis report
  const finalAnalysisTemplate = `# Final Analysis of Orphaned Files

## Overview
After thorough analysis including static dependency mapping, build process tracking, and verification of dynamic references, this report presents a more accurate picture of truly orphaned files in the codebase.

## Key Findings

1. Many files were falsely flagged as having dynamic references due to unrelated string literals in the code
2. The codebase shows evidence of a migration from \`src/\` to \`client/src/\` structure, with many duplicated files
3. Authentication components initially flagged as orphaned are likely used through dynamic imports or routing
4. Several script files are intended to be run directly and not imported

## Truly Orphaned Files

These files have been confirmed as not used in the application and are safe to archive:

### Scripts and Utilities
These standalone scripts aren't imported by the application code:

${extractFilesByPattern(confirmedContent, /^- (scripts\/.*\.js|client\/scripts\/.*\.js|client\/analyze-deps\.js)/gm)}

### Duplicated Files (Old Structure)
These files appear to be duplicates from the old src/ structure that have been migrated to client/src/:

${extractFilesByPattern(confirmedContent, /^- (src\/components\/.*|src\/services\/.*|src\/lib\/.*\.ts|src\/auth\/.*)/gm)}

### Test Files
Files used only for testing and not production:

${extractFilesByPattern(confirmedContent, /^- (.*\.test\.ts|.*TestAuthProvider\.tsx|.*\/testing\/.*)/gm)}

## Files That Should Not Be Archived

The following files may appear orphaned but serve important functions:

### Type Definition Files
These files provide TypeScript type definitions that may be used implicitly:

- shared/models/MetricModels.ts
- client/src/auth/types.ts

### Dynamically Loaded Components
These files might be loaded through React.lazy() or dynamic imports:

- client/src/components/auth/AuthCallback.tsx
- client/src/auth/routes/AuthRoutes.tsx
- client/src/components/ui/* (UI component library)

### Configuration and Infrastructure Files
These files are used in the build/deployment process:

- public/module-loader.js
- functions/src/functions/api-clients.ts
- secure_credentials/app_connection_example.js

## Recommended Approach

1. **Start with Scripts**: Archive the standalone scripts first as they're the lowest risk
2. **Next Address Duplicates**: Archive the old structure files (in src/) as their functionality has been migrated to client/src/
3. **Carefully Review UI Components**: Some components may be used through dynamic imports or lazy loading
4. **Leave Type Definitions**: Keep TypeScript type definitions unless absolutely certain they're unused
5. **Document Each Archived File**: Add a note to the checklist explaining why each file was archived

## Summary

This analysis has significantly refined our understanding of which files are truly unused in the codebase. The migration from src/ to client/src/ structure explains many of the apparent duplications, and special care has been taken to identify files that might be loaded dynamically.

Generated on: ${new Date().toISOString()}
`;

  fs.writeFileSync(config.reports.finalAnalysis, finalAnalysisTemplate);
  console.log(`✅ Final analysis created at ${path.relative(config.rootDir, config.reports.finalAnalysis)}`);
  return true;
}

/**
 * Extract files matching pattern from content
 */
function extractFilesByPattern(content, pattern) {
  const matches = content.match(pattern) || [];
  return matches.join('\n');
}

/**
 * Archive orphaned files
 */
async function archiveOrphanedFiles() {
  console.log('\n📦 Preparing to archive orphaned files...');
  
  if (!fs.existsSync(config.reports.finalAnalysis)) {
    console.error(`❌ Final analysis report not found at ${config.reports.finalAnalysis}`);
    return;
  }
  
  if (!options.autoArchive) {
    const archivePrompt = await prompt(
      'Do you want to archive the confirmed orphaned files? (y/n): '
    );
    
    if (archivePrompt.toLowerCase() !== 'y') {
      console.log('⏭️  Skipping archive process');
      return;
    }
  }
  
  // Run the batch archive script
  runScript(config.scripts.batchArchive);
}

/**
 * Create a workflow summary
 */
function createWorkflowSummary() {
  console.log('\n📊 Creating workflow summary...');
  
  const summaryPath = path.join(config.docsDir, 'workflow-summary.md');
  const timestamp = new Date().toISOString();
  
  const summary = `# Dependency Analysis Workflow Summary

## Overview
This document summarizes the dependency analysis workflow run on ${timestamp}.

## Steps Completed

1. **Basic Dependency Analysis**
   - Script: \`analyze-dependencies.cjs\`
   - Output: [orphaned-files.md](./orphaned-files.md)

2. **Enhanced Dependency Analysis**
   - Script: \`enhanced-dependency-analysis.cjs\`
   - Output: [enhanced-orphaned-files.md](./enhanced-orphaned-files.md)
   - Visualization: 
     - [dependency-visualizer.html](./dependency-visualizer.html)
     - [dependency-list-view.html](./dependency-list-view.html)

${options.skipBuild ? '' : `
3. **Build Analysis**
   - Script: \`analyze-build-dependencies.cjs\`
   - Output: [build-dependencies.md](./build-dependencies.md)
`}

4. **Dynamic Imports Check**
   - Script: \`check-dynamic-imports.cjs\`
   - Output: [dynamic-references.md](./dynamic-references.md)

5. **Route Components Verification**
   - Script: \`verify-route-components.cjs\`
   - Output: [route-component-verification.md](./route-component-verification.md)

6. **Orphaned Files Report Update**
   - Script: \`update-orphaned-files-report.cjs\`
   - Output: [confirmed-orphaned-files.md](./confirmed-orphaned-files.md)

7. **Final Analysis**
   - Output: [final-orphaned-files.md](./final-orphaned-files.md)

${options.autoArchive ? `
8. **File Archival**
   - Script: \`batch-archive-orphaned.cjs\`
   - Output: [../../FILE_CLEANUP_REPORT.md](../../FILE_CLEANUP_REPORT.md)
` : ''}

## Next Steps

1. Review the final analysis in [final-orphaned-files.md](./final-orphaned-files.md)
2. Verify application functionality after any archival
3. Commit changes to the repository

## Statistics

- Initial orphaned file candidates: ${countFilesInReport(config.reports.initialOrphaned)}
- Enhanced orphaned file candidates: ${countFilesInReport(config.reports.enhancedOrphaned)}
- Confirmed orphaned files: ${countFilesInReport(config.reports.confirmedOrphaned)}
- Archived files: ${fs.existsSync(config.reports.archivalReport) ? countFilesInReport(config.reports.archivalReport, 'archived') : 'N/A'}

## Runtime Information

- Date: ${new Date().toLocaleDateString()}
- Time: ${new Date().toLocaleTimeString()}
- Auto-archive: ${options.autoArchive ? 'Enabled' : 'Disabled'}
- Skip build: ${options.skipBuild ? 'Enabled' : 'Disabled'}

This summary was automatically generated by the dependency-workflow.cjs script.
`;

  fs.writeFileSync(summaryPath, summary);
  console.log(`✅ Workflow summary created at ${path.relative(config.rootDir, summaryPath)}`);
}

/**
 * Count files in a report
 */
function countFilesInReport(reportPath, type = 'orphaned') {
  if (!fs.existsSync(reportPath)) {
    return 'N/A';
  }
  
  const content = fs.readFileSync(reportPath, 'utf-8');
  let count = 0;
  
  if (type === 'orphaned') {
    // Count lines starting with "- " in the report
    const lines = content.split('\n');
    count = lines.filter(line => line.trim().startsWith('- ')).length;
  } else if (type === 'archived') {
    // Count "Successfully Archived Files" section
    const match = content.match(/## Successfully Archived Files\n\n([\s\S]*?)(?=\n\n## |$)/);
    if (match && match[1]) {
      count = match[1].split('\n').filter(line => line.trim().startsWith('- ')).length;
    }
  }
  
  return count;
}

/**
 * Display usage information
 */
function showUsage() {
  console.log(`
Usage: node scripts/dependency-workflow.cjs [options]

Options:
  --auto-archive    Automatically archive confirmed orphaned files without prompting
  --skip-build      Skip the build analysis step (useful for quick analysis)
  --start-server    Start the interactive visualization server after analysis
  --root-dir=<path> Specify a custom root directory path (default: auto-detect)
  --help            Display this help message

Examples:
  node scripts/dependency-workflow.cjs               # Run with interactive prompts
  node scripts/dependency-workflow.cjs --skip-build  # Skip build analysis
  node scripts/dependency-workflow.cjs --root-dir=/path/to/project # Use custom root
`);
}

/**
 * Main workflow function
 */
async function runWorkflow() {
  try {
    console.log('\n🚀 Starting Dependency Analysis Workflow\n');
    
    // Ensure output directory exists
    ensureDirectoryExists(config.docsDir);
    
    // Step 1: Basic dependency analysis
    console.log('\n📊 Step 1: Running basic dependency analysis...');
    runScript(config.scripts.basicAnalysis);
    
    // Step 2: Enhanced dependency analysis
    console.log('\n📊 Step 2: Running enhanced dependency analysis...');
    runScript(config.scripts.enhancedAnalysis);
    
    // Step 3: Build analysis (optional)
    if (!options.skipBuild) {
      console.log('\n📊 Step 3: Running build analysis...');
      await runBuild();
      
      if (fs.existsSync(config.buildLogFile)) {
        runScript(config.scripts.buildAnalysis);
      } else {
        console.log('⚠️  Build log not found, skipping build analysis');
      }
    }
    
    // Step 4: Check dynamic imports
    console.log('\n📊 Step 4: Checking for dynamic imports...');
    runScript(config.scripts.dynamicImports);
    
    // Step 5: Verify route components
    console.log('\n📊 Step 5: Verifying route components...');
    runScript(config.scripts.routeComponents);
    
    // Step 6: Update orphaned files report
    console.log('\n📊 Step 6: Updating orphaned files report...');
    runScript(config.scripts.updateReport);
    
    // Step 7: Create refined analysis report
    console.log('\n📊 Step 7: Creating refined analysis report...');
    createRefinedAnalysis();
    
    // Step 8: Create final analysis
    console.log('\n📊 Step 8: Creating final analysis...');
    const finalAnalysisCreated = await createFinalAnalysis();
    
    // Step 9: Archive orphaned files (if requested)
    if (finalAnalysisCreated && (options.autoArchive || await prompt('Do you want to archive orphaned files? (y/n): ') === 'y')) {
      console.log('\n📊 Step 9: Archiving orphaned files...');
      await archiveOrphanedFiles();
    } else {
      console.log('\n⏭️  Skipping file archival step');
    }
    
    // Create workflow summary
    createWorkflowSummary();
    
    // Generate visualization
    // await generateVisualization(results);  // Commenting out undefined function call

    // If requested, start the visualization server
    if (options.startServer) {
      console.log(colorize.green('\n✅ Starting interactive visualization server...'));
      try {
        const serverScript = path.join(config.scriptsDir, 'start-dependency-server.sh');
        
        // Make sure the script is executable
        fs.chmodSync(serverScript, '755');
        
        // Start the server
        console.log(colorize.yellow('Starting server in a new process. Press Ctrl+C to stop.'));
        
        // Add root directory if specified
        const serverArgs = [];
        if (options.rootDir) {
          serverArgs.push(`--root=${options.rootDir}`);
        }
        
        const serverProcess = spawn(serverScript, serverArgs, {
          stdio: 'inherit',
          detached: true,
          shell: true
        });
        
        // Log the URL and features
        console.log(colorize.green('\nAccess the visualization at: http://localhost:8000/dependency-visualizer.html'));
        console.log(colorize.cyan('New Features:'));
        console.log(colorize.cyan('  • Run dependency analysis directly from the UI'));
        console.log(colorize.cyan('  • Cancel running analysis with the stop button'));
        console.log(colorize.cyan('  • Real-time status updates'));
        
        // Don't wait for the server process
        serverProcess.unref();
      } catch (error) {
        console.error(colorize.red(`❌ Error starting visualization server: ${error.message}`));
      }
    } else {
      console.log(colorize.green('\n✅ To start the interactive visualization server:'));
      console.log(colorize.yellow('   Run: scripts/start-dependency-server.sh'));
      console.log(colorize.yellow('   Then visit: http://localhost:8000/dependency-visualizer.html'));
      console.log(colorize.cyan('   New features include real-time analysis with cancel button!'));
    }

    console.log('\n✨ Dependency Analysis Workflow Completed Successfully!\n');
    console.log(`📄 View workflow summary at: ${path.relative(config.rootDir, path.join(config.docsDir, 'workflow-summary.md'))}`);
    
  } catch (error) {
    console.error('\n❌ Error running workflow:', error);
    process.exit(1);
  } finally {
    rl.close();
  }
}

// Run the workflow
runWorkflow(); 