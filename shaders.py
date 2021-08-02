# Shaders code

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
