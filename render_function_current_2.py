#importing the mathematical library
import numpy as np
import math as m
import random



#importing the non mathematical library
import pygame #duh
import sys, os
os.chdir(sys.path[0])
np.set_printoptions(suppress=True)

#for the projection matrix
import render_3d_shared as rs #render_share

pygame.init() #Needed to get pygame initiated

print("\n"*20+"-"*11,"start of program","-"*11)



WIDTH , HEIGHT = 1900,1000


#pygame boiler plate part 2
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("3d_renderer")
clock = pygame.time.Clock()

#setting constants:
PI = m.pi
W_BUFFER, H_BUFFER = 40,40 #for when the camera moves off screen
z_near, z_far = 0.4,40
fov = 90 * PI/180
game_paused = False
FPS_playing = rs.FPS_playing

#creating a grid
GRID_MIN, GRID_MAX =  -3, 3
GRID_SIZE = 1

#setting cube faces: 1 5 4 0
face= np.array([ [0,2,3,1] , [0,1,5,4], [2,6,7,3], [4,5,7,6], [1,3,7,5] , [0,4,6,2]])
color_face = ["red", "green", "blue", "orange","white","black"]

#----------------------defining mathematical functions
def a(x,y):
    ''' (num,num) -> (num,num)
    takes a coordinates in cartesian and output the number in shitty 
    coordinates png style
    '''
    return(x + WIDTH/2,HEIGHT/2 - y)

def b(array):
    ''' (array or list) -> list
    takes an arrray corresponding to a coordinates in cartesian
    | output the coordinate in array form in a shitty png style'''
    return(a(array[0],array[1]))


def norm(array):
    """(array)-> (num)
    takes an array and return the euclidean norm"""
    return(np.linalg.norm(array))

Rx = rs.Rx
Ry = rs.Ry
Rz = rs.Rz



#-------------------defining translation_matrix so it's global  ---------------- AND SETTING THE CAMERA
camera_move_speed = rs.camera_move_speed
camera_move_vec = rs.camera_move_vec
camera_sensitivity_hor, camera_sensitivity_ver = 3 , 3
camera_rot_speed_hor_hor = 0.1/(FPS_playing) * camera_sensitivity_hor
camera_rot_speed_hor_ver = 0.1/(FPS_playing) * camera_sensitivity_ver


camera = rs.Camera()
camera.pos = np.array([0,0,-10]) #initial position
camera.rot_y,camera.rot_x = 0,0  #initial inclinaison
camera.rot_z = 0 #this won't change


projection_matrix = rs.projection_matrix



cube_ini = []

for i in [-1,1]:
    for j in [-1,1]:
        for k in [-1,1]:
            cube_ini.append([i,j,k,1])

cube_ini = np.matrix(np.transpose(cube_ini))



def array_to_matrix(array):
    """(array)-> matrix
    takes an numpy array and outputs a matrix
    this is used so that I can use the array for some operations and the matrix for the 3d rendering calculations"""
    array = np.transpose(array)
    matrix = np.insert(array,array.shape[0],np.ones(array.shape[1]),axis= 0)
    return(np.matrix(matrix))

def matrix_to_array(matrix):
    """(array)-> matrix
    takes an numpy array and outputs a matrix
    this is used so that I can use the array for some operations and the matrix for the 3d rendering calculations"""
    array = np.array(matrix)
    array = np.delete(array,3,0)
    return(np.transpose(array))


def load_obj(filename):
    fobj = open(filename, "r").read()
    file_list = fobj.split("\n")

    for i in range(len(file_list)):
        file_list[i] = file_list[i].strip(" ")


    i = 0
    while i < len(file_list):
        line = file_list[i]
        if line[0] == "#":
            file_list.remove(line)
        else:
            i += 1


    vertex_array = []
    face_array = []
    for line in file_list:
        if line[0] == "v":
            vertex = line.split(" ")[1:]
            vertex = np.array(vertex,dtype=float)
            vertex_array.append(vertex)

        if line[0] == "f":
            face = line.split(" ")[1:]
            face = np.array(face,dtype=int) - np.array([1,1,1]) #because they start at (1,n) whereas computer (0,n-1)
            face_array.append(face)

    vertex_array = np.array(vertex_array)
    face_array = np.array(face_array)
    return(vertex_array,face_array)



