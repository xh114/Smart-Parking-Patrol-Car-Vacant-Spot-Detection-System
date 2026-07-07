from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    publish_odom_tf = LaunchConfiguration('publish_odom_tf')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true.'
        ),
        DeclareLaunchArgument(
            'publish_odom_tf',
            default_value='false',
            description='Publish odom to base_link TF from car_odometry.'
        ),

        Node(
            package='car_control',
            executable='car_control_node',
            name='car_control_node',
            output='screen',
        ),
        Node(
            package='car_odometry',
            executable='car_odometry_node',
            name='car_odometry_node',
            output='screen',
            parameters=[{
                'publish_tf': publish_odom_tf,
            }],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_laser_link',
            arguments=[
                '--x', '-0.20165',
                '--y', '0.0',
                '--z', '0.1377',
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                '--frame-id', 'base_link',
                '--child-frame-id', 'laser_link',
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_imu_link',
            arguments=[
                '--x', '-0.197',
                '--y', '-0.12',
                '--z', '0.1117',
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                '--frame-id', 'base_link',
                '--child-frame-id', 'imu_link',
            ],
        ),
    ])