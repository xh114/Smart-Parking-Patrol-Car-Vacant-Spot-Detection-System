# Project Logic Table

## 1. Module Layout

| Layer | Folder | Package / Asset | Role | Main Inputs | Main Outputs |
|---|---|---|---|---|---|
| Chassis | `02_ros2_ws/src/chassis` | `car_control` | Host-side serial communication with the ELF2/STM32 control board | serial device | `/car_feedback`, `/car_status` |
| Chassis | `02_ros2_ws/src/chassis` | `car_control_msgs` | Custom chassis feedback message definition | none | `CarFeedback.msg` |
| Chassis | `02_ros2_ws/src/chassis` | `car_odometry` | Wheel odometry integration and optional `odom -> base_link` TF | `/car_feedback` | `/odom`, optional TF |
| Localization | `02_ros2_ws/src/localization/imu` | `serial_ros2` | Serial dependency used by IMU driver | serial stream | library support |
| Localization | `02_ros2_ws/src/localization/imu` | `yesense_interface` | Custom IMU-related message definitions | none | IMU message types |
| Localization | `02_ros2_ws/src/localization/imu` | `yesense_std_ros2` | Yesense IMU ROS2 driver | IMU serial data | IMU topics |
| Localization | `02_ros2_ws/src/localization` | `robot_localization` (`car_robot_localization`) | Starts IMU + odom fusion through EKF | `/odom`, `/imu/data_raw` | fused `odom -> base_link` TF |
| Perception | `02_ros2_ws/src/perception/lidar` | `lidar` | VLP-16 UDP lidar driver, point cloud publisher | UDP 2368 packets | `/velodyne_points` |
| Perception | `02_ros2_ws/src/perception/lidar` | `parking_robot_scan` | Converts point cloud to 2D scan | `/velodyne_points` | `/scan` |
| Mapping | `02_ros2_ws/src/mapping` | `car_slam_toolbox` | SLAM startup package with delayed bringup | `/scan`, `/odom`, TF | `/map`, `map -> odom` TF |
| Hardware archive | `03_hardware_archives` | `cam.zip`, `imu.zip`, `lidar_stack.zip` | Vendor SDK / backup materials | none | reference only |
| Reference output | `04_reference_outputs` | `frames_*.gv`, `frames_*.pdf` | Existing graph and exported reference files | none | reference only |

## 2. Runtime Data Flow

| Step | Source | Target | Meaning |
|---|---|---|---|
| 1 | ELF2/STM32 board | `car_control` | Chassis controller sends wheel speed and state feedback over serial |
| 2 | `car_control` | `/car_feedback` | Parsed chassis feedback is published as `CarFeedback` |
| 3 | `car_odometry` | `/odom` | Wheel feedback is integrated into wheel odometry |
| 4 | `yesense_std_ros2` | `/imu/data_raw` and related IMU topics | IMU publishes inertial data |
| 5 | `car_robot_localization` | fused `odom -> base_link` TF | EKF fuses wheel odom and IMU after delayed startup |
| 6 | `lidar` | `/velodyne_points` | VLP-16 packets are converted into point cloud |
| 7 | `parking_robot_scan` | `/scan` | Point cloud is projected to a 2D laser scan |
| 8 | `car_slam_toolbox` | `/map`, `map -> odom` TF | SLAM consumes scan and fused odom to build map |

## 3. Recommended Launch Order

| Order | Command | Purpose |
|---|---|---|
| 1 | `ros2 launch car_robot_localization fusion_odom.launch.py` | Start IMU, wheel odom chain, and delayed EKF fusion |
| 2 | `ros2 launch parking_robot_scan parking_robot_scan.launch.py` | Start lidar driver and publish `/scan` |
| 3 | `ros2 launch car_slam_toolbox car_slam.launch.py` | Start SLAM after odom TF and scan are available |

## 4. Main Structural Problems Found In The Original Project

| Problem | Current Situation | Recommended Handling |
|---|---|---|
| Duplicate source packages | `car_control`, `car_control_msgs`, `car_odometry` appear in both `car_driver` and `car_mapping` | Keep one source line only, preferably the newer set now placed in `02_ros2_ws/src/chassis` |
| Build artifacts mixed into source tree | `build/`, `install/`, `log/`, `__pycache__/`, `.pyc` exist inside project source | Remove from source tree and regenerate only during build |
| Third-party package nested with its own `.git` | `serial_ros2` carries an embedded git repo and generated files | Keep only usable source files; remove nested repo metadata from delivery version |
| Hardware archives mixed near code | `cam.zip`, `imu.zip`, `lidar_stack.zip` are mixed into the main project root area | Move to dedicated hardware archive folder |
| Reference exports mixed near workspace | `frames_*.gv` and `frames_*.pdf` sit beside ROS2 code | Move to a reference output folder |

## 5. Recommended Long-Term Rules

- Only keep editable source code under `02_ros2_ws/src`.
- Never commit `build/`, `install/`, `log/`, `__pycache__/`, or `.pyc`.
- Keep third-party vendor archives and SDKs under `03_hardware_archives`.
- Put runtime screenshots, PDFs, graphs, and exported artifacts under `04_reference_outputs`.
- Use `01_docs` for bringup notes, topic lists, pin mapping, and competition deployment steps.
