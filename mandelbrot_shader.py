import glfw, timeit, sys
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from PIL import Image
from shaders import vertex_src, fragment_src

file1 = open("to_draw.txt", "w")
file1.write('hey \n')

# Inititalize main game clock
clock = pg.time.Clock()

# viewer parameters
fbWidth, fbHeight = int(1920), int(1080)                    # Screenshot image dimensions
xmax, ymax = 1920.0, 1080.0                                 # Width and height (respectively) of display window
center_xt, center_yt, zoomt = -0.5, 0.0, 1.01               # Target center and target zoom
center_x, center_y, zoom = center_xt, center_yt, zoomt      # Actual center and actual zoom
wx = 4                                                      # Width of complex plane displayed
wy = wx * ymax / xmax                                       # Height of complex plane displayed
newpos = [0, 0]                                             # Mouse pixel coordinate
maxitr, brightness = 256.0, 6.0                             # Maximum iteration, brightness
zoomspeed, panspeed = 1.0034, 0.007                         # Camera zoom speed, camera pan speed
zoomin, zoomout, moveup, movedown, moveleft, moveright, newmouse, scrcap, zoomoutm = False, False, False, False, False, False, False, False, 1

###########################################################################################################################
# making all the glfw callback functions for keyboard and mouse inputs
def mouse_button_clb(window, button, action, mode):
    
    global newmouse, zoomin, zoomout, zoomoutm
    if button == glfw.MOUSE_BUTTON_3 and action == glfw.PRESS:
        zoomoutm = 1
        newmouse = True
    if button == glfw.MOUSE_BUTTON_3 and action == glfw.RELEASE:
        newmouse = False

    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        zoomoutm = 1
        zoomin = True
        newmouse = True
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
        zoomin = False
        newmouse = False

    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        zoomoutm = -1
        zoomout = True
        newmouse = True
    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        zoomoutm = -1
        zoomout = False
        newmouse = False


def cursor_pos_clb(window, xpos, ypos):
    mouse_coord(xpos, ypos)


def scroll_clb(window, xoffset, yoffset):
    global zoomin, zoomout
    pass


def key_input_clb(window, key, scancode, action, mode):
    global zoomin, zoomout, moveup, movedown, moveleft, moveright, maxitr, brightness, scrcap
    # zoomin, zoomout, moveup, movedown, moveleft, moveright = False, False, False, False, False, False
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        scrcap = True
    if key == glfw.KEY_E and action == glfw.PRESS:
        zoomin = True
    if key == glfw.KEY_E and action == glfw.RELEASE:
        zoomin = False

    if key == glfw.KEY_Q and action == glfw.PRESS:
        zoomout = True
    if key == glfw.KEY_Q and action == glfw.RELEASE:
        zoomout = False

    if key == glfw.KEY_W and action == glfw.PRESS:
        maxitr += 16
    if key == glfw.KEY_S and action == glfw.PRESS:
        maxitr -= 16

    if key == glfw.KEY_D and action == glfw.PRESS:
        brightness += 0.4
    if key == glfw.KEY_A and action == glfw.PRESS:
        brightness -= 0.4

###########################################################################################################################
# Camera functions

def mouse_coord(xpos, ypos):
    """
    setting the mouse coordinates every frame
    :param xpos:
    :param ypos:
    :return:
    """
    global newpos
    newpos = [xpos, ypos + 16]


def camera():
    """
    controls for camera, manipulating the centers x & y, as well as manipulating the zoom
    :return:
    """
    global center_x, center_y, zoom, zoomt, zoomin, zoomout, moveup, movedown, moveleft, moveright, center_xt, center_yt

    dz = zoomt - zoom
    zoom += dz*0.03
    if zoomin:
        zoomt *= zoomspeed
    if zoomout:
        zoomt *= 1 / zoomspeed

    dx = (center_xt - center_x)
    dy = (center_yt - center_y)

    center_x += dx * 0.02
    center_y += dy * 0.02

    if newmouse:
        center_xt += panspeed*(newpos[0] / xmax - 0.5) * wx / zoom * zoomoutm
        center_yt -= panspeed*(newpos[1] / ymax - 0.5) * wy / zoom * zoomoutm

###########################################################################################################################
# slimming the code
def AttribInit():
    position = glGetAttribLocation(program, "a_position")
    glEnableVertexAttribArray(position)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    scr_dims = glGetAttribLocation(program, "a_dims")
    glEnableVertexAttribArray(scr_dims)
    glVertexAttribPointer(scr_dims, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(36))

    center_n_zoom = glGetAttribLocation(program, "a_center_n_zoom")
    glVertexAttribPointer(center_n_zoom, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(44))
    glEnableVertexAttribArray(center_n_zoom)

    wx_wy = glGetAttribLocation(program, "wx_wy_maxitr")
    glVertexAttribPointer(wx_wy, 4, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(56))
    glEnableVertexAttribArray(wx_wy)

