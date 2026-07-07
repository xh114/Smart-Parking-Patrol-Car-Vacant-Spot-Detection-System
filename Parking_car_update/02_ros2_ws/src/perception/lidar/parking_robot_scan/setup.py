from setuptools import find_packages, setup

package_name = 'parking_robot_scan'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/parking_robot_scan.launch.py']),
        ('share/' + package_name + '/config', ['config/parking_robot_scan.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='elf',
    maintainer_email='elf@todo.todo',
    description='Convert VLP-16 point clouds into 2D LaserScan for parking robot use.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'pointcloud_to_scan = parking_robot_scan.pointcloud_to_scan:main',
        ],
    },
)
