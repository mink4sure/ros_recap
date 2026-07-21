import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import rclpy.parameter
from rclpy.parameter_event_handler import ParameterEventHandler



class Talker(Node):
    def __init__(self):
        super().__init__('talker')

        self.declare_parameter('publish_rate', 2.0)
        self.handler = ParameterEventHandler(self)
        self.callback_handle = self.handler.add_parameter_callback(
            parameter_name='publish_rate',
            node_name='talker',
            callback=self.parameter_callback,
        )
        
        self.timer = self.create_timer(1/2, self.timer_callback)

        self.publisher_ = self.create_publisher(String, 'chatter', 10)


    def timer_callback(self):
        msg = String()
        msg.data = "Heya"
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)


    def parameter_callback(self, p: rclpy.parameter.Parameter) -> None:
        freq_s = rclpy.parameter.parameter_value_to_python(p.value) 
        self.get_logger().info(f"Received an update to parameter: {p.name}: {freq_s}")
        
        self.timer.timer_period_ns = ((1/freq_s)*10**9)


def main(args=None):
    rclpy.init(args=args)
    
    talker = Talker()
    rclpy.spin(talker)
    
    rclpy.shurdown()


if __name__ == '__main__':
    main()
