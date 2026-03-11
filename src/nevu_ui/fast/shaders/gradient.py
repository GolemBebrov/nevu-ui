
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
    uniform float angle;
    uniform vec2 centerPos;
    uniform vec4 colors[MAX_COLORS];
    uniform float stops[MAX_COLORS];
    uniform int colorCount;
    uniform float alpha;
    uniform vec2 size;

    vec4 getColor(float t) {
        if (colorCount <= 1) return colors[0];
        if (t <= stops[0]) return colors[0];
        for (int i = 0; i < colorCount - 1; i++) {
            if (t >= stops[i] && t <= stops[i+1]) {
                float range = stops[i+1] - stops[i];
                if (range <= 0.0) return colors[i+1];
                float local_t = (t - stops[i]) / range;
                return mix(colors[i], colors[i+1], local_t);
            }
        }
        return colors[colorCount - 1];
    }

    float getLinearProgress(vec2 uv) {
        float rad = radians(angle);
        vec2 dir = vec2(cos(rad), sin(rad));
        float length = abs(cos(rad)) + abs(sin(rad));
        vec2 centered_uv = uv - 0.5;
        return dot(centered_uv, dir) / length + 0.5;
    }

    float getRadialProgress(vec2 uv) {
        vec2 pixelPos = uv * size;
        vec2 center = centerPos * size;
        float dist = distance(pixelPos, center);
        
        float d1 = distance(vec2(0.0, 0.0), center);
        float d2 = distance(vec2(size.x, 0.0), center);
        float d3 = distance(vec2(0.0, size.y), center);
        float d4 = distance(vec2(size.x, size.y), center);
        float maxRadius = max(max(d1, d2), max(d3, d4));
        
        if (maxRadius <= 0.0) return 0.0;
        return dist / maxRadius;
    }

    void main() {
        float progress = 0.0;
        if (gradientType == 0) progress = getLinearProgress(fragTexCoord);
        else progress = getRadialProgress(fragTexCoord);
        
        vec4 color = getColor(progress);
        finalColor = vec4(color.rgb, color.a * alpha);
    }
    """