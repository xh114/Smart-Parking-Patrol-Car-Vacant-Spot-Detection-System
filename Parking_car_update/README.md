# Project Standardized

This folder is a standardized copy of the original embedded car project.

Goal:
- keep the original desktop project untouched
- separate source code, hardware archives, reference outputs, and docs
- remove build artifacts from the copied source tree
- make module ownership and startup flow easier to understand

Recommended top-level layout:

```text
Project_standardized/
├─ 01_docs/                  # project docs, logic tables, maintenance notes
├─ 02_ros2_ws/               # ROS2 workspace source tree
│  └─ src/
│     ├─ chassis/            # car chassis control and wheel odometry
│     ├─ localization/       # IMU and odom fusion
│     ├─ perception/         # raw sensor drivers and point cloud processing
│     └─ mapping/            # SLAM bringup and map generation
├─ 03_hardware_archives/     # camera / imu / lidar vendor archives
├─ 04_reference_outputs/     # existing PDFs, graphs, exported references
└─ 05_cleanup_notes/         # duplicate-source and cleanup guidance
```

Notes:
- `build/`, `install/`, `log/`, `__pycache__/`, and nested `.git/` are removed from this standardized copy.
- The more up-to-date chassis packages were taken from `car_mapping/car_mapping/src` because they match the IMU fusion launch flow better.
- The original project contains duplicate packages under both `car_driver` and `car_mapping`; this copy keeps one clearer source line.
