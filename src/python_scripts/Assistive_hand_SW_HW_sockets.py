import os
import time
import socket
import tkinter as tk
from tkinter import messagebox
from math import radians, degrees, pi
import numpy as np
from robodk.robolink import *
from robodk.robomath import *

# Load RoboDK project from relative path
relative_path = "src/roboDK/Assistive_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)
RDK = Robolink()
RDK.AddFile(absolute_path)

# Robot setup
robot = RDK.Item("UR5e")
base = RDK.Item("UR5e Base")
tool = RDK.Item('Hand')
Init_target = RDK.Item('Init')
Control_1_target = RDK.Item('Control_1')
Pick_target = RDK.Item('Pick')
Control_2_target = RDK.Item('Control_2')
Show_target = RDK.Item('Show')

robot.setPoseFrame(base)
robot.setPoseTool(tool)
robot.setSpeed(20)

# Robot Constants
ROBOT_IP = '192.168.1.5'
ROBOT_PORT = 30002
accel_mss = 1.2
speed_ms = 0.75
blend_r = 0.0
timej = 6
timel = 4

# URScript commands
# RoboDK dona les coordenades en mm i graus pero en URScript necessitem m i rad
set_tcp = "set_tcp(p[0.000000, 0.000000, 0.050000, 0.000000, 0.000000, 0.000000])"
movej_init = f"movej(p[0.000000, -0.400000, 0.500000, 1.570796, 0.000000, 0.000000],1.20000,0.75000,{accel_mss},{speed_ms},{timel},0.000)"
movel_control_1 = f"movel(p[-0.370000, -0.550000, 0.300000, 1.246816, -1.148274, 1.148274],{accel_mss},{speed_ms},{timel/2},0.000)"
movel_pick = f"movel(p[-0.370000, -0.550000, 0.100000, 1.246817, -1.148274, 1.148274],{accel_mss},{speed_ms},{timel},0.000)"
movel_control_2 = f"movel(p[0.370000, -0.550000, 0.300000, 1.246816, -1.148274, 1.148274],{accel_mss},{speed_ms},{timel/2},0.000)"
movel_show = f"movel(p[0.370000, -0.550000, 0.300000, 1.230584, 1.175535, -1.175509],{accel_mss},{speed_ms},{timel/2},0.000)"

# Check robot connection
def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1)
        robot_socket.connect((ip, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
# Send URScript command
def send_ur_script(command):
    robot_socket.send((command + "\n").encode())

# Wait for robot response
def receive_response(t):
    try:
        print("Waiting time:", t)
        time.sleep(t)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        exit(1)

# Movements
def Init():
    print("Init")
    robot.setSpeed(100)
    robot.MoveJ(Init_target, True)
    print("Init_target REACHED")
    if robot_is_connected:
        print("Init REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movej_init)
        receive_response(timej)
    else:
        print("UR5e not connected. Simulation only.")

def Pick_object():
    print("")
    robot.setSpeed(100)
    robot.MoveL(Control_1_target, True)
    robot.setSpeed(30)
    robot.MoveL(Pick_target, True)
    # Petit stop per agafar l'objecte
    time.sleep(1)
    robot.setSpeed(50)
    robot.MoveL(Control_1_target, True)
    print("An object has been picked!")
    if robot_is_connected:
        print("Pick_object REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_control_1)
        receive_response(timel)
        send_ur_script(movel_pick)
        receive_response(timel)
        send_ur_script(movel_control_1)
        receive_response(timel)

def Show_object():
    robot.setSpeed(100)
    robot.MoveL(Control_2_target, True)
    robot.setSpeed(30)
    robot.MoveL(Show_target, True)
    # S'hauria de posar un stop aqui perque li dongui temps al metge d'agafar l'objecte
    print("The object has been gived, FINISHED")
    if robot_is_connected:
        print("Give5 REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_control_2)
        receive_response(timel)
        send_ur_script(movel_show)
        receive_response(timel)

# Confirmation dialog to close RoboDK
def confirm_close():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion(
        "Close RoboDK",
        "Do you want to save changes before closing RoboDK?",
        icon='question'
    )
    if response == 'yes':
        RDK.Save()
        RDK.CloseRoboDK()
        print("RoboDK saved and closed.")
    else:
        RDK.CloseRoboDK()
        print("RoboDK closed without saving.")

# Main function
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)
    Init()
    Pick_object()
    Show_object()
    Init()
    if robot_is_connected:
        robot_socket.close()

# Run and close
if __name__ == "__main__":
    main()
    #confirm_close()
