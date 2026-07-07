import math
import struct
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan, PointCloud2, PointField
from std_msgs.msg import Header


DATATYPE_MAP = {
    PointField.INT8: ('b', 1),
    PointField.UINT8: ('B', 1),
    PointField.INT16: ('h', 2),
    PointField.UINT16: ('H', 2),
    PointField.INT32: ('i', 4),
    PointField.UINT32: ('I', 4),
    PointField.FLOAT32: ('f', 4),
    PointField.FLOAT64: ('d', 8),
}


class PointCloudToLaserScan(Node):
    def __init__(self):
        super().__init__('parking_robot_scan')

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.declare_parameter('input_topic', '/velodyne_points')
        self.declare_parameter('output_topic', '/scan')
        self.declare_parameter('target_frame', '')
        self.declare_parameter('min_height', -0.20)
        self.declare_parameter('max_height', 0.30)
        self.declare_parameter('min_range', 0.35)
        self.declare_parameter('max_range', 20.0)
        self.declare_parameter('angle_min', -math.pi)
        self.declare_parameter('angle_max', math.pi)
        self.declare_parameter('angle_increment', math.radians(0.5))
        self.declare_parameter('scan_time', 0.1)
        self.declare_parameter('use_inf', True)
        self.declare_parameter('inf_epsilon', 1.0)
        self.declare_parameter('debug_interval_sec', 2.0)

        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.target_frame = self.get_parameter('target_frame').value
        self.min_height = float(self.get_parameter('min_height').value)
        self.max_height = float(self.get_parameter('max_height').value)
        self.min_range = float(self.get_parameter('min_range').value)
        self.max_range = float(self.get_parameter('max_range').value)
        self.angle_min = float(self.get_parameter('angle_min').value)
        self.angle_max = float(self.get_parameter('angle_max').value)
        self.angle_increment = float(self.get_parameter('angle_increment').value)
        self.scan_time = float(self.get_parameter('scan_time').value)
        self.use_inf = bool(self.get_parameter('use_inf').value)
        self.inf_epsilon = float(self.get_parameter('inf_epsilon').value)
        self.debug_interval_sec = float(self.get_parameter('debug_interval_sec').value)

        if self.angle_increment <= 0.0:
            raise ValueError('angle_increment must be positive')
        if self.angle_max <= self.angle_min:
            raise ValueError('angle_max must be larger than angle_min')

        self.ranges_size = int(math.ceil((self.angle_max - self.angle_min) / self.angle_increment))
        self.last_debug_time = time.monotonic()
        self.stats = self._new_stats()

        self.subscription = self.create_subscription(
            PointCloud2,
            self.input_topic,
            self.pointcloud_callback,
            sensor_qos,
        )
        self.publisher = self.create_publisher(LaserScan, self.output_topic, sensor_qos)

        self.get_logger().info(
            'parking_robot_scan started. '
            f'{self.input_topic} -> {self.output_topic}, '
            f'height=[{self.min_height:.2f}, {self.max_height:.2f}] m, '
            f'range=[{self.min_range:.2f}, {self.max_range:.2f}] m'
        )

    def pointcloud_callback(self, msg: PointCloud2) -> None:
        field_offsets = {field.name: field for field in msg.fields}
        required_fields = ('x', 'y', 'z')
        if any(name not in field_offsets for name in required_fields):
            self.get_logger().error('PointCloud2 is missing one of the required fields: x, y, z')
            return

        current_ranges = self._new_ranges()
        self.stats = self._new_stats()

        x_field = field_offsets['x']
        y_field = field_offsets['y']
        z_field = field_offsets['z']

        x_fmt = self._field_format(x_field)
        y_fmt = self._field_format(y_field)
        z_fmt = self._field_format(z_field)

        little_endian = '<' if not msg.is_bigendian else '>'
        local_bins_filled = 0

        for point in self._iter_points(msg):
            self.stats['input_points'] += 1
            x = struct.unpack_from(little_endian + x_fmt, point, x_field.offset)[0]
            y = struct.unpack_from(little_endian + y_fmt, point, y_field.offset)[0]
            z = struct.unpack_from(little_endian + z_fmt, point, z_field.offset)[0]

            if not math.isfinite(x) or not math.isfinite(y) or not math.isfinite(z):
                continue
            self.stats['finite_points'] += 1
            self.stats['z_min'] = min(self.stats['z_min'], z)
            self.stats['z_max'] = max(self.stats['z_max'], z)
            if z < self.min_height or z > self.max_height:
                continue
            self.stats['height_kept'] += 1

            range_xy = math.hypot(x, y)
            if range_xy < self.min_range or range_xy > self.max_range:
                continue
            self.stats['range_kept'] += 1

            angle = math.atan2(y, x)
            if angle < self.angle_min or angle >= self.angle_max:
                continue
            self.stats['angle_kept'] += 1

            index = int((angle - self.angle_min) / self.angle_increment)
            if 0 <= index < self.ranges_size and range_xy < current_ranges[index]:
                if not math.isfinite(current_ranges[index]):
                    local_bins_filled += 1
                current_ranges[index] = range_xy

        self.stats['filled_bins'] = local_bins_filled
        self.publish_scan(msg.header, current_ranges)

    def publish_scan(self, header, ranges) -> None:
        scan = LaserScan()
        if header is None:
            scan.header = Header()
            scan.header.stamp = self.get_clock().now().to_msg()
            scan.header.frame_id = self.target_frame
        else:
            scan.header = header
            if self.target_frame:
                scan.header.frame_id = self.target_frame

        scan.angle_min = self.angle_min
        scan.angle_max = self.angle_max
        scan.angle_increment = self.angle_increment
        scan.scan_time = self.scan_time
        scan.time_increment = self.scan_time / max(1, self.ranges_size)
        scan.range_min = self.min_range
        scan.range_max = self.max_range
        scan.ranges = list(ranges)

        self.publisher.publish(scan)
        self._maybe_log_debug()

    def _new_ranges(self):
        default_range = math.inf if self.use_inf else (self.max_range + self.inf_epsilon)
        return [default_range] * self.ranges_size

    def _new_stats(self):
        return {
            'input_points': 0,
            'finite_points': 0,
            'height_kept': 0,
            'range_kept': 0,
            'angle_kept': 0,
            'filled_bins': 0,
            'z_min': math.inf,
            'z_max': -math.inf,
        }

    def _maybe_log_debug(self) -> None:
        now = time.monotonic()
        if now - self.last_debug_time < self.debug_interval_sec:
            return

        z_text = 'n/a'
        if math.isfinite(self.stats['z_min']) and math.isfinite(self.stats['z_max']):
            z_text = f"[{self.stats['z_min']:.2f}, {self.stats['z_max']:.2f}]"

        self.get_logger().info(
            'scan stats: '
            f"input={self.stats['input_points']}, "
            f"finite={self.stats['finite_points']}, "
            f"height_kept={self.stats['height_kept']}, "
            f"range_kept={self.stats['range_kept']}, "
            f"angle_kept={self.stats['angle_kept']}, "
            f"filled_bins={self.stats['filled_bins']}, "
            f'z_range={z_text}'
        )
        if self.stats['angle_kept'] == 0 and self.stats['finite_points'] > 0:
            self.get_logger().warn(
                'No points survived projection. '
                'First check min_height/max_height and whether the lidar frame is level.'
            )
        self.last_debug_time = now

    def _iter_points(self, msg: PointCloud2):
        total_points = msg.width * msg.height
        for index in range(total_points):
            start = index * msg.point_step
            end = start + msg.point_step
            yield msg.data[start:end]

    def _field_format(self, field: PointField) -> str:
        datatype = DATATYPE_MAP.get(field.datatype)
        if datatype is None:
            raise ValueError(f'Unsupported PointField datatype: {field.datatype}')
        fmt, _ = datatype
        if field.count != 1:
            raise ValueError(f'Field {field.name} count={field.count} is not supported')
        return fmt


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudToLaserScan()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()