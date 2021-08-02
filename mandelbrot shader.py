import glfw, timeit, sys
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from PIL import Image


file1 = open("to_draw.txt", "w")
file1.write('hey \n')
# viewer parameters
fbWidth, fbHeight = int(1920), int(1080)
xmax, ymax = 1920.0, 1080.0                                 # Width and height (respectively) of display window
center_xt, center_yt, zoomt = -0.5, 0.0, 1.01               # Target center and target zoom
center_x, center_y, zoom = center_xt, center_yt, zoomt      # Actual center and actual zoom
wx = 4                                                      # Width of complex plane displayed
wy = wx * ymax / xmax                                       # Height of complex plane displayed
newpos = [0, 0]                                             # Mouse pixel coordinate
maxitr, brightness = 256.0, 6.0                             # Maximum iteration, brightness
zoomin, zoomout, moveup, movedown, moveleft, moveright, newmouse, scrcap = False, False, False, False, False, False, False, False

# making all the glfw callback functions for keyboard and mouse inputs
def mouse_button_clb(window, button, action, mode):
    global center_xt, center_yt, newpos, newmouse
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        newmouse = True
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
        newmouse = False

def cursor_pos_clb(window, xpos, ypos):
    mouse_coord(xpos, ypos)

def scroll_clb(window, xoffset, yoffset):
    global zoomin, zoomout
    pass
    # if int(yoffset) > 0.5:
    #     zoomin = True
    # elif int(yoffset) < -0.5:
    #     zoomout = True

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

    # if key == glfw.KEY_W and action == glfw.PRESS:
    #     moveup = True
    # if key == glfw.KEY_W and action == glfw.RELEASE:
    #     moveup = False
    #
    # if key == glfw.KEY_A and action == glfw.PRESS:
    #     moveleft = True
    # if key == glfw.KEY_A and action == glfw.RELEASE:
    #     moveleft = False
    #
    # if key == glfw.KEY_S and action == glfw.PRESS:
    #     movedown = True
    # if key == glfw.KEY_S and action == glfw.RELEASE:
    #     movedown = False
    #
    # if key == glfw.KEY_D and action == glfw.PRESS:
    #     moveright = True
    # if key == glfw.KEY_D and action == glfw.RELEASE:
    #     moveright = False

# making all the keyboard and mouse actions
def kbcamera():
    """
    keyboard controls for camera, sets the zoom levels by q and e keys for zooming in and out respectively
    :return:
    """
    global center_x, center_y, zoom, zoomt, zoomin, zoomout, moveup, movedown, moveleft, moveright

    dz = zoomt - zoom
    zoom += dz*0.03
    if zoomin:
        zoomt *= 1.015
        # zoomin = False
    if zoomout:
        zoomt *= 1 / 1.015
        # zoomout = False
    # if moveup:
    #     center_yt += move_size
    #     # moveup = False
    # if movedown:
    #     center_yt -= move_size
    #     # movedown = False
    # if moveright:
    #     center_xt += move_size
    #     # moveright = False
    # if moveleft:
    #     center_xt -= move_size
    #     # moveleft = False

def mouse_coord(xpos, ypos):
    """
    setting the mouse coordinates every frame
    :param xpos:
    :param ypos:
    :return:
    """
    global newpos
    newpos = [xpos, ypos + 16]

def mscamera():
    """
    mouse controls for camera, moving the center of the window to where user clicks on the window
    :return:
    """
    global center_x, center_y, zoomt, zoom, zoomin, zoomout, center_xt, center_yt

    dx = center_xt - center_x
    dy = center_yt - center_y

    center_x += dx * 0.05
    center_y += dy * 0.05

    if newmouse:
        center_xt += 0.02*(newpos[0] / xmax - 0.5) * wx / zoom
        center_yt -= 0.02*(newpos[1] / ymax - 0.5) * wy / zoom
        # print(13434)

    # if zoomin:
    #     zoomt *= 1.2
    #     # zoomin = False
    # elif zoomout:
    #     zoomt *= 1/1.2
    #     # zoomout = False
    #
    # dz = zoomt - zoom
    # print(dz, zoomt)
    # zoom += dz * 0.01
    # if dz < (0.1 * zoomt):
    #     zoomt = zoom


# glsl code for vertex shader, the vertex shader is responsible for setting the vertex properties on screen,
# and for passing the out data to the fragment shader
vertex_src = """
# version 400
in vec3 a_position;
in vec2 a_dims;
in vec3 a_center_n_zoom;
in vec4 wx_wy_maxitr;
out vec2 scr_dim;
out vec3 center_n_zoom;
out vec2 wx_wy2;
out vec2 maxitr;
void main()
{
    gl_Position = vec4(a_position, 1.0);
    scr_dim = a_dims;
    center_n_zoom = a_center_n_zoom;
    wx_wy2 = vec2(wx_wy_maxitr.x, wx_wy_maxitr.y);
    maxitr = vec2(wx_wy_maxitr.z, wx_wy_maxitr.w);
}
"""

