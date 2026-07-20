# ROS 2 Refresher — Reference Solutions

Companion to `TASKS.md`. One valid way to solve each task — not the only way.
File paths are given relative to `ros2_ws/src/`.

A note on the capstone (Module 8): it was deliberately open-ended in
`TASKS.md`. What's below is *one* reasonable architecture, not "the"
answer — if your design differs but satisfies the acceptance check, that's a
success, not a mismatch.

---

## Module 0 — Environment & CLI warm-up

Nothing to write here — this module is entirely about running commands and
reading their output. A few things worth having confirmed for yourself:

- `ros2 doctor --report` should show no missing dependencies and a healthy
  RMW (middleware) implementation.
- `ros2 node info /turtlesim` lists `/turtle1/cmd_vel` (subscribed),
  `/turtle1/pose` (published), and services like `/spawn`, `/kill`,
  `/clear`, `/reset`.
- Publishing a `Twist` with both `linear.x` and `angular.z` nonzero traces a
  spiral because turtlesim integrates the twist directly each timestep —
  this is the same fact Module 5 leans on to drive a square by timing alone.

---

## Module 1 — Python package basics

### `practice_py/package.xml`

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>practice_py</name>
  <version>0.0.1</version>
  <description>Python practice nodes for the ROS 2 refresher exercises</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>std_srvs</depend>
  <depend>geometry_msgs</depend>
  <depend>turtlesim</depend>
  <depend>practice_interfaces</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

(`std_srvs`, `turtlesim`, and `practice_interfaces` aren't needed until later
modules — added here up front so you're not re-editing this file every
module.)

### `practice_py/setup.py`

```python
from setuptools import find_packages, setup

package_name = 'practice_py'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Python practice nodes for the ROS 2 refresher exercises',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = practice_py.talker:main',
            'listener = practice_py.listener:main',
            'speed_service_server = practice_py.speed_service_server:main',
            'patrol_action_server = practice_py.patrol_action_server:main',
            'spawner = practice_py.spawner:main',
            'battery_monitor = practice_py.battery_monitor:main',
            'mission_control = practice_py.mission_control:main',
        ],
    },
)
```

(Again, entries for later modules are listed here up front — add them as you
reach each module rather than all at once.)

### `practice_py/practice_py/talker.py`

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):

    def __init__(self):
        super().__init__('talker')
        self.declare_parameter('publish_rate', 2.0)
        rate = self.get_parameter('publish_rate').get_parameter_value().double_value

        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.counter = 0
        period = 1.0 / rate if rate > 0 else 0.5
        self.timer = self.create_timer(period, self.timer_callback)
        self.get_logger().info(f'Talker started at {rate} Hz')

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS2 #{self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### `practice_py/practice_py/listener.py`

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):

    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String, 'chatter', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Don't forget: `ros2_ws/src/practice_py/practice_py/__init__.py` (empty file) —
`ros2 pkg create` generates this for you, but it's the usual culprit if
`colcon build` succeeds yet `ros2 run` can't find your module.

---

## Module 2 — C++ package basics

### `practice_cpp/package.xml`

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>practice_cpp</name>
  <version>0.0.1</version>
  <description>C++ practice nodes for the ROS 2 refresher exercises</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>rclcpp_action</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>practice_interfaces</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <test_depend>ament_cmake_gtest</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

### `practice_cpp/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.8)
project(practice_cpp)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(practice_interfaces REQUIRED)

add_executable(talker src/talker.cpp)
ament_target_dependencies(talker rclcpp std_msgs)

add_executable(listener src/listener.cpp)
ament_target_dependencies(listener rclcpp std_msgs)

add_executable(speed_service_client src/speed_service_client.cpp)
ament_target_dependencies(speed_service_client rclcpp practice_interfaces)

add_executable(patrol_action_client src/patrol_action_client.cpp)
ament_target_dependencies(patrol_action_client rclcpp rclcpp_action practice_interfaces)

