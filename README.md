# Dependency Analyzer

A powerful tool for analyzing and visualizing code dependencies in JavaScript and TypeScript projects.

## Features

- Static code analysis to identify imports and exports
- Interactive force-directed graph visualization
- Orphaned file detection and reporting
- Build process dependency analysis
- Dynamic import detection
- Route component verification
- Cross-boundary dependency detection

## Installation

### Prerequisites

- Node.js (v14 or later)
- Python 3.6+

### Install from npm

```bash
npm install -g dependency-analyzer
```

### Clone Repository

```bash
git clone https://github.com/your-username/dependency-analyzer.git
cd dependency-analyzer
```

## Usage

### Quick Start

1. Navigate to your project directory
2. Run the dependency analyzer

```bash
dependency-analyzer --root=/path/to/your/project
```

Or if running from the cloned repository:

```bash
python3 server.py --root=/path/to/your/project
```

A web server will start, and your browser will open to the visualization page.

### CLI Options

```
python3 server.py [--root=<path>] [--port=<port>] [--script=<path>] [--no-browser]
```

- `--root`: Path to the root of the project to analyze (defaults to current directory)
- `--port`: Port to run the web server on (defaults to 8000)
- `--script`: Path to the analysis script (default: 'scripts/enhanced-dependency-analysis.cjs')
- `--no-browser`: Don't automatically open the browser

## Available Tools

### Analysis Scripts

- `scripts/enhanced-dependency-analysis.cjs` - Enhanced dependency analysis with visualization
- `scripts/analyze-dependencies.cjs` - Basic dependency analysis
- `scripts/analyze-build-dependencies.cjs` - Build process dependency analysis
- `scripts/check-dynamic-imports.cjs` - Detect dynamically imported modules
- `scripts/verify-route-components.cjs` - Verify route components
- `scripts/update-orphaned-files-report.cjs` - Update orphaned files report
- `scripts/batch-archive-orphaned.cjs` - Batch archive orphaned files

### Reports

The analysis generates various reports:

- Orphaned files analysis
- Build dependencies
- Dynamic references
- Route component verification

### Visualization

- Interactive force-directed graph visualization
- Filter by folder or file type
- Show/hide missing nodes and duplicates
- Search functionality
- Run analysis directly from the browser
- Cancel running analysis with stop button
- Real-time status updates

## Development

### Running Tests

```bash
npm test
```

### Building from Source

```bash
npm run build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 