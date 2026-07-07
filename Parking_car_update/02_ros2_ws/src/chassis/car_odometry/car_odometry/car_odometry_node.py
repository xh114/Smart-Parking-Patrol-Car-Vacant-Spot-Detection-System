import math

import rclpy
from geometry_msgs.msg import Quaternion, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster

from car_control_msgs.msg import CarFeedback


def yaw_to_quaternion(yaw: float) -> Quaternion:
    quat = Quaternion()
    quat.z = math.sin(yaw * 0.5)
    quat.w = math.cos(yaw * 0.5)
    return quat


class CarOdometryNode(Node):
    def __init__(self):
        super().__init__('car_odometry_node')

        self.declare_parameter('feedback_topic', 'car_feedback')
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('publish_tf', False)
        self.declare_parameter('use_feedback_angular_velocity', True)
        self.declare_parameter('wheel_separation', 0.36)

        self.feedback_topic = self.get_parameter('feedback_topic').value
        self.odom_topic = self.get_parameter('odom_topic').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.publish_tf = self.get_parameter('publish_tf').value
        self.use_feedback_angular_velocity = self.get_parameter('use_feedback_angular_velocity').value
        self.wheel_separation = float(self.get_parameter('wheel_separation').value)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.last_stamp = None

        self.odom_pub = self.create_publisher(Odometry, self.odom_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self) if self.publish_tf else None
        self.feedback_sub = self.create_subscription(
            CarFeedback,
            self.feedback_topic,
            self.feedback_callback,
            10,
        )

        self.get_logger().info(
            f'Subscribing to {self.feedback_topic}, publishing {self.odom_topic} '
            f'and TF {self.odom_frame} -> {self.base_frame}'
        )

    def feedback_callback(self, msg: CarFeedback):
        stamp = rclpy.time.Time.from_msg(msg.header.stamp)
        if self.last_stamp is None:
            self.last_stamp = stamp
            return

        dt = (stamp - self.last_stamp).nanoseconds * 1e-9
        self.last_stamp = stamp
        if dt <= 0.0:
            return

        linear_velocity = float(msg.linear_velocity)
        angular_velocity = self.resolve_angular_velocity(msg)

        delta_yaw = angular_velocity * dt
        heading = self.yaw + delta_yaw * 0.5
        distance = linear_velocity * dt

        self.x += distance * math.cos(heading)
        self.y += distance * math.sin(heading)
        self.yaw = math.atan2(math.sin(self.yaw + delta_yaw), math.cos(self.yaw + delta_yaw))

        self.publish_odometry(msg, linear_velocity, angular_velocity)
        if self.publish_tf:
            self.publish_transform(msg)

    def resolve_angular_velocity(self, msg: CarFeedback) -> float:
        if self.use_feedback_angular_velocity:
            return float(msg.angular_velocity)

        if self.wheel_separation <= 0.0:
            self.get_logger().warn('wheel_separation must be positive, falling back to feedback angular velocity')
            return float(msg.angular_velocity)

        return float(msg.right_wheel_velocity - msg.left_wheel_velocity) / self.wheel_separation

    def publish_odometry(self, msg: CarFeedback, linear_velocity: float, angular_velocity: float):
        odom = Odometry()
        odom.header.stamp = msg.header.stamp
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = yaw_to_quaternion(self.yaw)

        odom.twist.twist.linear.x = linear_velocity
        odom.twist.twist.angular.z = angular_velocity

        odom.pose.covariance[0] = 0.05
        odom.pose.covariance[7] = 0.05
        odom.pose.covariance[35] = 0.1
        odom.twist.covariance[0] = 0.05
        odom.twist.covariance[7] = 0.05
        odom.twist.covariance[35] = 0.1

        self.odom_pub.publish(odom)

    def publish_transform(self, msg: CarFeedback):
        transform = TransformStamped()
        transform.header.stamp = msg.header.stamp
        transform.header.frame_id = self.odom_frame
        transform.child_frame_id = self.base_frame
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0
        transform.transform.rotation = yaw_to_quaternion(self.yaw)
        self.tf_broadcaster.sendTransform(transform)


def main(args=None):
    rclpy.init(args=args)
    node = CarOdometryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