install(TARGETS
  talker
  listener
  speed_service_client
  patrol_action_client
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

### `practice_cpp/src/talker.cpp`

```cpp
#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class Talker : public rclcpp::Node
{
public:
  Talker()
  : Node("talker"), count_(0)
  {
    this->declare_parameter<double>("publish_rate", 2.0);
    double rate = this->get_parameter("publish_rate").as_double();
    auto period = std::chrono::duration<double>(1.0 / rate);

    publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);
    timer_ = this->create_wall_timer(
      std::chrono::duration_cast<std::chrono::milliseconds>(period),
      std::bind(&Talker::timer_callback, this));

    RCLCPP_INFO(this->get_logger(), "Talker started at %.2f Hz", rate);
  }

private:
  void timer_callback()
  {
    auto message = std_msgs::msg::String();
    message.data = "Hello ROS2 (cpp) #" + std::to_string(count_++);
    RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
    publisher_->publish(message);
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  size_t count_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Talker>());
  rclcpp::shutdown();
  return 0;
}
```

### `practice_cpp/src/listener.cpp`

```cpp
#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class Listener : public rclcpp::Node
{
public:
  Listener()
  : Node("listener")
  {
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "chatter", 10, std::bind(&Listener::topic_callback, this, _1));
  }

private:
  void topic_callback(const std_msgs::msg::String & msg) const
  {
    RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg.data.c_str());
  }

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Listener>());
  rclcpp::shutdown();
  return 0;
}
```

*(`speed_service_client.cpp` and `patrol_action_client.cpp` are listed under
Modules 4 and 5 below, since they depend on `practice_interfaces`.)*

---

## Module 3 — Custom interfaces

### `practice_interfaces/package.xml`

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>practice_interfaces</name>
  <version>0.0.1</version>
  <description>Custom msg/srv/action definitions for the ROS 2 refresher exercises</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <build_depend>rosidl_default_generators</build_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>

  <member_of_group>rosidl_interface_packages</member_of_group>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

### `practice_interfaces/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.8)
project(practice_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotStatus.msg"
  "srv/SetSpeed.srv"
  "action/Patrol.action"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

### `practice_interfaces/msg/RobotStatus.msg`

```
std_msgs/Header header
string robot_name
float32 battery_percent
string status
float32 x
float32 y
float32 theta
```

### `practice_interfaces/srv/SetSpeed.srv`

```
float32 speed
---
bool success
string message
```

### `practice_interfaces/action/Patrol.action`

```
# Goal
int32 laps
---
# Result
float32 total_distance
float32 elapsed_time
---
# Feedback
int32 current_lap
float32 distance_so_far
```

Verification once built:

```
ros2 interface show practice_interfaces/msg/RobotStatus
ros2 interface show practice_interfaces/srv/SetSpeed
ros2 interface show practice_interfaces/action/Patrol
```

---

## Module 4 — Services across languages

### `practice_py/practice_py/speed_service_server.py`

```python
import rclpy
from rclpy.node import Node

from practice_interfaces.srv import SetSpeed


class SpeedServiceServer(Node):

    def __init__(self):
        super().__init__('speed_service_server')
        self.srv = self.create_service(SetSpeed, 'set_speed', self.handle_set_speed)
        self.current_speed = 0.0

    def handle_set_speed(self, request, response):
        if request.speed < 0.0:
            response.success = False
            response.message = 'Speed must be non-negative'
        else:
            self.current_speed = request.speed
            response.success = True
            response.message = f'Speed set to {self.current_speed:.2f}'
            self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SpeedServiceServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### `practice_cpp/src/speed_service_client.cpp`

```cpp
#include <chrono>
#include <cstdlib>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "practice_interfaces/srv/set_speed.hpp"

using SetSpeed = practice_interfaces::srv::SetSpeed;
using namespace std::chrono_literals;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  if (argc != 2) {
    RCLCPP_INFO(
      rclcpp::get_logger("speed_service_client"),
      "Usage: speed_service_client <speed>");
    return 1;
  }

  auto node = rclcpp::Node::make_shared("speed_service_client");
  auto client = node->create_client<SetSpeed>("set_speed");

  while (!client->wait_for_service(1s)) {
    if (!rclcpp::ok()) {
      RCLCPP_ERROR(node->get_logger(), "Interrupted while waiting for service.");
      return 1;
    }
    RCLCPP_INFO(node->get_logger(), "Waiting for 'set_speed' service...");
  }

  auto request = std::make_shared<SetSpeed::Request>();
  request->speed = std::atof(argv[1]);

  auto result_future = client->async_send_request(request);
  if (rclcpp::spin_until_future_complete(node, result_future) ==
    rclcpp::FutureReturnCode::SUCCESS)
  {
    auto result = result_future.get();
    RCLCPP_INFO(
      node->get_logger(), "success: %s, message: %s",
      result->success ? "true" : "false", result->message.c_str());
  } else {
    RCLCPP_ERROR(node->get_logger(), "Service call failed");
  }

  rclcpp::shutdown();
  return 0;
}
```

Remember to add `speed_service_server` to `practice_py`'s `setup.py`
`console_scripts` (already included in the Module 1 listing above) and
`speed_service_client` to `practice_cpp`'s `CMakeLists.txt` (already included
in the Module 2 listing above) — both are shown there so you don't have to
re-edit those files a second time.

---

## Module 5 — Actions + turtlesim

### `practice_py/practice_py/patrol_action_server.py`

```python
import math
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from practice_interfaces.action import Patrol


def leg_durations(side_length, linear_speed, angular_speed):
    """Pure helper (easy to unit test in Module 7): seconds to drive one
    side, and seconds to turn 90 degrees, at the given speeds."""
    forward_duration = side_length / linear_speed
    turn_duration = (math.pi / 2) / angular_speed
    return forward_duration, turn_duration


class PatrolActionServer(Node):

    def __init__(self):
        super().__init__('patrol_action_server')

        self.declare_parameter('turtle_name', 'turtle1')
        self.turtle_name = self.get_parameter(
            'turtle_name').get_parameter_value().string_value

        self.side_length = 2.0
        self.linear_speed = 1.0
        self.angular_speed = math.pi / 2  # rad/s

        self._cb_group = ReentrantCallbackGroup()
        self._cmd_pub = self.create_publisher(
            Twist, f'/{self.turtle_name}/cmd_vel', 10)
        self._pose_sub = self.create_subscription(
            Pose, f'/{self.turtle_name}/pose', self._pose_callback, 10,
            callback_group=self._cb_group)
        self._last_pose = None
        self._distance = 0.0

        self._action_server = ActionServer(
            self,
            Patrol,
            f'/{self.turtle_name}/patrol',
            execute_callback=self._execute_callback,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback,
            callback_group=self._cb_group)

        self.get_logger().info(f'Patrol action server ready for {self.turtle_name}')

    def _pose_callback(self, msg):
        if self._last_pose is not None:
            dx = msg.x - self._last_pose.x
            dy = msg.y - self._last_pose.y
            self._distance += math.hypot(dx, dy)
        self._last_pose = msg

    def _goal_callback(self, goal_request):
        if goal_request.laps <= 0:
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    def _stop(self):
        self._cmd_pub.publish(Twist())

    def _drive_for(self, linear, angular, duration, goal_handle):
        """Publish a constant twist for `duration` seconds, bailing out
        early (and stopping) if a cancel comes in."""
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        end_time = self.get_clock().now().nanoseconds / 1e9 + duration
        while self.get_clock().now().nanoseconds / 1e9 < end_time:
            if goal_handle.is_cancel_requested:
                self._stop()
                return False
            self._cmd_pub.publish(twist)
            time.sleep(0.05)
        self._stop()
        return True

    def _make_result(self, start_time):
        result = Patrol.Result()
        result.total_distance = self._distance
        result.elapsed_time = (self.get_clock().now() - start_time).nanoseconds / 1e9
        return result

    def _execute_callback(self, goal_handle):
        laps_requested = goal_handle.request.laps
        feedback_msg = Patrol.Feedback()
        self._distance = 0.0
        start_time = self.get_clock().now()

        forward_duration, turn_duration = leg_durations(
            self.side_length, self.linear_speed, self.angular_speed)

        for lap in range(1, laps_requested + 1):
            for _ in range(4):
                if not self._drive_for(
                        self.linear_speed, 0.0, forward_duration, goal_handle):
                    goal_handle.canceled()
                    return self._make_result(start_time)
                if not self._drive_for(
                        0.0, self.angular_speed, turn_duration, goal_handle):
                    goal_handle.canceled()
                    return self._make_result(start_time)

            feedback_msg.current_lap = lap
            feedback_msg.distance_so_far = self._distance
            goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        return self._make_result(start_time)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolActionServer()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**Why `ReentrantCallbackGroup` + `MultiThreadedExecutor`:** `_execute_callback`
blocks (via `time.sleep`) for the whole patrol. With a single-threaded
executor or a `MutuallyExclusiveCallbackGroup` (the default), the pose
subscription callback would never get a chance to run while a goal is
executing, and distance would never update. Reentrant + multithreaded lets
`_pose_callback` keep firing concurrently.

**Why time-based driving is acceptable here:** turtlesim applies whatever
`Twist` you publish directly each simulation tick — no inertia, no physics —
so `distance = speed × time` and `angle = angular_speed × time` hold almost
exactly. `pose` is only used to *measure* what happened, not to steer.

### `practice_cpp/src/patrol_action_client.cpp`

```cpp
#include <cstdlib>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "practice_interfaces/action/patrol.hpp"

using Patrol = practice_interfaces::action::Patrol;
using GoalHandlePatrol = rclcpp_action::ClientGoalHandle<Patrol>;

class PatrolActionClient : public rclcpp::Node
{
public:
  PatrolActionClient(int laps, std::string action_name)
  : Node("patrol_action_client"), laps_(laps)
  {
    client_ = rclcpp_action::create_client<Patrol>(this, action_name);
  }

  void send_goal()
  {
    if (!client_->wait_for_action_server(std::chrono::seconds(5))) {
      RCLCPP_ERROR(get_logger(), "Action server not available");
      rclcpp::shutdown();
      return;
    }

    auto goal_msg = Patrol::Goal();
    goal_msg.laps = laps_;

    auto send_goal_options = rclcpp_action::Client<Patrol>::SendGoalOptions();
    send_goal_options.feedback_callback =
      [this](
      GoalHandlePatrol::SharedPtr,
      const std::shared_ptr<const Patrol::Feedback> feedback) {
        RCLCPP_INFO(
          get_logger(), "Lap %d, distance so far: %.2f",
          feedback->current_lap, feedback->distance_so_far);
      };
    send_goal_options.result_callback =
      [this](const GoalHandlePatrol::WrappedResult & result) {
        switch (result.code) {
          case rclcpp_action::ResultCode::SUCCEEDED:
            RCLCPP_INFO(
              get_logger(), "Patrol finished. Total distance: %.2f, time: %.2fs",
              result.result->total_distance, result.result->elapsed_time);
            break;
          case rclcpp_action::ResultCode::CANCELED:
            RCLCPP_WARN(get_logger(), "Patrol canceled");
            break;
          default:
            RCLCPP_ERROR(get_logger(), "Patrol failed");
            break;
        }
        rclcpp::shutdown();
      };

    client_->async_send_goal(goal_msg, send_goal_options);
  }

private:
  rclcpp_action::Client<Patrol>::SharedPtr client_;
  int laps_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  int laps = (argc > 1) ? std::atoi(argv[1]) : 2;
  std::string action_name = (argc > 2) ? argv[2] : "/turtle1/patrol";
  auto node = std::make_shared<PatrolActionClient>(laps, action_name);
  node->send_goal();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

Usage: `ros2 run practice_cpp patrol_action_client 3 /turtle1/patrol` for 3
laps against `turtle1`'s server.

---

## Module 6 — Launch files & parameters

### `practice_bringup/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.8)
project(practice_bringup)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
```

### `practice_bringup/package.xml`

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>practice_bringup</name>
  <version>0.0.1</version>
  <description>Launch files tying the practice packages together</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <exec_depend>practice_py</exec_depend>
  <exec_depend>practice_cpp</exec_depend>
  <exec_depend>practice_interfaces</exec_depend>
  <exec_depend>turtlesim</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

### `practice_bringup/launch/talker_listener.launch.py`

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate', default_value='2.0',
        description='Rate (Hz) at which the talker publishes')

    talker_node = Node(
        package='practice_py',
        executable='talker',
        name='talker',
        parameters=[{'publish_rate': LaunchConfiguration('publish_rate')}],
        output='screen')

    listener_node = Node(
        package='practice_cpp',
        executable='listener',
        name='listener',
        output='screen')

    return LaunchDescription([
        publish_rate_arg,
        talker_node,
        listener_node,
    ])
```

