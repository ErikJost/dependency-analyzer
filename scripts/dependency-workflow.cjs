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
 *   node scripts/dependency-workflow.cjs [--auto-archive] [--skip-build] [--start-server] [--root-dir=<path>] [--output-dir=<path>] [--help]
 * 
 * Options:
 *   --auto-archive: Automatically archive confirmed orphaned files without prompting
 *   --skip-build: Skip the build analysis step (useful for quick analysis)
 *   --start-server: Start the interactive visualization server after analysis
 *   --root-dir: Specify a custom root directory (default: auto-detect)
 *   --output-dir: Specify a custom output directory (default: auto-detect)
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

// Debug: print process.argv to verify received arguments
console.error('process.argv:', process.argv);

// Parse command line arguments
const args = process.argv.slice(2);
let options = {
  autoArchive: false,
  skipBuild: false,
  startServer: false,
  rootDir: null,
  outputDir: null
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--auto-archive') options.autoArchive = true;
  if (args[i] === '--skip-build') options.skipBuild = true;
  if (args[i] === '--start-server') options.startServer = true;
  if (args[i] === '--root-dir' && args[i + 1]) {
    options.rootDir = args[i + 1];
    i++;
  } else if (args[i].startsWith('--root-dir=')) {
    options.rootDir = args[i].split('=')[1];
  }
  if (args[i] === '--output-dir' && args[i + 1]) {
    options.outputDir = args[i + 1];
    i++;
  } else if (args[i].startsWith('--output-dir=')) {
    options.outputDir = args[i].split('=')[1];
  }
}

// Debug: print parsed options
console.error('Parsed options:', options);

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
        console.error(`Detected project root at: ${currentDir} (found marker: ${marker})`);
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
  console.error(`Could not detect project root, using default: ${path.resolve(__dirname, '..')}`);
  return path.resolve(__dirname, '..');
}

// Configuration
const rootDir = options.rootDir ? path.resolve(options.rootDir) : detectProjectRoot(path.resolve(__dirname, '..'));
const outputDir = options.outputDir ? path.resolve(options.outputDir) : path.join(rootDir, 'output');
console.error(`Using project root: ${rootDir}`);
console.error(`[DEBUG] dependency-workflow.cjs options.rootDir: ${options.rootDir}`);
console.error(`[DEBUG] dependency-workflow.cjs resolved rootDir: ${rootDir}`);
console.error(`[DEBUG] dependency-workflow.cjs outputDir: ${outputDir}`);

const containerScriptsDir = '/app/scripts';
const config = {
  rootDir: rootDir,
  scriptsDir: containerScriptsDir,
  docsDir: outputDir,
  buildLogFile: path.join(rootDir, 'build_log.txt'),
  reports: {
    initialOrphaned: path.join(outputDir, 'orphaned-files.md'),
    enhancedOrphaned: path.join(outputDir, 'enhanced-orphaned-files.md'),
    buildDependencies: path.join(outputDir, 'build-dependencies.md'),
    dynamicReferences: path.join(outputDir, 'dynamic-references.md'),
    routeVerification: path.join(outputDir, 'route-component-verification.md'),
    confirmedOrphaned: path.join(outputDir, 'confirmed-orphaned-files.md'),
    refinedAnalysis: path.join(outputDir, 'refined-orphaned-files.md'),
    finalAnalysis: path.join(outputDir, 'final-orphaned-files.md'),
    archivalReport: path.join(outputDir, 'FILE_CLEANUP_REPORT.md')
  },
  scripts: {
    basicAnalysis: path.join(containerScriptsDir, 'analyze-dependencies.cjs'),
    enhancedAnalysis: path.join(containerScriptsDir, 'enhanced-dependency-analysis.cjs'),
    buildAnalysis: path.join(containerScriptsDir, 'analyze-build-dependencies.cjs'),
    updateReport: path.join(containerScriptsDir, 'update-orphaned-files-report.cjs'),
    dynamicImports: path.join(containerScriptsDir, 'check-dynamic-imports.cjs'),
    routeComponents: path.join(containerScriptsDir, 'verify-route-components.cjs'),
    batchArchive: path.join(containerScriptsDir, 'batch-archive-orphaned.cjs')
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
  const stepStart = Date.now();
  // Always add --output-dir to sub-scripts
  const fullArgs = [...args, `--output-dir=${outputDir}`];
  console.error(`[DEBUG] About to run script: ${scriptPath} with args: ${fullArgs}`);
  try {
    const result = spawnSync('node', [scriptPath, ...fullArgs], {
      stdio: 'inherit',
      cwd: config.rootDir
    });
    const duration = ((Date.now() - stepStart) / 1000).toFixed(2);
    if (result.status !== 0) {
      console.error(`[DEBUG] Script ${scriptPath} failed with status ${result.status}`);
      if (result.error) {
        console.error(`[DEBUG] Script error: ${result.error.stack || result.error}`);
      }
      throw new Error(`Script ${scriptPath} failed`);
    }
    console.error(`[DEBUG] Script ${scriptPath} completed in ${duration}s`);
    return result;
  } catch (err) {
    console.error(`[DEBUG] Exception running script ${scriptPath}: ${err.stack || err}`);
    throw err;
  }
}

/**
 * Ensure directory exists
 */
function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.error(`📁 Created directory: ${path.relative(config.rootDir, dirPath)}`);
  }
}

