from setuptools import setup

package_name = 'car_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['pyserial'],
    zip_safe=True,
    maintainer='noah',
    maintainer_email='noah@todo.todo',
    description='ROS2 node for STM32 motor drive host serial interface.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'car_control_node = car_control.car_control_node:main',
        ],
    },
)
