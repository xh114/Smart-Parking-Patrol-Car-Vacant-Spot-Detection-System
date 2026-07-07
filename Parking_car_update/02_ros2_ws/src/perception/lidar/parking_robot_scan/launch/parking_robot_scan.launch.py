from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    rviz_config = PathJoinSubstitution([
        FindPackageShare('parking_robot_scan'),
        'config',
        'parking_robot_scan.rviz',
    ])

    lidar_node = Node(
        package='lidar',
        executable='lidar_node',
        name='lidar_node',
        output='screen',
        parameters=[{
            'frame_id': 'laser_link',
            'bind_address': '0.0.0.0',
            'data_port': 2368,
            'publish_period_sec': 0.1,
            'max_packets_per_publish': 120,
        }],
    )

    scan_node = Node(
        package='parking_robot_scan',
        executable='pointcloud_to_scan',
        name='parking_robot_scan',
        output='screen',
        parameters=[{
            'input_topic': '/velodyne_points',
            'output_topic': '/scan',
            'target_frame': 'laser_link',
            'min_height': -0.20,
            'max_height': 0.20,
            'min_range': 0.8,
            'max_range': 5.0,
            'angle_min': -3.141592653589793,
            'angle_max': 3.141592653589793,
            'angle_increment': 0.008726646259971648,
            'scan_time': 0.1,
            'use_inf': True,
            'inf_epsilon': 1.0,
            'debug_interval_sec': 2.0,
        }],
    )

    # rviz_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     output='screen',
    #     arguments=['-d', rviz_config],
    # )

    return LaunchDescription([
        lidar_node,
        scan_node,
        # rviz_node,
    ])
