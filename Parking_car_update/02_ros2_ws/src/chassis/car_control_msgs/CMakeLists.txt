cmake_minimum_required(VERSION 3.8)
project(car_control_msgs)

find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/CarFeedback.msg"
  DEPENDENCIES std_msgs
)


install(FILES
  resource/${PROJECT_NAME}
  DESTINATION share/ament_index/resource_index/packages
)

install(FILES
  package.xml
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