### `practice_bringup/launch/patrol_demo.launch.py`

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    laps_arg = DeclareLaunchArgument(
        'laps', default_value='2',
        description='Number of laps for the patrol action client to request')

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen')

    patrol_server = Node(
        package='practice_py',
        executable='patrol_action_server',
        name='patrol_action_server',
        output='screen')

    patrol_client = Node(
        package='practice_cpp',
        executable='patrol_action_client',
        name='patrol_action_client',
        arguments=[LaunchConfiguration('laps'), '/turtle1/patrol'],
        output='screen')

    return LaunchDescription([
        laps_arg,
        turtlesim_node,
        patrol_server,
        patrol_client,
    ])
```

Run with: `ros2 launch practice_bringup patrol_demo.launch.py laps:=3`

---

## Module 7 — Automated tests (stretch)

### `practice_py/test/test_patrol_math.py`

```python
from practice_py.patrol_action_server import leg_durations
import math
import pytest


def test_leg_durations_basic():
    forward, turn = leg_durations(side_length=2.0, linear_speed=1.0,
                                   angular_speed=math.pi / 2)
    assert forward == pytest.approx(2.0)
    assert turn == pytest.approx(1.0)


def test_leg_durations_scales_with_speed():
    forward, _ = leg_durations(side_length=4.0, linear_speed=2.0,
                                angular_speed=math.pi / 2)
    assert forward == pytest.approx(2.0)
