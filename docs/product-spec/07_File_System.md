# 07 File System

## Purpose

Project files should be easy to find, move, and back up.

## Project Folder

Each Project is stored as one folder.

Project folder contains:

- project.json
- sample folder
- devices folder
- regions folder
- reports folder
- exports folder
- logs folder

## Region Folder

Each Region has its own folder.

Region folder contains:

- region.json
- alignment.json
- scan_config.json
- scans folder
- analysis folder
- exports folder

## Scan Folder

Each Scan has its own folder.

Scan folder contains:

- scan.json
- raw data folder
- processed data folder

## Rules

- Project data should be portable as one folder.
- Region data should be independent.
- Raw scan data should not be overwritten.
- Exports can be generated again from Project data.

## Status

Draft 0.1