def project_3D_to_2D(vertex_matrix):
    pos_cam_proj = np.dot(rs.projection_matrix,vertex_matrix)

    shape = (np.shape(pos_cam_proj)[1],3)
    pos_cam_perspective = np.zeros(shape)
    for i in range(shape[0]):
        pos_cam_perspective[i,0] =  0.5 * (1/m.tan(fov/2)) * WIDTH * pos_cam_proj[0,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,1] =  0.5 * (1/m.tan(fov/2)) * WIDTH  * pos_cam_proj[1,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,2] = (z_far/(z_far-z_near))*(pos_cam_proj[2,i] - z_near)


    pos_cam_perspective = np.array(pos_cam_perspective)
    return(pos_cam_perspective)


class PolygonFace:
    """ This class represent the face generated by the polygons on a Objet3D"""
    def __init__(self,vertex3D,index,color=(0,0,0),camera=rs.Camera(),name="def face",remove= True):
        
        self.color = color
        #print(self.color)
        self.vertex3D =  vertex3D

        self.vertex_matrix = array_to_matrix(self.vertex3D)

        self.center = np.array([0,0,0])
        for vertex in self.vertex3D:
            self.center = self.center + vertex

        self.center = self.center/len(self.vertex3D)
        self.name = name + " face # " + str(index)
        self.index = index



        vect1 =  self.vertex3D[1] -  self.vertex3D[0]
        vect2 =  self.vertex3D[2] -  self.vertex3D[1]
        vect1 = vect1 / norm(vect1)
        vect2 = vect2/ norm(vect2)

        self.normal_vector = np.cross(vect1,vect2)
        
        self.shown = True

        center_temp = array_to_matrix(np.array([self.center]))
        self.center_z = project_3D_to_2D(center_temp)[0,2]

        self.vertex2D = project_3D_to_2D(self.vertex_matrix)[:,0:2]
        for i in range(len(self.vertex2D)):
            if abs(self.vertex2D[i,0]) <= WIDTH + W_BUFFER  and abs(self.vertex2D[i,1]) <= HEIGHT + H_BUFFER and self.center_z <= z_far and self.center_z  >=  z_near:
                pass
            else:
                self.shown = False
                #print(WIDTH,"this is not shown\n",self)



        vertex2D_temp = []
        #converting it to a list of tupple
        for i in range(len(self.vertex2D)):
            vertex2D_temp.append(b(tuple(self.vertex2D[i])))

        self.vertex2D = vertex2D_temp



        self.light = np.dot(self.normal_vector,(self.center-camera.pos)/norm(  (self.center-camera.pos)   ))
        if remove:
            if self.light <=0 and self.shown == True:
                if rs.bruh:
                    #self.vertex3D
                    #if self.index+59 != 79:
                    # print("Caught it")
                    #print("wrong line=",self.index+59)
                    #print("light=",self.light)
                    #print(self.vertex3D)
                    rs.bruh = False
                self.shown = False
                #pass

    def __str__(self):
        q = "-"*20 + "\n"
        q += "Here is the Face data: \n \n"
        q += "name = " + str(self.name) +" \n"
        q += "points_3D = \n" + str(self.vertex3D) + "\n \n"
        q += "points_2D = \n" + str(self.vertex2D) + "\n \n"
        q += "center3D = " + str(self.center) + "\n"
        q += "center_z = " + str(self.center_z) +"\n"
        q += "shown = " + str(self.shown) + "\n\n"
        q += "normal =" + str(self.normal_vector) + "\n"
        q += "lightning = " + str(self.light) + "\n"
        q += "color = " + str(self.color) +"\n" + "_"*20
        
        return(q)




        

