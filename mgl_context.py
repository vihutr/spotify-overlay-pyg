from array import array

import moderngl as mgl
from config import SETTINGS

vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 uvs;
out vec4 f_color;

void main() {
    // vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + time) * 0.01, uvs.y);
    f_color = vec4(texture(tex, uvs).rgb, 1.0);
}
'''

class ModernGLHandler:
    def __init__(self):
        self.ctx = mgl.create_context()
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # position (x, y), uv coords (x, y)
            -1.0, 1.0, 0.0, 0.0,    # topleft
            1.0, 1.0, 1.0, 0.0,     # topright
            -1.0, -1.0, 0.0, 1.0,   # bottomleft
            1.0, -1.0, 1.0, 1.0,    # bottomright
        ]))

        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
        self.render_obj = self.ctx.vertex_array(self.program,
                                                [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])

        self.window_tex = self.ctx.texture(SETTINGS.win_size, 4)
        self.window_tex.filter = (mgl.NEAREST, mgl.NEAREST)
        self.window_tex.swizzle = 'BGRA'

    def render(self, surf):
        self.window_tex.write(surf.get_view('1'))
        self.window_tex.use(0)
        self.program['tex'] = 0
        self.render_obj.render(mode=mgl.TRIANGLE_STRIP)

    def release(self):
        self.window_text.release()
