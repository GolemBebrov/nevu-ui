class GlassyBorderShader:
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

float sdf_rounded_box(vec2 p, vec2 b, vec4 r)
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

vec2 get_smooth_grad(vec2 p, vec2 halfSize, vec4 radius)
{
    float minSize = min(halfSize.x, halfSize.y);
    vec4 normRadius = max(radius, vec4(minSize * 0.25));

    vec2 eps = vec2(1.5, 1.5);
    float d_r = sdf_rounded_box(p + vec2(eps.x, 0.0), halfSize, normRadius);
    float d_l = sdf_rounded_box(p - vec2(eps.x, 0.0), halfSize, normRadius);
    float d_u = sdf_rounded_box(p + vec2(0.0, eps.y), halfSize, normRadius);
    float d_d = sdf_rounded_box(p - vec2(0.0, eps.y), halfSize, normRadius);

    vec2 grad = vec2(d_r - d_l, d_u - d_d);
    float gradLen = length(grad);
    return (gradLen > 0.0001) ? grad / gradLen : vec2(0.0);
}

void main()
{
    vec2 halfSize = rectSize * 0.5;
    vec2 p = fragTexCoord * rectSize - halfSize;

    float d = sdf_rounded_box(p, halfSize, radius);
    float aa = max(fwidth(d), 1e-4) * 0.707;
    float alpha = smoothstep(-aa, aa, -d);

    if (alpha <= 0.0) {
        discard;
    }

    vec2 grad = get_smooth_grad(p, halfSize, radius);

    vec2 normP = p / halfSize;
    float centerDistSq = dot(normP, normP);
    vec2 domeDistortion = normP * (1.0 - clamp(centerDistSq, 0.0, 1.0)) * 0.12;

    float distInside = -d;
    float bevelSize = min(halfSize.x, halfSize.y) * 0.25;
    float edgeFactor = clamp(1.0 - (distInside / bevelSize), 0.0, 1.0);
    float edgeProfile = pow(edgeFactor, 1.8);
    vec2 edgeDistortion = grad * edgeProfile * 0.18;

    vec2 totalDistortion = domeDistortion - edgeDistortion;

    vec2 uvG = clamp(fragTexCoord + totalDistortion, vec2(0.001), vec2(0.999));
    vec2 uvR = clamp(fragTexCoord + totalDistortion * 1.35, vec2(0.001), vec2(0.999));
    vec2 uvB = clamp(fragTexCoord + totalDistortion * 0.65, vec2(0.001), vec2(0.999));

    vec4 blurredColor = vec4(0.0);
    float totalWeight = 0.0;
    float blurRadius = 14.0 / max(rectSize.x, rectSize.y);

    const int SAMPLES = 12;
    for (int i = 0; i < SAMPLES; i++)
    {
        float fi = float(i);
        float angle = fi * 2.39996323;
        float dist = sqrt((fi + 0.5) / float(SAMPLES)) * blurRadius;
        vec2 offset = vec2(cos(angle), sin(angle)) * dist;

        float r = texture(texture0, uvR + offset).r;
        float g = texture(texture0, uvG + offset).g;
        float b = texture(texture0, uvB + offset).b;
        float a = texture(texture0, uvG + offset).a;

        float w = 1.0 - (dist / blurRadius) * 0.5;
        blurredColor += vec4(r, g, b, a) * w;
        totalWeight += w;
    }
    vec4 bg = blurredColor / totalWeight;

    vec3 N = normalize(vec3(-totalDistortion * 4.0, 1.0));
    vec3 lightDir = normalize(vec3(-0.55, 0.75, 0.85));
    vec3 viewDir = vec3(0.0, 0.0, 1.0);
    vec3 H = normalize(lightDir + viewDir);

    float NdotH = max(dot(N, H), 0.0);
    float specSharp = pow(NdotH, 64.0) * 0.85;
    float specSoft  = pow(NdotH, 14.0) * 0.30;
    float fresnel = pow(1.0 - max(dot(N, viewDir), 0.0), 3.0);

    float edgeLight = max(dot(-grad, lightDir.xy), 0.0) * edgeProfile;
    edgeLight = pow(edgeLight, 1.2) * 0.85;

    float edgeShadow = max(dot(grad, lightDir.xy), 0.0) * edgeProfile * 0.20;

    vec3 glassTint = vec3(1.0, 1.0, 1.0);
    vec3 frostedBg = mix(bg.rgb, glassTint, 0.10);

    float edgeFade = smoothstep(0.0, -aa * 2.0, d);

    vec3 glassColor = frostedBg * (1.0 - edgeShadow)
                    + (vec3(specSharp + specSoft)
                    + vec3(edgeLight) * 0.90
                    + glassTint * (fresnel * 0.40)) * edgeFade;

    vec4 glassMat = vec4(glassColor, bg.a) * fragColor * colDiffuse;

    float borderMix = smoothstep(-thickness - aa, -thickness + aa, d);
    vec4 resultColor = mix(glassMat, borderColor, borderMix);

    finalColor = resultColor * alpha;
}
"""
