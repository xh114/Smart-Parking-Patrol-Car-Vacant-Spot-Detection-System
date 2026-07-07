# Cleanup Recommendations For The Original Project

## Keep

- real ROS2 source packages
- launch files
- config files
- message definitions
- hardware vendor zip archives
- useful exported PDF or graph references

## Remove Or Ignore In Version Control

- `build/`
- `install/`
- `log/`
- `__pycache__/`
- `*.pyc`
- nested dependency `.git/` directories copied into the project

## Duplicate Packages Found

The following packages exist in both the driver area and the mapping area:

- `car_control`
- `car_control_msgs`
- `car_odometry`

Recommended choice:

- keep the copies from `car_mapping/car_mapping/src`
- remove or archive the duplicate copies under `car_driver/car_control/src`

Reason:

- the `car_mapping` copies are closer to the current integrated workflow
- `car_control` there adds tighter polling and configurable serial timeout
- `car_odometry` there defaults `publish_tf` to `false`, which matches EKF fusion ownership better

## Suggested Final Project Root On Your Desktop

```text
Project/
├─ docs/
├─ ros2_ws/
│  └─ src/
│     ├─ chassis/
│     ├─ localization/
│     ├─ perception/
│     └─ mapping/
├─ hardware_archives/
├─ reference_outputs/
└─ scripts/
```

If you want to fully migrate the original desktop project later, use the standardized copy in this output folder as the reference source of truth.
