# 06 Glossary

## Project

A Project represents one PCB or one tested object.

A Project can contain multiple Regions.

## Sample

The physical PCB or object being tested.

Sample information includes name, sample ID, version, notes, and images.

## Region

A Region is one scan area on the PCB.

Examples:

- CPU
- WiFi
- PMIC
- GNSS

Each Region has its own name, coordinates, alignment, scan settings, scans, and analysis results.

## Scan

A Scan is one acquisition task under one Region.

Hx and Hy scans are stored separately.

## Probe Channel

Probe Channel means the probe direction or polarization used for acquisition.

Supported channels:

- Hx
- Hy

## Alignment

Alignment is the mapping between the Region on the sample image and the real motion coordinates.

Alignment belongs to Region.

## Device Profile

A reusable system-level device configuration.

Examples:

- Default GRBL Motion
- Keysight Spectrum
- USB Camera

## Device Snapshot

A copy of the device configuration saved into a Project or Scan for traceability.

## Heatmap

A 2D visual result generated from scan data.

Heatmap can be shown alone or overlaid on the sample image if image alignment exists.

## Report

A generated document that summarizes Project, Region, scan result, analysis image, and conclusion.

## Status

Draft 0.1