###########################################################################################################################
### screenshot-ing functions
def saveImageFromFBO(width, height):
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels (0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.new("RGB", (width, height), (0, 0, 0))
    image.frombytes(data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save (f'{round(timeit.default_timer(),7)}4thtry.bmp')
    image.save (f'{round(timeit.default_timer(),7)}4thtry.png')
    image.save (f'{round(timeit.default_timer(),7)}4thtry.jpg')
    image.save (f'{round(timeit.default_timer(),7)}4thtry.tiff')


def Screenshot():
    print("Printing screenshot...")
    # Setup framebuffer
    framebuffer = glGenFramebuffers (1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    # Setup colorbuffer
    colorbuffer = glGenRenderbuffers (1)
    glBindRenderbuffer(GL_RENDERBUFFER, colorbuffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, fbWidth, fbHeight)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, colorbuffer)

    # Setup depthbuffer
    depthbuffer = glGenRenderbuffers (1)
    glBindRenderbuffer(GL_RENDERBUFFER,depthbuffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, fbWidth, fbHeight)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthbuffer)

    # check status
    status = glCheckFramebufferStatus (GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        print( "Error in framebuffer activation")

    glViewport(0, 0, fbWidth, fbHeight)
    # setting shader inputs
    fb_wx = 4
    fb_wy = fb_wx*fbHeight/fbWidth
    shader_inputs = [-1.0, 1.0, 0.0,  # vertex 1 position
                     1111111111.0, 1.0, 0.0,  # vertex 2 position
                     -1.0, -1111111111.0, 0.0,  # vertex 3 position
                     fbWidth, fbHeight,  # width and height of glfw window
                     center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                     fb_wx, fb_wy, # width and height of complex plane
                     maxitr, brightness] # maximum iteration for mandelbrot iteration

    shader_inputs = np.array(shader_inputs, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, shader_inputs.nbytes, shader_inputs, GL_STATIC_DRAW)

    AttribInit()

    glDrawArrays(GL_TRIANGLES, 0, 3)

    saveImageFromFBO(fbWidth, fbHeight)

    glBindFramebuffer(GL_FRAMEBUFFER, GL_NONE)

    glViewport(0, 0, int(xmax), int(ymax))

###########################################################################################################################
### Main

# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(int(xmax), int(ymax), "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position on screen 34 is height of window top bar
glfw.set_window_pos(window, 0, 34)
glfw.make_context_current(window)

# set Vsync to be zero so frame time can go lower than 16.66ms
glfw.swap_interval(0)

# setting all glfw input callbacks
glfw.set_key_callback(window, key_input_clb)
glfw.set_cursor_pos_callback(window, cursor_pos_clb)
glfw.set_mouse_button_callback(window, mouse_button_clb)
glfw.set_scroll_callback(window, scroll_clb)

# compiling and using shader programs
program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
glUseProgram(program)

# frame time variables
frame_times = [0, 0]

# the main application loop
while not glfw.window_should_close(window):
    tic = timeit.default_timer()  # frame timer start
    _   = clock.tick(target_fps)

    # setting shader inputs everyframe
    shader_inputs = [-1.0, 1.0, 0.0,  # vertex 1 position
                     1111111111.0, 1.0, 0.0,  # vertex 2 position
                     -1.0, -1111111111.0, 0.0,  # vertex 3 position
                     xmax, ymax,  # width and height of glfw window
                     center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                     wx, wy, # width and height of complex plane
                     maxitr, brightness] # maximum iteration for mandelbrot iteration

    shader_inputs = np.array(shader_inputs, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, shader_inputs.nbytes, shader_inputs, GL_STATIC_DRAW)

    # initialize attributes everyframe
    AttribInit()

    glfw.poll_events()

    # calling the camera functions to facilitate camera movement
    camera()

    # drawing on the window
    glDrawArrays(GL_TRIANGLES, 0, 3)

    glfw.swap_buffers(window)

    toc = timeit.default_timer()  # frame timer end

    # calculate frame time
    frame_times[0] += toc - tic
    frame_times[1] += 1

    # printing frame time averaged over 50 frames
    if frame_times[1] >= 50:
        print(f'frame time = {round(frame_times[0] / frame_times[1] * 1000, 2)}ms')
        print(f"zoom: {zoom}")
        frame_times[0], frame_times[1] = 0, 0

    # screenshot sequence
    if scrcap:
        scrcap = False
        Screenshot()


# terminate glfw, free up allocated resources
glfw.terminate()

to_write = f'center x: {center_x} \n center y: {center_y} \n zoom: {zoom}'
file1.write(to_write)
file1.close()