# glsl code for fragment shader, the fragment shader is responsible for colouring each and every pixel on the window
fragment_src = """
# version 400
in vec2 scr_dim;
in vec3 center_n_zoom;
in vec2 wx_wy2;
in vec2 maxitr;
out vec4 out_color;
void main()
{   
    int itr = 0;
    int itr_limit = int(maxitr.x);
    float brightness = maxitr.y;
    float abs = 0.0;
    float abs_lim = 16.0;
    float converged = 0;

    float zoom = center_n_zoom.z;
    vec2 center = vec2(center_n_zoom.x, center_n_zoom.y);
    vec2 xy = vec2(gl_FragCoord.x, gl_FragCoord.y);
    vec2 z = vec2(0.0, 0.0);
    vec2 zt = vec2(0.0, 0.0);
    
    vec4 clr_vec = vec4(0.0, 0.0, 0.0, 0.0);
    for(int aae=0; aae<2; aae++)
    {   
        for(int bae=0; bae<2; bae++)
        {   
            vec2 aa = vec2(aae, bae);
            vec2 c = ((xy-1.0+aa*0.5)/scr_dim-0.5)*wx_wy2/zoom+center;

            while (itr<itr_limit && abs<abs_lim)
            {   
                zt = z;
                z = vec2(zt.x* zt.x - zt.y*zt.y + c.x, 
                         2* zt.x*zt.y + c.y);

                abs = z.x*z.x + z.y*z.y;
                itr++;
            }
            converged = int(abs<abs_lim);
            float multiplier = -1.0/(1.0+exp(itr/18.0-2.0))+0.89;
            
            clr_vec.x = clr_vec.x + 0.25*itr/itr_limit*int(itr<=itr_limit)+converged;
            clr_vec.y = clr_vec.y + 0.7*itr/itr_limit*int(itr<=itr_limit)+converged;
            clr_vec.z = clr_vec.z + 1.0*itr/itr_limit*int(itr<=itr_limit)+converged;
            itr = 0;
        }
    }
    clr_vec = clr_vec/4.0*brightness;
    clr_vec.w = 1.0;

    if (xy.x > 959 && xy.x < 961)
    {   
        if (xy.y > 529 && xy.y < 551)
        {
            out_color = clr_vec;
        } else
        {
        out_color = clr_vec;
        }
    } else if (xy.y > 539 && xy.y < 541)
    {   
        if (xy.x > 949 && xy.x < 971)
        {
            out_color = clr_vec;
        } else
        {
        out_color = clr_vec;
        }
    } else 
    {
        out_color = clr_vec;
    }
}
"""

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

def saveImageFromFBO(width, height):
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels (0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.new("RGB", (width, height), (0, 0, 0))
    image.frombytes(data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save ('test.tiff')


def setupSelfDefineFBO(program):
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
    shader_inputs = [-1111111.0, 1111111.0, 0.0,  # vertex 1 position
                     1111111111.0, 1111111.0, 0.0,  # vertex 2 position
                     -1111111.0, -1111111111.0, 0.0,  # vertex 3 position
                     fbWidth, fbHeight,  # width and height of glfw window
                     center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                     wx, wy, # width and height of complex plane
                     maxitr, brightness] # maximum iteration for mandelbrot iteration
    # print(maxitr)
    shader_inputs = np.array(shader_inputs, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, shader_inputs.nbytes, shader_inputs, GL_STATIC_DRAW)

    # setting up all the attribpointers every frame
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

    glDrawArrays(GL_TRIANGLES, 0, 3)

    saveImageFromFBO(fbWidth, fbHeight)

    glBindFramebuffer(GL_FRAMEBUFFER, GL_NONE)

    glViewport(0, 0, int(xmax), int(ymax))

def Draw():
    # setting shader inputs
    shader_inputs = [-1.0, 1.0, 0.0,  # vertex 1 position
                     1111111111.0, 1.0, 0.0,  # vertex 2 position
                     -1.0, -1111111111.0, 0.0,  # vertex 3 position
                     xmax, ymax,  # width and height of glfw window
                     center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                     wx, wy, # width and height of complex plane
                     maxitr, brightness] # maximum iteration for mandelbrot iteration
    # print(maxitr)
    shader_inputs = np.array(shader_inputs, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, shader_inputs.nbytes, shader_inputs, GL_STATIC_DRAW)

    # setting up all the attribpointers every frame
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

    glfw.poll_events()

    # running the camera functions to facilitate camera movement
    kbcamera()
    mscamera()

    # drawing on the window
    glDrawArrays(GL_TRIANGLES, 0, 3)

# frame time variables
frame_times = [0, 0]

# the main application loop
while not glfw.window_should_close(window):
    # move_size = wy/zoom * 0.005

    tic = timeit.default_timer()  # frame timer start

    # setting shader inputs
    shader_inputs = [-1.0, 1.0, 0.0,  # vertex 1 position
                     1111111111.0, 1.0, 0.0,  # vertex 2 position
                     -1.0, -1111111111.0, 0.0,  # vertex 3 position
                     xmax, ymax,  # width and height of glfw window
                     center_x, center_y, zoom,  # complex coordinate of center of complex plane, level of zoom
                     wx, wy, # width and height of complex plane
                     maxitr, brightness] # maximum iteration for mandelbrot iteration
    # print(maxitr)
    shader_inputs = np.array(shader_inputs, dtype=np.float32)
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, shader_inputs.nbytes, shader_inputs, GL_STATIC_DRAW)

    # setting up all the attribpointers every frame
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

    glfw.poll_events()

    # running the camera functions to facilitate camera movement
    kbcamera()
    mscamera()

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
        frame_times[0], frame_times[1] = 0, 0

    if scrcap:
        scrcap = False
        setupSelfDefineFBO(program)


# terminate glfw, free up allocated resources
glfw.terminate()

to_write = f'{center_x} \n {center_y} \n {zoom}'
file1.write(to_write)
file1.close()