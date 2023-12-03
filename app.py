from flask import url_for, g, jsonify
from flask import render_template
from flask import request 
from sqlite3 import Error
import subprocess
import signal
import os
import time
import sqlite3

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

from flask import Flask
app = Flask(__name__)

data = ''
plan = ''

DATABASE = os.path.join(os.getcwd(), "static", "database.db")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


class roslaunch_process():
    @classmethod
    def start_navigation(self, mapname):
        
        # self.process_navigation = subprocess.Popen(
        #     ["ros2", "launch", "robot_pose_publisher_ros2", "robot_pose_publisher_launch.py"])
        
        # self.process_navigation = subprocess.Popen(
        #     ["ros2", "launch", "gcamp_gazebo", "launch_sim.launch.py"])
        
        # self.process_navigation = subprocess.Popen(
        #     ["rviz2"])

        self.process_navigation = subprocess.Popen(
            ["ros2", "launch", "gcamp_gazebo", "navigation_launch.py", "use_sim_time:=false"])
        
        time.sleep(5)

        self.process_navigation = subprocess.Popen(
            ["ros2", "launch", "gcamp_gazebo", "localization_launch.py", "map:=./static/"+ mapname +".yaml", "use_sim_time:=false"])  

    @classmethod
    def stop_navigation(self):
        # self.process_navigation.send_signal(signal.SIGINT)
        self.process_navigation.kill()

    @classmethod
    def start_mapping(self):

        # self.process_mapping = subprocess.Popen(
        #     ["ros2", "launch", "robot_pose_publisher_ros2", "robot_pose_publisher_launch.py"])    

        self.process_mapping = subprocess.Popen(
            ["ros2", "launch", "gcamp_gazebo", "launch_sim.launch.py"])

        self.process_mapping = subprocess.Popen(
            ["rviz2"])

        # self.process_mapping = subprocess.Popen(
        #     ["ros2", "launch", "gcamp_gazebo", "online_async_launch.py", "use_sim_time:=false"])

        self.process_mapping = subprocess.Popen(
            ["ros2", "launch", "gcamp_gazebo", "online_async_launch.py"])
        
        
    @classmethod
    def stop_mapping(self):
        # self.process_mapping.send_signal(signal.SIGINT)
        self.process_mapping.kill()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# @app.before_first_request
# def create_table():

#     subprocess.Popen(["ros2", "launch", "gcamp_gazebo",
#                       "navigation_launch.py"])

#     with app.app_context():
#         try:
#             c = get_db().cursor()
#             c.execute(
#                 "CREATE TABLE IF NOT EXISTS maps (id integer PRIMARY KEY,name text NOT NULL)")
#             c.close()
#         except Error as e:
#             print(e)

## get function to get sensor readings :
@app.route('/getReadings', methods=['GET'])
def update():
    global data
    data = "sensors = 1,2,3,4,5,6,7,8,9,10"
    return data
    
    
  
## Get Request to get plan:
#convert ros coordinates to web coordinates to visualize plan on the ui
outMinX = 0
outMaxX = 945
outMinY = 0
outMaxY = 681
inMinX = -8.36
inMaxX = 18
inMinY = 8.18
inMaxY = -11.1
@app.route('/getPlan', methods=['GET'])
def updateplan():
    global plan
    if (plan == ''):
        return ''
    print('return')
    out = ''
    temp = plan.split('_')
    for point in temp:
        pt = point.split(',')
        if (len(pt) == 2):
            x = (pt [0])
            y = (pt [1])
       
               
## Equation
           
            outx = ((float(x)- inMinX) / (inMaxX - inMinX)) * (outMaxX - outMinX) + outMinX
            outy = ((float(y) - inMinY) / (inMaxY - inMinY)) * (outMaxY - outMinY) + outMinY
            out += str(outx)+','+str(outy)+'_'
    return out[0:-1]
    

##Get goal position 
@app.route('/getpose/<val>')
def updatepose(val):
    
    
    print(val.split(','))
    publish.single('cic_pose', val, hostname='broker.hivemq.com')
    return 'ok'
    