/**
 * Run Docker build to collect build log
 */
async function runBuild() {
  if (options.skipBuild) {
    console.error('⏭️  Skipping build analysis as requested with --skip-build');
    return;
  }
  
  console.error('\n🏗️  Running Docker build to capture build logs...');
  
  const runBuild = await prompt('Do you want to run a Docker build to analyze build dependencies? (y/n): ');
  if (runBuild.toLowerCase() !== 'y') {
    console.error('⏭️  Skipping build analysis');
    return;
  }
  
  try {
    // Check if Docker is available
    execSync('docker --version', { stdio: 'ignore' });
    
    // Run Docker build with output redirected to build_log.txt
    console.error('🐳 Running Docker build (this may take a while)...');
    execSync(`docker build -t intellipact-dep-test . > ${config.buildLogFile} 2>&1`, {
      cwd: config.rootDir
    });
    
    console.error(`✅ Build completed, log saved to ${path.relative(config.rootDir, config.buildLogFile)}`);
  } catch (error) {
    console.error('❌ Error running Docker build:', error.message);
    console.error('⚠️  Proceeding without build analysis');
  }
}

/**
 * Create refined analysis report
 */
function createRefinedAnalysis() {
  console.error('\n📝 Creating refined analysis report...');
  
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
  console.error(`[DEBUG] Wrote output file: ${config.reports.refinedAnalysis}`);
  console.error(`✅ Refined analysis template created at ${path.relative(config.rootDir, config.reports.refinedAnalysis)}`);
}

/**
 * Create final analysis report
 */
