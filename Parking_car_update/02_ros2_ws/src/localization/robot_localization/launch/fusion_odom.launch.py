import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    ekf_params_file = LaunchConfiguration('ekf_params_file')

    default_params_file = os.path.join(
        get_package_share_directory('car_robot_localization'),
        'config',
        'ekf_odom.yaml'
    )
    bringup_launch = os.path.join(
        get_package_share_directory('car_odometry'),
        'launch',
        'car_bringup.launch.py'
    )
    imu_launch = os.path.join(
        get_package_share_directory('yesense_std_ros2'),
        'launch',
        'yesense_node.launch.py'
    )

    delayed_ekf = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='robot_localization',
                executable='ekf_node',
                name='ekf_filter_node',
                output='screen',
                parameters=[
                    ekf_params_file,
                    {'use_sim_time': use_sim_time},
                ],
            ),
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true.'
        ),
        DeclareLaunchArgument(
            'ekf_params_file',
            default_value=default_params_file,
            description='Full path to the EKF parameter file.'
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(imu_launch),
            launch_arguments={
                'use_sim_time': use_sim_time,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(bringup_launch),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'publish_odom_tf': 'false',
            }.items(),
        ),
        delayed_ekf,
    ])