class Object3D:
    """The class corresponding to the 3d object"""
    zero_matrix = np.matrix([[0],[0],[0],[1]])
    zero_array = np.array([0,0,0])
    zerror_array_4 = np.array([0,0,0,0])
    #print(zero_matrix) matrix_to_array(cube_ini),face
    def __init__(self, vertex_array=  None , face_array = None,camera = rs.Camera(),face_color = None,
    filename = "",name="def",remove= True):
        """(numpy.ndarray(N x 3), np.ndarray(M x 4))
                         ^ (x,y,z)  ^(a squarre shape)
        example of vertex array:
        [[-1.  0.  0.]
        [ 0. -1.  0.]
        [ 0.  1.  0.]
        [ 1.  0.  0.]
        [ 0.  0.  1.]
        [ 0.  0. -1.]]
        
        example of vertex matrix:
        [[-1 -1 -1 -1  1  1  1  1] each collumns is (x,y,z,1) of a point.
        [-1 -1  1  1 -1 -1  1  1]
        [-1  1 -1  1 -1  1 -1  1]
        [ 1  1  1  1  1  1  1  1]] <- last rows is always 1 for translations

        example of face_array:
        [[0 2 3 1] each row represent the index of a face in the vertex matrix
        [0 1 5 4]
        [2 6 7 3]
        [4 5 7 6]
        [1 3 7 5]
        [0 4 6 2]]
        """
        if type(vertex_array) == type(None) and type(face_array) == type(None):
            if vertex_array == None and face_array == None and filename != "":
                vertex_array,face_array = load_obj(filename)


        self.vertex_array = vertex_array
        self.vertex_matrix = array_to_matrix(self.vertex_array)


        self.name = name
        self.remove = remove


        
        self.face_array = face_array
        self.face_color = face_color
        
        self.camera = camera

        
        if face_color == None:
            self.face_color = []
            for i in range(len(self.face_array)):

                self.face_color.append( (0,0,0) )
            self.project_2(update=True)
            self.generate_color_light()


        self.update("array")
        #print("color=",self.face_color)
        self.translate(-self.object_center)


        
        



    def update(self,mode):
        """ update the face_center, the object center"""
        if mode == "matrix": #using the matrix to update
            self.vertex_array = matrix_to_array(self.vertex_matrix)
        
        elif mode == "array":
            self.vertex_matrix = array_to_matrix(self.vertex_array)

        else:
            raise AssertionError("You didn't specify what to update from")



        #generating the face object
        self.face_list = []
        i_temp = 0
        for face_index in self.face_array:
            self.face_list.append(PolygonFace(  self.vertex_array[face_index] ,i_temp ,camera= self.camera ,color = self.face_color[i_temp],name = self.name
            ,remove = self.remove))
            #print(self.face_list[i_temp],"\n")
            i_temp +=1

        #----------------start of face_center_list
        self.face_center_list = []
        for vertexes in self.face_array:
            face_center = np.array([0,0,0])
            for vertex_index in vertexes:
                face_center= face_center + self.vertex_array[vertex_index]
 

            face_center = face_center/len(vertexes)
            self.face_center_list.append(face_center)
        self.face_center_list = np.array(self.face_center_list)
        #-----------------end of face_center_list


        #-----------start of keep
        self.object_center = np.array([0,0,0])

        for vertex_pos in self.vertex_array:
            self. object_center = self.object_center + vertex_pos

        self.object_center = self.object_center/len(self.vertex_array) 

        self.face_not_shown = []
        for face in self.face_list:
            if face.shown == False:
                self.face_not_shown.append(face.index)
        
        self.face_not_shown = list(np.sort(self.face_not_shown))
        #-----------end of keep










        

    def scale(self,scale_x,scale_y= None,scale_z = None,update=True):

        if scale_z == None or scale_y == None:
            scale_y,scale_z = scale_x,  scale_x

        temp_center= self.object_center
        self.translate(-self.object_center,False)

        scale_matrix = np.matrix(
        [
        [scale_x,0,0,0],
        [0,scale_y,0,0],
        [0,0,scale_z,0],
        [0,0,  0,    1]])
        self.vertex_matrix = np.dot(scale_matrix,self.vertex_matrix)

        self.translate(temp_center,False)
        if update:
            self.update("matrix")

    def translate(self,delta_x,delta_y=0,delta_z=0,update=True):

        if type(delta_x) == type(np.array([1])) or type(delta_x) == type([1]):
            if len(delta_x) == 3:
                delta_y = delta_x[1]
                delta_z = delta_x[2]
                delta_x = delta_x[0]

                #print(delta_x,delta_y,delta_z)

        translate_matrix =  np.matrix([
        [1,0,0,delta_x],
        [0,1,0,delta_y],
        [0,0,1,delta_z],
        [0,0,0,1]])


        self.vertex_matrix = np.dot(translate_matrix,self.vertex_matrix)
        if update:
            self.update("matrix")

    def rotate(self,rot_x,rot_y,rot_z,update=True): #rotate the object base on
        rot_mat = np.dot(Ry(rot_y),Rz(rot_z))
        rot_mat = np.dot(Rx(rot_x),rot_mat)
        self.vertex_matrix = np.dot(rot_mat,self.vertex_matrix)
        if update:
            self.update("matrix")

    def center_rotate(self,rot_x,rot_y,rot_z): #rotate the object on itself
        center_temp = self.object_center
        self.translate(-self.object_center,False)
        self.rotate(rot_x,rot_y,rot_z,False)
        self.translate(center_temp,True)



    def project_2(self,remove = True,update=True):
        if update:
            self.update("matrix")
        self.vertex_perspective = project_3D_to_2D(self.vertex_matrix)


        face_center_matrix = array_to_matrix(self.face_center_list)
        face_center_z = project_3D_to_2D(face_center_matrix)[:,2]

        self.face_render_order = list(np.flip(np.argsort(face_center_z)))
            


        if remove:
            for i in self.face_not_shown:
                
                if i in self.face_render_order:                    
                    self.face_render_order.remove(i)


        #print("face order=",self.face_render_order)

    def render_mesh(self,remove=True):
        self.project_2(remove)
        

        for i in self.face_render_order:
            number_point_in_face = len(self.face_array[i])
            for j in range( number_point_in_face  ): #
                points = self.face_list[i].vertex2D
                #print(points)
                point_1 = points[j]
                point_2 = points[ (j + 1) % number_point_in_face ]
                pygame.draw.line(screen, self.face_list[i].color, point_1, point_2)


    def render_face(self,remove=True):
        self.update("matrix")
        for i in self.face_render_order:
            pygame.draw.polygon(screen, self.face_list[i].color,self.face_list[i].vertex2D)

    def generate_color_light(self,light_pos = np.array([0,0,0])):
        light_pos = self.camera.pos
        light_brightness = 1000
        self.face_color = [0]*len(self.face_array)
        #print(self.face_color)
        #print(self.face_color)
        for i in self.face_render_order:
            #print(self.face_normal[i],self.face_center_list[i])
            self.face_color[i] = np.dot(self.face_center_list[i] - light_pos,self.face_list[i].normal_vector)/(norm(light_pos - self.face_center_list[i]))**3
            self.face_color[i] = self.face_color[i] *  light_brightness * 255
            self.face_color[i] = max(self.face_color[i], 0   )
            self.face_color[i] = min(self.face_color[i], 255   )
            #self.face_color[i] = 
            self.face_color[i] = (self.face_color[i],self.face_color[i],self.face_color[i])
            #print(self.face_color[i])
        

#PolygonFace().normal_vector




"""
    def render_face3(self,projection_matrix,remove=True):
        #self.order_face(remove)
        self.update("matrix")
        for i in range(len(self.face_render_order)):
            ii = self.face_render_order[i]
            #pygame.draw.polygon(screen, self.face_list[ii].color, self.face_2D[i])
            pygame.draw.polygon(screen, self.face_list[ii].color,self.face_list[ii].vertex2D_tuple)

    def order_face(self,remove=True):
        self.face_2D = []
        self.project_2(remove=True)
        for i in self.face_render_order:
            length = len(self.face_array[i])

            for j in range(length):
                #print("length =",length)
                points_list = []

                for next_val in range(length):
                    k =  self.face_array[i, (j + next_val) % length ]  
                    points_list.append(b(self.vertex_perspective[k][0:2]))
                
            self.face_2D.append(points_list)
            #pygame.draw.polygon(screen, self.face_color[i], points_list)  #this is without creating a face thing

"""