## MQTT:
##decoding messages from string to the type what we need (int ,float,..) then print in terminal
def onFB(_, __, msg):
    global data
    data = msg.payload.decode('utf-8')
    print(data)
    
def onPlan(_, __, msg):
    global plan
    plan = msg.payload.decode('utf-8')
    print(plan)



@app.route('/')
def index():

    with get_db():
        try:
            c = get_db().cursor()
            c.execute("SELECT * FROM maps")
            data = c.fetchall()
            c.close()
        except Error as e:
            print(e)

    return render_template('index.html', title='Index', map=data)


@app.route('/index/<variable>', methods=['GET', 'POST'])
def themainroute(variable):
    if variable == "navigation-precheck":

        with get_db():

            try:

                c = get_db().cursor()

                c.execute("SELECT count(*) FROM maps")
                k = c.fetchall()[0][0]
                c.close()

                print(k)
                return jsonify(mapcount=k)

            except Error as e:
                print(e)
    elif variable == "gotonavigation":

        mapname = request.get_data().decode('utf-8')

        roslaunch_process.start_navigation(mapname)
        
        return "success"


@app.route('/navigation', methods=['GET', 'POST'])
def navigation():

    with get_db():
        try:
            c = get_db().cursor()
            c.execute("SELECT * FROM maps")
            data = c.fetchall()
            c.close()
        except Error as e:
            print(e)
    return render_template('navigation.html', map=data)


@app.route('/navigation/deletemap', methods=['POST'])
def deletemap():
    mapname = request.get_data().decode('utf-8')
    print(mapname)
    os.system("rm -rf"+" "+os.getcwd()+"/static/"+mapname+".yaml "+os.getcwd() +
              "/static/"+mapname+".png "+os.getcwd()+"/static/"+mapname+".pgm")

    with get_db():
        try:
            c = get_db().cursor()
            c.execute("DELETE FROM maps WHERE name=?", (mapname,))
            c.close()
        except Error as e:
            print(e)
    return ("successfully deleted map")


@app.route("/navigation/<variable>", methods=['GET', 'POST'])
def gotomapping(variable):
    if variable == "index":
        roslaunch_process.start_mapping()
    elif variable == "gotomapping":
        roslaunch_process.stop_navigation()
        time.sleep(2)
        roslaunch_process.start_mapping()
    return "success"


@app.route("/navigation/loadmap", methods=['POST'])
def navigation_properties():

    mapname = request.get_data().decode('utf-8')

    roslaunch_process.stop_navigation()
    time.sleep(5)
    roslaunch_process.start_navigation(mapname)
    return("success")


@app.route("/navigation/stop", methods=['POST'])
def stop():
    # os.system("rostopic pub /move_base/cancel actionlib_msgs/GoalID -- {}")
    return("stopped the robot")


@app.route('/mapping')
def mapping():
    with get_db():
        try:
            c = get_db().cursor()
            c.execute("SELECT * FROM maps")
            data = c.fetchall()
            c.close()
        except Error as e:
            print(e)

    return render_template('mapping.html', title='Mapping', map=data)


@app.route("/mapping/cutmapping", methods=['POST'])
def killnode():
    roslaunch_process.stop_mapping()
    return("killed the mapping node")


@app.route("/mapping/savemap", methods=['POST'])
def savemap():
    mapname = request.get_data().decode('utf-8')

    os.system("ros2 run nav2_map_server map_saver_cli -f" + " " +
              os.path.join(os.getcwd(), "static", mapname) + " " + 
              "--ros-args -p save_map_timeout:=10000" )
    os.system("convert ./static/"+ mapname + ".pgm" +
              " ./static/" + mapname + ".png")

    with get_db():
        try:
            c = get_db().cursor()
            c.execute("insert into maps (name) values (?)", (mapname,))
            # get_db().commit()
            c.close()
        except Error as e:
            print(e)

    return("success")


@app.route("/shutdown", methods=['POST'])
def shutdown():
    os.system("shutdown now")
    return("shutting down the robot")


@app.route("/restart", methods=['POST'])
def restart():
    os.system("restart now")
    return("restarting the robot")



if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
