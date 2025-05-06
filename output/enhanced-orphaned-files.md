# Potentially Orphaned Files
  
## Overview
This report identifies files in the codebase that are not imported by any other files and may be orphaned.
This enhanced analysis includes barrel file (index.ts) re-exports and route component references.

Total files analyzed: 12
Potentially orphaned files: 11

## Files that may be orphaned

- updated_mcp.json

- temp_multi_server_mcp.json

- simple_mcp_fixed.json

- simple_mcp_clean.json

- simple_mcp.json

- package-lock.json

- mcp.server.json

- final_mcp.json

- dependency-graph.json

- debug_mcp.json

- output/dependency-graph.json

## Note
Some files may be legitimately unused directly (e.g., types, utilities called via dynamic imports, 
files referenced via webpack/vite plugins, etc.). Further investigation may be required.

## Barrel Files Analysis
The following barrel files (index.ts/js) were analyzed for re-exports:



## Route Component References
The following component references were found in route definitions:



Generated on: 2025-05-06T22:28:45.444Z
