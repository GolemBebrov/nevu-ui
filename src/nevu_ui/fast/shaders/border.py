class BorderShader:
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

uniform sampler2D texture0;
uniform vec4 colDiffuse;

uniform vec2 rectSize; 
uniform vec4 radius;       
uniform vec4 borderColor; 
uniform float thickness;

float calculate_dist(vec2 p, vec2 b, vec4 r)
{
    vec2 s = step(0.0, p);
    
    float currentRadius = mix(
        mix(r.w, r.z, s.x),
        mix(r.x, r.y, s.x),
        s.y
    );
    
    vec2 q = abs(p) - b + currentRadius;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - currentRadius;
}

void main()
{
    vec2 halfSize = rectSize * 0.5;
    vec2 p = fragTexCoord * rectSize - halfSize;
    float d = calculate_dist(p, halfSize, radius);
    float aa = max(fwidth(d), 1e-4) * 0.707;
    float alpha = smoothstep(-aa, aa, -d);
    float borderMix = smoothstep(-thickness - aa, -thickness + aa, d);
    vec4 texColor = texture(texture0, fragTexCoord) * fragColor * colDiffuse;
    vec4 resultColor = mix(texColor, borderColor, borderMix);
    finalColor = resultColor * alpha;
}
"""