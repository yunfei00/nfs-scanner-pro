# 03 Devices

## Page Purpose

Devices page manages device connection and device profiles.

## Device Types

Required devices:

- Motion Controller
- Spectrum Analyzer

Optional devices:

- Camera
- Probe Servo

## User Goals

- Select a Device Profile.
- Connect required devices.
- Check device status.
- Test simple device actions.
- Save working settings as a Device Profile.

## Motion Controller

Motion section should support:

- Port selection
- Baudrate
- Connect and disconnect
- Home
- Query position
- Manual movement

## Spectrum Analyzer

Spectrum section should support:

- Device type
- Connection address
- Connect and disconnect
- Read device information
- Single sweep test

## Camera

Camera section is optional.

Camera section should support:

- Camera type
- Camera index or address
- Preview
- Capture test image

## Probe Servo

Probe Servo controls probe channel switching between Hx and Hy.

It should support:

- Hx position
- Hy position
- Test rotate
- Offset calibration

## Rules

- Motion and Spectrum must be ready before scanning.
- Camera is optional.
- Probe Servo can be replaced by manual probe setting.

## Status

Draft 0.1