```

Run with `colcon test --packages-select practice_py`, then
`colcon test-result --verbose` to see failures inline.

### C++ equivalent

If you extracted a small pure function on the C++ side too (e.g. a distance
helper), a matching `ament_add_gtest` target looks like:

```cmake
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_patrol_math test/test_patrol_math.cpp)
endif()
```

```cpp
#include <gtest/gtest.h>
#include <cmath>

double forward_duration(double side_length, double linear_speed)
{
  return side_length / linear_speed;
}

TEST(PatrolMath, ForwardDuration)
{
  EXPECT_NEAR(forward_duration(2.0, 1.0), 2.0, 1e-6);
}
```

---

## Module 8 — Capstone: two-turtle patrol

One valid architecture:

- `turtlesim_node` owns both turtles (`turtle1` exists at startup; `turtle2`
  is spawned into the same node via `/spawn`).
- `spawner` — a one-shot node/script that calls `/spawn` then exits.
- `battery_monitor` — publishes `RobotStatus` on `/<turtle_name>/status` for
  each turtle, and serves `/reset_battery` (`std_srvs/srv/Trigger`).
- Two instances of the **same** `patrol_action_server` executable from
  Module 5, differentiated by the `turtle_name` parameter (`turtle1` /
  `turtle2`) and by node `name=` in the launch file — that parameterization
  is exactly why Module 5 built it that way instead of hard-coding
  `/turtle1/...`.
- `mission_control` — sends a `Patrol` goal to each turtle's action server
  and logs when both finish.

### `practice_py/practice_py/spawner.py`

```python
import rclpy
from turtlesim.srv import Spawn


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('spawner')
    client = node.create_client(Spawn, '/spawn')

    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('Waiting for /spawn service...')

    request = Spawn.Request()
    request.x = 3.0
    request.y = 3.0
    request.theta = 0.0
    request.name = 'turtle2'

    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        node.get_logger().info(f'Spawned turtle: {future.result().name}')
    else:
        node.get_logger().error('Spawn service call failed')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### `practice_py/practice_py/battery_monitor.py`