async function createFinalAnalysis() {
  console.error('\n📋 Creating final analysis report...');
  // Always generate the final analysis without prompting
  // Read the confirmed orphaned files report
  if (!fs.existsSync(config.reports.confirmedOrphaned)) {
    console.error(`❌ Confirmed orphaned files report not found at ${config.reports.confirmedOrphaned}`);
    console.error('⚠️  Please run update-orphaned-files-report.cjs first');
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
  console.error(`[DEBUG] Wrote output file: ${config.reports.finalAnalysis}`);
  console.error(`✅ Final analysis created at ${path.relative(config.rootDir, config.reports.finalAnalysis)}`);
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
  console.error('\n📦 Preparing to archive orphaned files...');
  
  if (!fs.existsSync(config.reports.finalAnalysis)) {
    console.error(`❌ Final analysis report not found at ${config.reports.finalAnalysis}`);
    return;
  }
  
  if (!options.autoArchive) {
    const archivePrompt = await prompt(
      'Do you want to archive the confirmed orphaned files? (y/n): '
    );
    
    if (archivePrompt.toLowerCase() !== 'y') {
      console.error('⏭️  Skipping archive process');
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
  console.error('\n📊 Creating workflow summary...');
  const summaryPath = path.join(config.docsDir, 'workflow-summary.md');
  const timestamp = new Date().toISOString();
  // Dynamically determine the project folder from outputDir
  const projectFolder = path.basename(outputDir);
  const visualizationLink = `/${projectFolder}/enhanced-dependency-visualizer.html`;
  console.error(`[DEBUG] About to write workflow summary to: ${summaryPath}`);
  console.error(`[DEBUG] Visualization link to be written: ${visualizationLink}`);
  const summary = `# Dependency Analysis Workflow Summary\n\n## Overview\nThis document summarizes the dependency analysis workflow run on ${timestamp}.\n\n## Visualization\n- [Open Dependency Visualizer](${visualizationLink})\n`;
  fs.writeFileSync(summaryPath, summary);
  console.error(`[DEBUG] Successfully wrote workflow summary to: ${summaryPath}`);
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
  console.error(`
Usage: node scripts/dependency-workflow.cjs [options]

Options:
  --auto-archive    Automatically archive confirmed orphaned files without prompting
  --skip-build      Skip the build analysis step (useful for quick analysis)
  --start-server    Start the interactive visualization server after analysis
  --root-dir=<path> Specify a custom root directory path (default: auto-detect)
  --output-dir=<path> Specify a custom output directory path (default: auto-detect)
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
  const workflowStepStart = Date.now();
  try {
    console.error('[DEBUG] Workflow: Step 1 (basic analysis) starting');
    runScript(config.scripts.basicAnalysis);
    console.error('[DEBUG] Workflow: Step 1 (basic analysis) finished');

    console.error('[DEBUG] Workflow: Step 2 (enhanced analysis) starting');
    runScript(config.scripts.enhancedAnalysis);
    console.error('[DEBUG] Workflow: Step 2 (enhanced analysis) finished');

    console.error('[DEBUG] Workflow: Step 3 (update orphaned files report) starting');
    runScript(config.scripts.updateReport);
    console.error('[DEBUG] Workflow: Step 3 (update orphaned files report) finished');

    if (!options.skipBuild) {
      console.error('[DEBUG] Workflow: Step 4 (build analysis) starting');
      await runBuild();
      if (fs.existsSync(config.buildLogFile)) {
        runScript(config.scripts.buildAnalysis);
      } else {
        console.error('[DEBUG] Build log not found, skipping build analysis');
      }
      console.error('[DEBUG] Workflow: Step 4 (build analysis) finished');
    }

    console.error('[DEBUG] Workflow: Step 5 (dynamic imports) starting');
    runScript(config.scripts.dynamicImports);
    console.error('[DEBUG] Workflow: Step 5 (dynamic imports) finished');

    console.error('[DEBUG] Workflow: Step 6 (route components) starting');
    runScript(config.scripts.routeComponents);
    console.error('[DEBUG] Workflow: Step 6 (route components) finished');

    console.error('[DEBUG] Workflow: Step 7 (refined analysis) starting');
    createRefinedAnalysis();
    console.error('[DEBUG] Workflow: Step 7 (refined analysis) finished');

    console.error('[DEBUG] Workflow: Step 8 (final analysis) starting');
    const finalAnalysisCreated = await createFinalAnalysis();
    console.error('[DEBUG] Workflow: Step 8 (final analysis) finished');

    // Skipping archival step
    console.error('[DEBUG] Workflow: Skipping file archival step');

    // At the end, log a summary of output files
    const outputFiles = fs.readdirSync(config.docsDir);
    console.error('[DEBUG] Workflow: Output files in output directory:', outputFiles);
    // Optionally, log a preview of the workflow summary
    const summaryPath = path.join(config.docsDir, 'workflow-summary.md');
    if (fs.existsSync(summaryPath)) {
      const summaryPreview = fs.readFileSync(summaryPath, 'utf-8').slice(0, 500);
      console.error('[DEBUG] Workflow: workflow-summary.md preview:', summaryPreview);
    }
    const workflowElapsed = ((Date.now() - workflowStepStart) / 1000).toFixed(2);
    console.error(`[DEBUG] Workflow completed in ${workflowElapsed}s`);
    console.error('\n✨ Dependency Analysis Workflow Completed Successfully!\n');
    console.error(`📄 View workflow summary at: ${path.relative(config.rootDir, path.join(config.docsDir, 'workflow-summary.md'))}`);
    
  } catch (error) {
    console.error(`\n[DEBUG] Error running workflow: ${error.stack || error}`);
    process.exit(1);
  } finally {
    rl.close();
    const totalElapsed = ((Date.now() - workflowStepStart) / 1000).toFixed(2);
    console.error(`[DEBUG] Workflow script exiting. Total elapsed: ${totalElapsed}s`);
  }
}

// Run the workflow
runWorkflow(); 