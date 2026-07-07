from setuptools import setup
from glob import glob

package_name = 'car_odometry'


setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name+'/launch',glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='noah',
    maintainer_email='noah@todo.todo',
    description='ROS2 odometry publisher for the car feedback topic.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'car_odometry_node = car_odometry.car_odometry_node:main',
        ],
    },
)
