class LineSdfShader:
    VERTEX_SHADER = """#version 330

in vec3 vertexPosition;
in vec2 vertexTexCoord;
in vec4 vertexColor;

out vec2 fragTexCoord;
out vec4 fragColor;

uniform mat4 mvp;

void main()
{
    fragTexCoord = vertexTexCoord;
    fragColor = vertexColor;
    gl_Position = mvp * vec4(vertexPosition, 1.0);
}
"""

    FRAGMENT_SHADER = """#version 330
in vec2 fragTexCoord;
in vec4 fragColor;

out vec4 finalColor;

uniform vec2 p1;
uniform vec2 p2;
uniform float thickness;
uniform float radius;
uniform vec4 lineColor;
uniform vec2 bboxPos;
uniform vec2 bboxSize;

float sdf_oriented_box(vec2 p, vec2 a, vec2 b, float th, float r)
{
    vec2 ba = b - a;
    float len = length(ba);
    if (len < 1e-5) {
        return length(p - a) - (th * 0.5);
    }
    vec2 u = ba / len;
    vec2 v = vec2(-u.y, u.x);
    vec2 center = (a + b) * 0.5;
    vec2 p_rel = p - center;

    float lx = abs(dot(p_rel, u));
    float ly = abs(dot(p_rel, v));

    float half_len = len * 0.5;
    float half_th = th * 0.5;

    float r_eff = clamp(r, 0.0, min(half_len, half_th));
    vec2 inner_box = vec2(half_len - r_eff, half_th - r_eff);

    vec2 q = vec2(lx, ly) - inner_box;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r_eff;
}

void main()
{
    vec2 pixelPos = bboxPos + fragTexCoord * bboxSize;
    float d = sdf_oriented_box(pixelPos, p1, p2, thickness, radius);
    float aa = max(fwidth(d), 1e-4) * 0.707;
    float alpha = smoothstep(aa, -aa, d);

    if (alpha <= 0.0) {
        discard;
    }

    finalColor = vec4(lineColor.rgb * lineColor.a, lineColor.a) * alpha;
}
"""
