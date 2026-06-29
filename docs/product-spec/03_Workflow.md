# 03 Workflow

## Normal Test Flow

```text
Open or create Project
  -> Place PCB
  -> Check Motion Controller
  -> Check Spectrum Analyzer
  -> Check Camera if available
  -> Set Probe Channel Hx or Hy
  -> Create Region
  -> Move probe to start point
  -> Save start point
  -> Move probe to end point
  -> Save end point
  -> Set scan parameters
  -> Generate path preview
  -> Run scan
  -> Generate heatmap
  -> Analyze result
  -> Export report
```

## Required Devices

- Motion Controller
- Spectrum Analyzer

## Optional Devices

- Camera
- Probe Servo

Camera failure should not block scan acquisition or heatmap generation.

## Hx and Hy Flow

Recommended mode for the first commercial version:

```text
Set Hx
  -> Scan whole Region
  -> Save Hx result
  -> Set Hy
  -> Apply probe offset compensation
  -> Scan whole Region
  -> Save Hy result
  -> Generate Hx, Hy, and total result
```
