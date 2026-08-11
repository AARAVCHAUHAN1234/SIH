# Garuda Kavach

Garuda Kavach is an AI-powered bridge inspection and Digital Twin platform.

The platform processes bridge imagery, detects visible structural defects,
reconstructs bridge geometry, maps defects into 3D space, and provides
inspection intelligence.

## Architecture

```text
Bridge Photos / Videos
        |
        v
Media Processing
        |
        v
AI Defect Detection
        |
        v
3D Reconstruction
        |
        v
Digital Twin
        |
        v
Defect Mapping
        |
        v
Inspection Intelligence
        |
        v
Inspection Report
        |
        v
PX4 + Gazebo Simulation