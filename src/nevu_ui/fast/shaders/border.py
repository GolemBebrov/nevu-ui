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
uniform int thickness;   

float calculate_dist(vec2 p, vec2 b, vec4 r)
{
    r.xy = (p.x > 0.0) ? r.yz : r.xw;
    r.x  = (p.y > 0.0) ? r.y  : r.x;
    vec2 q = abs(p) - b + r.x;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r.x;
}

void main()
{
    vec2 halfSize = rectSize * 0.5;
    vec2 p = fragTexCoord * rectSize - halfSize;
    
    float d = calculate_dist(p, halfSize, radius);
    float distChange = fwidth(d); 
    
    float alphaShape = 1.0 - smoothstep(0.0, distChange, d);

    float th = float(thickness); 
    
    float borderMix = smoothstep(-th - distChange, -th, d);

    vec4 texColor = texture(texture0, fragTexCoord) * fragColor * colDiffuse;
    vec4 resultColor = mix(texColor, borderColor, borderMix);

    finalColor = vec4(resultColor.rgb, resultColor.a * alphaShape);
}
"""