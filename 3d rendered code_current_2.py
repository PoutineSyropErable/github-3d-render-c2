 #----This line of code sets the current working directory to the directory where the file is being runned, rather then just documents folder
from render_function_current_2 import *


""" how to use this program:
have this python file
render_function_current_2
render_3d_shared
and spaceship_ini
in the same directory
run this

playing key:
aswd : move camera
shift space: up and down
mouse movement: move camera

r: reset position and camera
e: reset position

f: time stop (you can still move, but not the object)
c: pause program (nothing move)
escape: end program
 """

print(FPS_playing)

#--------------setting up the text
font = pygame.font.Font('freesansbold.ttf', 20)


def pause(game_paused):
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            #print("The program finished running \n \n")
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                #print("Test")
                game_paused = not game_paused
        
    pygame.display.update()
    clock.tick(20)
    return(game_paused)
#------------------------------------------------------End of the function that needs to be in this part

#-------Make the surfaces
white_surface = pygame.Surface((WIDTH,HEIGHT))
white_surface.fill("grey")



#--------------Initializing variables


cube = Object3D(matrix_to_array(cube_ini),face,camera,color_face,name="cube")
spaceship = Object3D(filename="spaceship_ini.obj",name="shapeship")
#spaceship2 = Object3D(filename="spaceship_part.obj",name="shapeship",face_color=["green","red"],remove="False")

cube.translate(5,0,-3)
cube.scale(0.05)



#spaceship.center_rotate(2,3,0.2)
spaceship.translate(5,0,-3)
#spaceship.scale(4)
#spaceship2.scale(4)

cube_rot_speed = 0.02
cube_rot_x,cube_rot_y,cube_rot_z = 0,0,0
time_stop = False





#--------------------------------doing some computer first run to define stuff
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
pygame.mouse.set_pos(a(0,0))



