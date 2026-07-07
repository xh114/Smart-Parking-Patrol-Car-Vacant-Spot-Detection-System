import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from car_control_msgs.msg import CarFeedback

try:
    import serial
except ImportError:
    serial = None


def checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def int16_to_bytes(value: int) -> bytes:
    return value.to_bytes(2, byteorder='little', signed=True)


def bytes_to_int16(data: bytes) -> int:
    return int.from_bytes(data, byteorder='little', signed=True)


class CarControlNode(Node):
    def __init__(self):
        super().__init__('car_control_node')
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('feedback_poll_period_sec', 0.002)
        self.declare_parameter('serial_timeout_sec', 0.0)
        self.serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
        self.baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.feedback_poll_period_sec = self.get_parameter('feedback_poll_period_sec').get_parameter_value().double_value
        self.serial_timeout_sec = self.get_parameter('serial_timeout_sec').get_parameter_value().double_value

        self.feedback_pub = self.create_publisher(CarFeedback, 'car_feedback', 10)
        self.status_pub = self.create_publisher(String, 'car_status', 10)
        self.timer = self.create_timer(self.feedback_poll_period_sec, self.timer_callback)

        self.serial = None
        self.buffer = bytearray()

        if serial is None:
            self.get_logger().error('pyserial is not installed. Install with pip install pyserial.')
        else:
            self.open_serial()

    def open_serial(self):
        try:
            self.serial = serial.Serial(
                self.serial_port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.serial_timeout_sec,
            )
            self.get_logger().info(f'Opened serial port: {self.serial_port} @ {self.baudrate}')
        except Exception as exc:
            self.get_logger().error(f'Failed to open serial port {self.serial_port}: {exc}')
            self.serial = None

    def build_pns_frame(self, velocity: int, angular: int, mode: int = 1, brake: int = 0, navigation_mode: int = 0):
        payload = bytearray()
        payload.append(0x01)
        payload.append(mode)
        payload.append(brake)
        payload.append(0x00)
        payload.extend(int16_to_bytes(velocity))
        payload.extend(int16_to_bytes(angular))
        payload.append(navigation_mode)
        payload.extend((0).to_bytes(2, byteorder='little'))
        payload.extend((0).to_bytes(4, byteorder='little'))
        payload.append(0x0A)
        frame = bytearray([0xAA, 0xBB, 0xCC, len(payload) + 2])
        frame.extend(payload)
        frame.append(checksum(frame))
        return frame

    def parse_feedback(self):
        if self.serial is None or self.serial.in_waiting == 0:
            return
        try:
            data = self.serial.read(self.serial.in_waiting)
        except Exception as exc:
            self.get_logger().error(f'Serial read error: {exc}')
            return
        self.buffer.extend(data)

        while len(self.buffer) >= 5:
            if self.buffer[0:3] != b'\xAA\xBB\xCC':
                self.buffer.pop(0)
                continue
            length = self.buffer[3]
            packet_size = length + 3
            if len(self.buffer) < packet_size:
                break
            packet = self.buffer[:packet_size]
            self.buffer = self.buffer[packet_size:]
            if checksum(packet[:-1]) != packet[-1]:
                self.get_logger().warn('Invalid PNS checksum, dropping packet')
                continue
            packet_stamp = self.get_clock().now().to_msg()
            self.handle_feedback(packet, packet_stamp)

    def handle_feedback(self, packet: bytearray, stamp):
        if len(packet) < 16:
            self.get_logger().warn('Received short feedback packet')
            return

        frame_type = packet[4]
        x_speed = bytes_to_int16(packet[8:10])
        z_speed = bytes_to_int16(packet[10:12])
        svl = bytes_to_int16(packet[12:14])
        svr = bytes_to_int16(packet[14:16])

        feedback = CarFeedback()
        # MCU feedback has no source timestamp, so use the host receive time right after frame validation.
        feedback.header.stamp = stamp
        feedback.header.frame_id = 'base_link'
        feedback.linear_velocity = x_speed / 100.0
        feedback.angular_velocity = z_speed / 100.0
        feedback.left_wheel_velocity = svl / 100.0
        feedback.right_wheel_velocity = svr / 100.0
        feedback.frame_type = frame_type
        self.feedback_pub.publish(feedback)

        status = String()
        status.data = f'FB type=0x{frame_type:02X} x_speed={x_speed} z_speed={z_speed} svl={svl} svr={svr}'
        self.status_pub.publish(status)
        self.get_logger().debug(f'Published feedback: {status.data}')

    def timer_callback(self):
        self.parse_feedback()


def main(args=None):
    rclpy.init(args=args)
    node = CarControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
