# 05 Navigation

## Navigation Principle

The product navigation should follow the real test workflow.

The user should not see all controls on one page. Each page should focus on one job.

## Main Pages

The first commercial version uses these main pages:

1. Dashboard
2. Projects
3. Devices
4. Sample
5. Regions
6. Scan
7. Analysis
8. Reports
9. Settings

## Page Responsibilities

### Dashboard

Shows recent Projects, device status summary, recent scans, and product status.

### Projects

Creates, opens, copies, archives, and manages Projects.

### Devices

Manages Motion Controller, Spectrum Analyzer, Camera, and Probe Servo.

### Sample

Manages the PCB sample information and sample image.

### Regions

Creates and manages scan Regions on the PCB.

### Scan

Runs scan tasks for the selected Region and probe channel.

### Analysis

Views heatmaps, spectrum data, comparisons, and analysis results.

### Reports

Creates and exports test reports.

### Settings

Manages system settings, device profiles, license, theme, and paths.

## Navigation Rules

- Project must be selected before Region and Scan.
- Devices should be checked before Scan.
- Region must be selected before Scan.
- Analysis depends on scan data.
- Reports depend on analysis results.

## Status

Draft 0.1
