import rclpy
from rclpy.node import Node
from turbidity_interfaces.msg import Turbidity
import rclpy.time
from std_msgs.msg import String

class TurbidityDecoder(Node):
    # $PVHY2,01,8,0.48705,0.012,NTU,141.65588,0.023,NTU,M1,*6D 

    def __init__(self, input_topic, output_topic):
        super().__init__('turbidity_driver')
        self.get_logger().info("Starting turbidity driver node to decode raw Turbidity data")
        self.publisher = self.create_publisher(Turbidity, output_topic, 10)
        self.subscriber = self.create_subscription(
            String,
            input_topic,
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f"Received message: {msg.data}")
        msg = msg.data.strip('\r\n').split(',')
        if len(msg) != 11:
            self.get_logger().error(f"Invalid message format. Length should be 11, got {len(msg)}")
            return
        turb_msg = Turbidity()
        turb_msg.time = self.get_clock().now().to_msg()
        turb_msg.nmea_header = msg[0]
        turb_msg.instrument_address = int(msg[1])
        turb_msg.parameter_id = int(msg[2])
        turb_msg.val1 = float(msg[3])
        turb_msg.val1_sd = float(msg[4]) if msg[4] else 0.0
        turb_msg.val1_unit = msg[5]
        turb_msg.val2 = float(msg[6])
        turb_msg.val2_sd = float(msg[7]) if msg[7] else 0.0
        turb_msg.val2_unit = msg[8]
        turb_msg.operating_mode = msg[9]
        turb_msg.check_sum = msg[10]
   
        self.get_logger().info(f"Publishing message: {turb_msg}")
        self.publisher.publish(turb_msg)

def main(args=None):
    rclpy.init(args=args)
    # TODO: Parse in/out topic from config file or launch file
    node = TurbidityDecoder(
        input_topic='/turbidity/raw',
        output_topic='/turbidity'
    )
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()