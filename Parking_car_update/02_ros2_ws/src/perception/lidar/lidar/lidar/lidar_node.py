import socket
import struct
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header

# VLP-16 vertical angles from the datasheet, ordered by laser id.
VERTICAL_ANGLES = np.array([
    -15.0, 1.0, -13.0, 3.0, -11.0, 5.0, -9.0, 7.0,
    -7.0, 9.0, -5.0, 11.0, -3.0, 13.0, -1.0, 15.0,
], dtype=np.float32)
VERTICAL_ANGLES_RAD = np.radians(VERTICAL_ANGLES)
VERTICAL_CORR_M = np.array([
    11.2, -0.7, 9.7, -2.2, 8.1, -3.7, 6.6, -5.1,
    5.1, -6.6, 3.7, -8.1, 2.2, -9.7, 0.7, -11.2,
], dtype=np.float32) / 1000.0

DATA_PORT = 2368
# Velodyne UDP payload is 1206 bytes: 12 data blocks (1200) + timestamp/factory bytes (6).
PACKET_LEN = 1206
BLOCKS_PER_PACKET = 12
BLOCK_LEN = 100
POINTS_PER_BLOCK = 32
RANGE_RESOLUTION_M = 0.002


class VLP16Listener(Node):
    def __init__(self):
        super().__init__('lidar_node')

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.publisher_ = self.create_publisher(PointCloud2, 'velodyne_points', sensor_qos)

        self.declare_parameter('frame_id', 'laser_link')
        self.declare_parameter('bind_address', '0.0.0.0')
        self.declare_parameter('data_port', DATA_PORT)
        self.declare_parameter('socket_timeout_sec', 1.0)
        self.declare_parameter('publish_period_sec', 0.1)
        self.declare_parameter('max_packets_per_publish', 180)
        self.declare_parameter('debug_interval_sec', 2.0)

        self.frame_id = self.get_parameter('frame_id').value
        bind_address = self.get_parameter('bind_address').value
        data_port = int(self.get_parameter('data_port').value)
        socket_timeout_sec = float(self.get_parameter('socket_timeout_sec').value)
        publish_period_sec = float(self.get_parameter('publish_period_sec').value)
        self.max_packets_per_publish = int(self.get_parameter('max_packets_per_publish').value)
        self.debug_interval_sec = float(self.get_parameter('debug_interval_sec').value)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((bind_address, data_port))
        self.sock.settimeout(socket_timeout_sec)
        self.sock.setblocking(False)

        self.timer = self.create_timer(publish_period_sec, self.timer_callback)
        self.last_debug_time = time.monotonic()
        self.total_packets = 0
        self.total_points = 0

        self.get_logger().info(
            'VLP-16 node started. '
            f'Listening on {bind_address}:{data_port}, frame_id={self.frame_id}, '
            f'publish_period={publish_period_sec:.3f}s, max_packets_per_publish={self.max_packets_per_publish}'
        )

    def create_point_cloud2(self, points: np.ndarray) -> PointCloud2:
        msg = PointCloud2()
        header = Header()
        header.frame_id = self.frame_id
        header.stamp = self.get_clock().now().to_msg()
        msg.header = header
        msg.height = 1
        msg.width = int(points.shape[0])
        msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = False
        msg.data = np.asarray(points, dtype=np.float32).tobytes()
        return msg

    def parse_vlp16_packet(self, data: bytes) -> np.ndarray:
        points = []
        for i in range(BLOCKS_PER_PACKET):
            block = data[i * BLOCK_LEN:(i + 1) * BLOCK_LEN]
            if len(block) != BLOCK_LEN:
                continue

            flag = struct.unpack_from('<H', block, 0)[0]
            if flag != 0xEEFF:
                continue

            azi_raw = struct.unpack_from('<H', block, 2)[0]
            azi_rad = np.radians(azi_raw / 100.0)

            for j in range(POINTS_PER_BLOCK):
                offset = 4 + j * 3
                dist_raw, intensity = struct.unpack_from('<HB', block, offset)
                if dist_raw == 0:
                    continue

                dist = dist_raw * RANGE_RESOLUTION_M
                laser_id = j % 16
                omega = VERTICAL_ANGLES_RAD[laser_id]

                x = -dist * np.cos(omega) * np.sin(azi_rad)
                y = -dist * np.cos(omega) * np.cos(azi_rad)
                z = dist * np.sin(omega) + VERTICAL_CORR_M[laser_id]
                points.append((x, y, z, intensity / 255.0))

        if not points:
            return np.empty((0, 4), dtype=np.float32)
        return np.array(points, dtype=np.float32)

    def timer_callback(self) -> None:
        try:
            packet_count = 0
            packet_points = []

            while packet_count < self.max_packets_per_publish:
                try:
                    data, _ = self.sock.recvfrom(2048)
                except BlockingIOError:
                    break

                if len(data) != PACKET_LEN:
                    self.get_logger().debug(f'Unexpected packet length: {len(data)}')
                    continue

                points = self.parse_vlp16_packet(data)
                packet_count += 1
                if points.size != 0:
                    packet_points.append(points)

            if packet_count == 0:
                return

            merged_points = np.concatenate(packet_points, axis=0) if packet_points else np.empty((0, 4), dtype=np.float32)
            if merged_points.size == 0:
                return

            self.publisher_.publish(self.create_point_cloud2(merged_points))
            self.total_packets += packet_count
            self.total_points += int(merged_points.shape[0])
            self._maybe_log_debug(packet_count, int(merged_points.shape[0]))
        except socket.timeout:
            self.get_logger().warn('No lidar packet received. Check radar IP, cable, and firewall settings.')
        except Exception as exc:  # pragma: no cover - defensive runtime logging.
            self.get_logger().error(f'Failed to parse lidar packet: {exc}')

    def _maybe_log_debug(self, packet_count: int, point_count: int) -> None:
        now = time.monotonic()
        if now - self.last_debug_time < self.debug_interval_sec:
            return

        self.get_logger().info(
            'lidar stats: '
            f'packets_this_publish={packet_count}, '
            f'points_this_publish={point_count}, '
            f'total_packets={self.total_packets}, '
            f'total_points={self.total_points}'
        )
        self.last_debug_time = now

    def destroy_node(self):
        try:
            self.sock.close()
        finally:
            super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VLP16Listener()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
