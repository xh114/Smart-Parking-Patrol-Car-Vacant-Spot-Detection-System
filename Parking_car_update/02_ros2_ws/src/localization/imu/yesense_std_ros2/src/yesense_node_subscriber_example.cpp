#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "yesense_interface/msg/imu_data.hpp"
#include "yesense_interface/msg/euler_only.hpp"
#include "yesense_interface/msg/attitude_min_vru.hpp"
#include "yesense_interface/msg/nav_min.hpp"

using std::placeholders::_1;

class YESENSE_Subscriber : public rclcpp::Node
{
public:
    YESENSE_Subscriber()
    : Node("yesense_subscriber")
    {
        sub_imu_data = this->create_subscription<yesense_interface::msg::ImuData>(
            "imu_data", 10, std::bind(&YESENSE_Subscriber::topic_callback_imu_data, this, _1));
        sub_euler_only = this->create_subscription<yesense_interface::msg::EulerOnly>(
            "euler_only", 10, std::bind(&YESENSE_Subscriber::topic_callback_euler_only, this, _1));
        sub_att_min_vru = this->create_subscription<yesense_interface::msg::AttitudeMinVru>(
            "att_min_vru", 10, std::bind(&YESENSE_Subscriber::topic_callback_att_min_vru, this, _1));
        sub_nav_min = this->create_subscription<yesense_interface::msg::NavMin>(
            "nav_min", 10, std::bind(&YESENSE_Subscriber::topic_callback_nav_min, this, _1));

        // [ADDED] Watch the command response topic so manual yaw-reset debugging is visible in one terminal.
        sub_cmd_resp_ = this->create_subscription<std_msgs::msg::String>(
            "/yesense/cmd_resp", 10, std::bind(&YESENSE_Subscriber::topic_callback_cmd_resp, this, _1));

        // [ADDED] Optional helper publisher: set parameter command_once to send one command after startup.
        this->declare_parameter<std::string>("command_once", "");
        this->declare_parameter<int>("command_delay_ms", 1000);
        this->get_parameter("command_once", command_once_);
        this->get_parameter("command_delay_ms", command_delay_ms_);
        pub_cmd_ = this->create_publisher<std_msgs::msg::String>("/yesense/cmd", 10);

        if (!command_once_.empty())
        {
            timer_send_once_ = this->create_wall_timer(
                std::chrono::milliseconds(command_delay_ms_),
                std::bind(&YESENSE_Subscriber::publish_command_once, this));
        }
    }

private:
    void topic_callback_imu_data(const yesense_interface::msg::ImuData::SharedPtr msg) const
    {
        RCLCPP_INFO(this->get_logger(), "I heard imu data: '%u, %f, %f, %f, %f, %f, %f, %f, %u'",
            (unsigned int)msg->tid.tid, msg->acc.x, msg->acc.y, msg->acc.z,
            msg->gyro.x, msg->gyro.y, msg->gyro.z, msg->temp.temp, msg->sample_timestamp.timestamp);
    }

    void topic_callback_euler_only(const yesense_interface::msg::EulerOnly::SharedPtr msg) const
    {
        // [MODIFIED] This yaw is now the software-zeroed yaw after reset_yaw/reset_heading.
        RCLCPP_INFO(this->get_logger(), "I heard euler data: '%u, %f, %f, %f'",
            (unsigned int)msg->tid.tid, msg->euler.pitch, msg->euler.roll, msg->euler.yaw);
    }

    void topic_callback_att_min_vru(const yesense_interface::msg::AttitudeMinVru::SharedPtr msg) const
    {
        RCLCPP_INFO(this->get_logger(), "I heard att min vru data: '%u, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f'",
            (unsigned int)msg->imu_basic.tid.tid, msg->imu_basic.acc.x, msg->imu_basic.acc.y, msg->imu_basic.acc.z,
            msg->imu_basic.gyro.x, msg->imu_basic.gyro.y, msg->imu_basic.gyro.z,
            msg->euler.pitch, msg->euler.roll, msg->euler.yaw, msg->imu_basic.temp.temp);
    }

    void topic_callback_nav_min(const yesense_interface::msg::NavMin::SharedPtr msg) const
    {
        RCLCPP_INFO(this->get_logger(), "I heard nav min data: '%u, %.10f, %.10f, %f, %f, %f, %f, %u, %u'",
            (unsigned int)msg->pos.tid.tid, msg->pos.pos.longitude, msg->pos.pos.latitude, msg->pos.pos.altitude,
            msg->euler.pitch, msg->euler.roll, msg->euler.yaw,
            msg->pos.status.fusion_status, msg->pos.status.gnss_status);
    }

    // [ADDED] Command execution confirmation callback.
    void topic_callback_cmd_resp(const std_msgs::msg::String::SharedPtr msg) const
    {
        // [MODIFIED] Auto-zero completion from yesense_node will also be printed here.
        RCLCPP_INFO(this->get_logger(), "cmd response: '%s'", msg->data.c_str());
    }

    // [ADDED] Small helper for people who prefer a node parameter over CLI topic publishing.
    void publish_command_once()
    {
        std_msgs::msg::String cmd_msg;
        cmd_msg.data = command_once_;
        pub_cmd_->publish(cmd_msg);
        RCLCPP_INFO(this->get_logger(), "published one-shot cmd: '%s'", cmd_msg.data.c_str());

        if (timer_send_once_)
        {
            timer_send_once_->cancel();
        }
    }

    rclcpp::Subscription<yesense_interface::msg::ImuData>::SharedPtr sub_imu_data;
    rclcpp::Subscription<yesense_interface::msg::EulerOnly>::SharedPtr sub_euler_only;
    rclcpp::Subscription<yesense_interface::msg::AttitudeMinVru>::SharedPtr sub_att_min_vru;
    rclcpp::Subscription<yesense_interface::msg::NavMin>::SharedPtr sub_nav_min;

    // [ADDED] Yaw-reset debug topics.
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_cmd_resp_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_cmd_;
    rclcpp::TimerBase::SharedPtr timer_send_once_;
    std::string command_once_;
    int command_delay_ms_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    rclcpp::spin(std::make_shared<YESENSE_Subscriber>());
    rclcpp::shutdown();

    return 0;
}