#spaceship.order_face(projection_matrix)
#--------------------------------------------------------------The actual code being runned every frame
while True:
    ##print(camera.pos)
    #adding a pause to the game:
    while game_paused:
        game_paused = pause(game_paused)
        

    #----------------------------------------------START OF MOUSE MOVEMENT CODE
    #Moving the camera with the mouse fps style
    mouse_change_rel = pygame.mouse.get_rel()
    if mouse_change_rel != (0,0):
        camera.rot_y += camera_rot_speed_hor_hor*mouse_change_rel[0]
        camera.rot_x -= camera_rot_speed_hor_ver*mouse_change_rel[1] #because the change in y coordinate, mobing the mouse down means a positive delta_mouse_y

        mouse_position = pygame.mouse.get_pos()#so the mouse stays in the screen
        if (mouse_position[0] <= W_BUFFER or mouse_position[0] >= WIDTH-W_BUFFER) or (mouse_position[1] <= H_BUFFER or mouse_position[1] >= HEIGHT-H_BUFFER): 
            pygame.mouse.set_pos(a(0,0))
        if camera.rot_x >= PI/2:
            camera.rot_x = PI/2
        if camera.rot_x <= -PI/2:
            camera.rot_x = -PI/2
    #--------------------------------------------------END OF MOUSE MOVEMENT CODE
    
    #-------------START OF camera MOUVEMENT CODE------------------------------------------
        #These are the vector for movements
    movement_array = np.dot(Ry(camera.rot_y),Rz(camera.rot_z))
    movement_array = np.dot(Rx(camera.rot_x),movement_array)
    movement_array = np.transpose(np.array(movement_array)[0:3,0:3])
    movement_array[2,1] = 0
    movement_array[0,1] = 0
    movement_array[2] = movement_array[2] / norm(movement_array[2])
    movement_array[1] = movement_array[1] / norm(movement_array[1])

    keys = pygame.key.get_pressed()
    #movement keys
    camera_move_vec = np.array([0,0,0])
    if keys[pygame.K_w]:
        camera_move_vec = camera_move_vec + movement_array[2] #using absolute positioning to simplify stuff
    if keys[pygame.K_s]:
        camera_move_vec = camera_move_vec - movement_array[2]
    if keys[pygame.K_d]:
        camera_move_vec = camera_move_vec + movement_array[0]
    if keys[pygame.K_a]:
        camera_move_vec = camera_move_vec - movement_array[0]
    if keys[pygame.K_SPACE]:
        camera_move_vec = camera_move_vec + np.array([0,1,0])
    if keys[pygame.K_LSHIFT]:
        camera_move_vec = camera_move_vec - np.array([0,1,0])

    if abs(norm(camera_move_vec) - 1) > 0.1 and norm(camera_move_vec) > 0.1  :
        camera_move_vec = camera_move_vec / norm(camera_move_vec)

    camera.pos = camera.pos + camera_move_speed*camera_move_vec
    #-------------END OF camera MOUVEMENT CODE------------------------------------------


    #Getting the event and single key press (Runs once when the key is pressed) +++++++ Making it quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            #print("The program finished running \n \n")
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                game_paused = not game_paused

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: #r for resetting your position
                camera.rot_y,camera.rot_x = 0,0
                camera.pos = np.array([0,0,-10])
            if event.key == pygame.K_e:
                camera.pos = np.array([0,0,-10])
            if event.key == pygame.K_f:
                time_stop = not time_stop
                
    
    #--------------# creating the projection matrix
    translation_matrix = np.matrix([[ 1 , 0 , 0 , -camera.pos[0]],
                                [ 0 , 1 , 0 , -camera.pos[1]],
                                [ 0 , 0 , 1 , -camera.pos[2]],
                                [ 0 , 0 , 0 ,       1       ]])
    rotation_matrix = np.dot(Ry(-camera.rot_y),Rz(-camera.rot_z))
    rotation_matrix = np.dot(Rx(-camera.rot_x),rotation_matrix)
    rs.projection_matrix = np.dot(rotation_matrix,translation_matrix)


    #print(id(projection_matrix))

    #rendering the cube calculations
    


    #-------- START OF DRAWING EVERYTHING------------------------------------- START OF DRAWING EVERYTHINg----------- START OF DRAWING EVERYTHING
    screen.fill("grey")


    camera.camera_update(camera.pos,camera.rot_x,camera.rot_y,camera.rot_z)


    cube.render_mesh()
    #print(cube.face_render_order)
    
    cube.render_face()

    spaceship.render_mesh(False)

    #spaceship.generate_color_light()
    #spaceship.render_face(True)
    #spaceship2.render_face()
    #print("number of face not shown=",len(spaceship.face_not_shown))
    #if len(spaceship.face_not_shown) != 0:
        #print(" ")
    rs.bruh = True

    #spaceship.render_mesh(projection_matrix,False)
    if not time_stop:
        #spaceship.translate(0,0,0.2)
        spaceship.center_rotate(0,0,0.05)
        #pass


    

    #the cursor11
    pygame.draw.line(screen,"gold",a(-10,0),a(10,0))
    pygame.draw.line(screen,"gold",a(0,-10),a(0,10))

    #---------THE TEXT    
    camera.pos_text = font.render('camera pos = ' + str(  np.round(camera.pos,2)  ), True, (0,0,0),)
    text_pos_Rect = camera.pos_text.get_rect(center= a(int(0.6*WIDTH/2),int(0.75*HEIGHT/2)))
    screen.blit(camera.pos_text, text_pos_Rect)

    camera_angle = np.array([camera.rot_y,camera.rot_x])
    camera_angle_text = font.render('[phi, theta] = ' + str(  np.round(180/PI*camera_angle,2)  ), True, (0,0,0))
    text_angle_Rect = camera_angle_text.get_rect()
    text_angle_Rect.center = a(0.6*WIDTH/2,0.65*HEIGHT/2)
    screen.blit(camera_angle_text, text_angle_Rect)
    #-------- END OF DRAWING EVERYTHING------------------------------------- END OF DRAWING EVERYTHING----- END OF DRAWING EVERYTHING----- END OF DRAWING EVERYTHING-----

    

    #cube.project_2(cube.vertex_matrix,projection_matrix)
    #time_stop = True

    cube_rot_x = cube_rot_speed*(not time_stop)
    cube_rot_y = random.random()*cube_rot_speed*(not time_stop)
    cube_rot_z = m.sqrt(2)*cube_rot_speed*(not time_stop)
    #cube.center_rotate(cube_rot_x,cube_rot_y,cube_rot_z)
    

    #update everything (except camera mouvement and mouse movement (so everything that moved during the frame thats not directly camera input))
    #So, if my input makes an entity move (indirectly), the code to change said entity is here (let's say it's due to the entity reaction time of 1 frame)


    
    #the final two lines
    #print("------------end of frame----------")
    pygame.display.update()
    clock.tick(FPS_playing)
    
    






