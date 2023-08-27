import paho.mqtt.client as mqtt
import rclpy # Import the ROS client library for Python
from rclpy.node import Node # Enables the use of rclpy's Node class
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path


#check if disconect ---> connect again
def on_disconnect(client, userdata, rc):
    print("disconnecting reason  "  +str(rc))
    client.connect("broker.hivemq.com", 1883, 60)
    
           
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("cic_pose")
    



# The callback for when a PUBLISH message is received from the server.
## publish goals that recieved from UI to ROS :
#convert WEB coordinates to ROS coordinates to give them to ROS & visualize goal on RVIZ
def on_message(client, userdata, msg):
    global publisher_goal_values
    
    px,py,pz,ox,oy,oz,ow = msg.payload.decode('utf-8').split(',')
    goalMsg = PoseStamped()
    
    goalMsg.pose.position.x = float(px)
    goalMsg.pose.position.y = float(py)
    goalMsg.pose.position.z = float(pz)
    goalMsg.pose.orientation.x = float(ox)
    goalMsg.pose.orientation.y = float(oy)
    goalMsg.pose.orientation.z = float(oz)
    goalMsg.pose.orientation.w = float(ow)

    goalMsg.header.frame_id    = "map"
    print (goalMsg)
     
    # Publish the x coordinates to the topic
    publisher_goal_values.publish(goalMsg)
    


def main(args=None):
	global client, publisher_goal_values
	# Initialize the rclpy library
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.on_disconnect = on_disconnect
	# Create the node
	rclpy.init(args=args)
	x = Node('values')
	publisher_goal_values = x.create_publisher(PoseStamped, 'goal_pose', 10) 
	client.connect("broker.hivemq.com", 1883, 60)
	client.loop_forever()
	
    
    
if __name__ == '__main__':
	main()
