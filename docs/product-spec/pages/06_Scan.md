# 06 Scan

## Page Purpose

Scan page runs acquisition tasks for the selected Region.

## User Goals

- Select Region.
- Select probe channel.
- Configure scan parameters.
- Preview scan path.
- Start, pause, resume, or stop scan.
- Watch progress.
- Generate live heatmap when possible.

## Scan Preconditions

Before scan:

- Project is selected.
- Region is selected.
- Motion Controller is ready.
- Spectrum Analyzer is ready.
- Start point and end point are saved.
- Scan parameters are valid.

## Probe Channels

Supported modes:

- Hx only
- Hy only
- Hx plus Hy

Recommended first version:

- scan full Region in Hx
- then scan full Region in Hy

Do not switch Hx and Hy at every point in the first commercial version.

## Parameters

Scan page should include:

- X step
- Y step
- Z height
- Speed
- Dwell time
- Frequency settings
- Trace selection
- Snake mode

## Progress

Progress should show:

- Current point
- Total points
- Current coordinate
- Elapsed time
- Estimated remaining time
- Current channel

## Status

Draft 0.1
