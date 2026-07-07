import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    slam_start_delay = LaunchConfiguration('slam_start_delay')

    default_params_file = os.path.join(
        get_package_share_directory('car_slam_toolbox'),
        'config',
        'mapper_params_online_async.yaml'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true.'
        ),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=default_params_file,
            description='Full path to the slam_toolbox parameter file.'
        ),
        DeclareLaunchArgument(
            'slam_start_delay',
            default_value='12.0',
            description='Delay slam_toolbox until the odom TF and scan topic are available.'
        ),
        TimerAction(
            period=slam_start_delay,
            actions=[
                Node(
                    package='slam_toolbox',
                    executable='async_slam_toolbox_node',
                    name='slam_toolbox',
                    output='screen',
                    parameters=[
                        slam_params_file,
                        {'use_sim_time': use_sim_time},
                    ],
                ),
            ],
        ),
    ])
