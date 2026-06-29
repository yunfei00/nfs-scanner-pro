# 04 Object Model

## Overview

The product is organized around the real testing workflow.

```text
System
  Device Profiles
  Projects

Project
  Sample
  Device Snapshot
  Regions
  Reports

Region
  Alignment
  Scan Configuration
  Scan Hx
  Scan Hy
  Analysis
  Export
```

## Definitions

### Project

One Project represents one PCB or one tested object.

### Region

One Region represents one scan area on the PCB. A Project can contain multiple Regions such as CPU, WiFi, PMIC, or GNSS.

### Scan

One Scan represents one acquisition task under one Region. Hx and Hy scans are stored separately.

### Alignment

Alignment belongs to Region, not Project. The PCB photo can belong to Project, but the rectangle, coordinates, and transform belong to each Region.

### Device Profile

Device Profile is a system-level reusable device configuration.

### Device Snapshot

Device Snapshot is the device configuration captured inside a Project for traceability.
