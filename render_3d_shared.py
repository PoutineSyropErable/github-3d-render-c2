import numpy as np
import math as m

bruh = True

def Rx(rot_x):  #The rotation matrix over the x axis
    z   = np.matrix([
    [ 1, 0, 0, 0],
    [ 0, m.cos(rot_x), m.sin(rot_x), 0],
    [ 0, -m.sin(rot_x), m.cos(rot_x), 0],
    [ 0, 0, 0, 1 ]
    ])
    return(z)

def Ry(rot_y):#The rotation matrix over the y axis
    z = np.matrix([
    [ m.cos(rot_y), 0,m.sin(rot_y), 0],
    [ 0, 1, 0, 0],
    [ -m.sin(rot_y), 0, m.cos(rot_y), 0],
    [ 0, 0, 0, 1 ],
    ])
    return(z)

def Rz(rot_z): #The rotation matrix over the z axis
    z = np.matrix([
    [ m.cos(rot_z), m.sin(rot_z), 0, 0],
    [- m.sin(rot_z), m.cos(rot_z), 0, 0],
    [ 0, 0, 1, 0],
    [ 0, 0, 0, 1 ]
    ])
    return(z)

class Camera:
    """The camera class"""
    def __init__(self):
        self.rot_y,self.rot_x = 0,0
        self.rot_z = 0 #this won't change
        self.pos = np.array([14,0,-18])


    def set_rot(self,rot_x,rot_y,rot_z=0):
        self.rot_x,self.rot_y,self.rot_z = rot_x,rot_y,rot_z

    def add_rot(self,d_rot_x,d_rot_y,d_rot_z):
        self.rot_x += d_rot_x
        self.rot_y += d_rot_y
        self.rot_z += d_rot_z

    def get_rot(self): #kinda useless
        return(self.rot_x,self.rot_y,self.rot_z)

    def set_pos(self,pos_array):
        self.pos = pos_array

    def add_pos(self,pos_change_array):
        self.pos = self.pos + pos_change_array

    def camera_update(self,pos_array,rot_x,rot_y,rot_z):
        self.pos = pos_array
        self.rot_x,self.rot_y,self.rot_z = rot_x,rot_y,rot_z


    def __str__(self):
        q_string = "pos = " + str(self.pos) + " | rx = " + str(self.rot_x) + " ry = " + str(self.rot_y) + " rx = " + str(self.rot_y)
        return(q_string)



#-----------------------------setting the camera stuff
FPS_playing = 30

camera_move_speed = 9/FPS_playing
camera_move_vec = np.array([0,0,0])
camera_sensitivity_hor, camera_sensitivity_ver = 3 , 3
camera_rot_speed_hor_hor = 0.1/(FPS_playing) * camera_sensitivity_hor
camera_rot_speed_hor_ver = 0.1/(FPS_playing) * camera_sensitivity_ver


camera = Camera()
camera.pos = np.array([0,0,-10]) #initial position
camera.rot_y,camera.rot_x = 0,0  #initial inclinaison
camera.rot_z = 0 #this won't change



translation_matrix = np.matrix([[ 1 , 0 , 0 , -camera.pos[0]],
                                [ 0 , 1 , 0 , -camera.pos[1]],
                                [ 0 , 0 , 1 , -camera.pos[2]],
                                [ 0 , 0 , 0 ,       1       ]])
rotation_matrix = np.dot(Ry(-camera.rot_y),Rz(-camera.rot_z))
rotation_matrix = np.dot(Rx(-camera.rot_x),rotation_matrix)
projection_matrix = np.dot(rotation_matrix,translation_matrix)