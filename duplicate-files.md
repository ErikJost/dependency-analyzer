# Duplicate Files Report

## Overview
This report identifies identical files that exist in multiple locations throughout the codebase.
These are files that have the same name AND the same content.

Total duplicate file groups found: 1

## Duplicate File Groups

### dependency-graph.json (2 duplicates)
- dependency-graph.json
- docs/dependency-analysis/dependency-graph.json


## Recommendation
Consider consolidating these duplicate files to reduce redundancy and maintenance overhead.
Possible strategies:
1. Move shared code to a common location and import it
2. Use symbolic links if separate copies are necessary
3. Delete redundant copies if they're part of an incomplete migration

Generated on: 2025-05-05T22:59:30.223Z
