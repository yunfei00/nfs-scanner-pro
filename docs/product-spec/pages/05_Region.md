# 05 Region

## Page Purpose

Region page manages scan areas on the PCB.

A Region is the main working unit inside a Project.

## User Goals

- Create a new Region.
- Give the Region a clear name.
- Define start point and end point.
- Save alignment data.
- View Region status.
- Select a Region before scanning.

## Region Name

Region name is required.

Good names:

- CPU
- WiFi
- PMIC
- GNSS
- USB

Avoid unnamed Region entries.

## Region Data

A Region should contain:

- Region name
- Description
- Start point
- End point
- Z height
- Alignment
- Scan configuration
- Scan history
- Analysis results

## Start and End Point Flow

The real workflow is:

1. Move probe to start point.
2. Save start point.
3. Move probe to end point.
4. Save end point.
5. Generate Region range.

## Alignment

Alignment belongs to Region.

The sample image can belong to Project, but the rectangle and coordinate mapping belong to Region.

## Status

Draft 0.1