```python
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

from practice_interfaces.msg import RobotStatus


class BatteryMonitor(Node):

    def __init__(self):
        super().__init__('battery_monitor')
        self.declare_parameter('turtle_names', ['turtle1', 'turtle2'])
        names = self.get_parameter(
            'turtle_names').get_parameter_value().string_array_value

        self._names = list(names)
        self._publishers = {
            name: self.create_publisher(RobotStatus, f'/{name}/status', 10)
            for name in self._names
        }
        self._battery = {name: 100.0 for name in self._names}

        self._timer = self.create_timer(1.0, self._tick)
        self._reset_srv = self.create_service(
            Trigger, '/reset_battery', self._handle_reset)

    def _tick(self):
        for name in self._names:
            self._battery[name] = max(0.0, self._battery[name] - 1.0)
            msg = RobotStatus()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.robot_name = name
            msg.battery_percent = self._battery[name]
            msg.status = 'patrolling' if self._battery[name] > 0 else 'depleted'
            self._publishers[name].publish(msg)

    def _handle_reset(self, request, response):
        for name in self._names:
            self._battery[name] = 100.0
        response.success = True
        response.message = 'Battery reset for all turtles'
        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = BatteryMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### `practice_py/practice_py/mission_control.py`

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from practice_interfaces.action import Patrol


class MissionControl(Node):

    def __init__(self):
        super().__init__('mission_control')
        self.declare_parameter('laps', 2)
        self.laps = self.get_parameter('laps').get_parameter_value().integer_value

        self._clients = {
            'turtle1': ActionClient(self, Patrol, '/turtle1/patrol'),
            'turtle2': ActionClient(self, Patrol, '/turtle2/patrol'),
        }
        self._pending = set(self._clients.keys())

    def start(self):
        for name, client in self._clients.items():
            client.wait_for_server()
            goal = Patrol.Goal()
            goal.laps = self.laps
            future = client.send_goal_async(
                goal, feedback_callback=self._make_feedback_cb(name))
            future.add_done_callback(self._make_goal_response_cb(name))

    def _make_feedback_cb(self, name):
        def cb(feedback):
            fb = feedback.feedback
            self.get_logger().info(
                f'[{name}] lap {fb.current_lap}, distance {fb.distance_so_far:.2f}')
        return cb

    def _make_goal_response_cb(self, name):
        def cb(future):
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().warn(f'[{name}] goal rejected')
                self._pending.discard(name)
                return
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self._make_result_cb(name))
        return cb

    def _make_result_cb(self, name):
        def cb(future):
            result = future.result().result
            self.get_logger().info(
                f'[{name}] finished: distance={result.total_distance:.2f}, '
                f'time={result.elapsed_time:.2f}s')
            self._pending.discard(name)
            if not self._pending:
                self.get_logger().info('All turtles finished patrolling')
        return cb


def main(args=None):
    rclpy.init(args=args)
    node = MissionControl()
    executor = MultiThreadedExecutor()
    node.start()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### `practice_bringup/launch/capstone.launch.py`

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    laps_arg = DeclareLaunchArgument('laps', default_value='2')

    turtlesim = Node(
        package='turtlesim', executable='turtlesim_node',
        name='turtlesim', output='screen')

    spawner = Node(
        package='practice_py', executable='spawner',
        name='spawner', output='screen')

    battery_monitor = Node(
        package='practice_py', executable='battery_monitor',
        name='battery_monitor', output='screen',
        parameters=[{'turtle_names': ['turtle1', 'turtle2']}])

    patrol_server_1 = Node(
        package='practice_py', executable='patrol_action_server',
        name='patrol_action_server_turtle1', output='screen',
        parameters=[{'turtle_name': 'turtle1'}])

    patrol_server_2 = Node(
        package='practice_py', executable='patrol_action_server',
        name='patrol_action_server_turtle2', output='screen',
        parameters=[{'turtle_name': 'turtle2'}])

    mission_control = Node(
        package='practice_py', executable='mission_control',
        name='mission_control', output='screen',
        parameters=[{'laps': LaunchConfiguration('laps')}])

    # Give the spawner and both action servers a moment to come up before
    # mission_control starts sending goals.
    delayed_mission_control = TimerAction(period=3.0, actions=[mission_control])

    return LaunchDescription([
        laps_arg,
        turtlesim,
        spawner,
        battery_monitor,
        patrol_server_1,
        patrol_server_2,
        delayed_mission_control,
    ])
```

Run with: `ros2 launch practice_bringup capstone.launch.py laps:=2`, then in
another shell: `ros2 topic echo /turtle1/status`, `ros2 topic echo
/turtle2/status`, and `ros2 service call /reset_battery std_srvs/srv/Trigger`
to confirm the reset path.

**What made two turtles coexist cleanly:** every name that could collide was
parameterized or made explicit — `cmd_vel`/`pose` topics via `turtle_name`,
the action name via `turtle_name`, and the node name via launch's `name=`.
Nothing in the node code itself changed between Module 5 and Module 8; only
how many instances you launch, and with what parameters.
