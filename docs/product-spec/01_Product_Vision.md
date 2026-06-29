# 01 Product Vision

## Product Name

Near Field Scanner Professional.

## Positioning

NFS Scanner Professional is an enterprise near-field scanning platform for PCB EMC testing.

It is not only a device control program or a heatmap viewer. It is a complete workflow platform for project management, device setup, region scanning, data analysis, and report generation.

## Core Workflow

```text
Project
  -> Devices
  -> Sample
  -> Region
  -> Scan
  -> Analysis
  -> Report
```

## Design Principles

- One page should focus on one job.
- Project represents one PCB or one tested object.
- Region represents one scan area on the PCB.
- Motion and spectrum devices are required for scanning.
- Camera is optional and should not block scanning.
- Hx and Hy are separate probe channels.
