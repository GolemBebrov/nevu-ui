
class GradientShader:
    VERTEX_SHADER = """
    #version 330
    in vec3 vertexPosition;
    in vec2 vertexTexCoord;
    in vec4 vertexColor;
    out vec2 fragTexCoord;
    out vec4 fragColor;
    uniform mat4 mvp;
    void main() {
        fragTexCoord = vertexTexCoord;
        fragColor = vertexColor;
        gl_Position = mvp * vec4(vertexPosition, 1.0);
    }
    """

    FRAGMENT_SHADER = """
    #version 330
    in vec2 fragTexCoord;
    in vec4 fragColor;
    out vec4 finalColor;

    #define MAX_COLORS 16

    uniform int gradientType;
    uniform int direction;
    uniform vec3 colors[MAX_COLORS];
    uniform int colorCount;
    uniform float alpha;
    uniform vec2 size;

    vec3 getColor(float t) {
        if (colorCount <= 1) return colors[0];
        t = clamp(t, 0.0, 1.0);
        float step = 1.0 / float(colorCount - 1);
        float pos = t / step;
        int idx = int(pos);
        float fractPart = pos - float(idx);
        if (idx >= colorCount - 1) return colors[colorCount - 1];
        return mix(colors[idx], colors[idx + 1], fractPart);
    }

    float getLinearProgress(vec2 uv) {
        float p = 0.0;
        if (direction == 0) p = uv.x;
        else if (direction == 1) p = 1.0 - uv.x;
        else if (direction == 2) p = uv.y;
        else if (direction == 3) p = 1.0 - uv.y;
        else if (direction == 4) p = (uv.x + uv.y) * 0.5;
        else if (direction == 5) p = 1.0 - (uv.x + uv.y) * 0.5;
        else if (direction == 6) p = (uv.x + (1.0 - uv.y)) * 0.5;
        else if (direction == 7) p = ((1.0 - uv.x) + uv.y) * 0.5;
        return p;
    }

    float getRadialProgress(vec2 uv) {
        
        vec2 pixelPos = uv * size;
        vec2 center = vec2(0.0);
        float w = size.x - 1.0;
        float h = size.y - 1.0;
        
        if (direction == 0) center = vec2(w * 0.5, h * 0.5);
        else if (direction == 1) center = vec2(w * 0.5, 0.0);
        else if (direction == 2) center = vec2(0.0, 0.0);
        else if (direction == 3) center = vec2(w, 0.0);
        else if (direction == 4) center = vec2(w * 0.5, h);
        else if (direction == 5) center = vec2(0.0, h);
        else if (direction == 6) center = vec2(w, h);
        
        float dist = distance(pixelPos, center);
        
        float d1 = distance(vec2(0.0, 0.0), center);
        float d2 = distance(vec2(w, 0.0), center);
        float d3 = distance(vec2(0.0, h), center);
        float d4 = distance(vec2(w, h), center);
        float maxRadius = max(max(d1, d2), max(d3, d4));
        
        if (maxRadius <= 0.0) return 0.0;
        return dist / maxRadius;
    }

    void main() {
        float progress = 0.0;
        if (gradientType == 0) progress = getLinearProgress(fragTexCoord);
        else progress = getRadialProgress(fragTexCoord);
        
        vec3 rgb = getColor(progress);
        finalColor = vec4(rgb, alpha);
    }
    """