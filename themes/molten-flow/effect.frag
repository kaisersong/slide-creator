#version 300 es
precision highp float;
uniform vec2 uResolution;
uniform float uPhase;
out vec4 outColor;

mat2 rotate(float angle) { float c=cos(angle),s=sin(angle);return mat2(c,-s,s,c); }
float metal(vec3 p) {
  p.xy=rotate(-0.48+sin(uPhase)*0.20)*p.xy;
  p.yz=rotate(0.95+cos(uPhase)*0.15)*p.yz;
  float angle=atan(p.z,p.x);
  float radius=0.89+0.09*sin(angle*3.0+sin(uPhase));
  vec2 crossSection=vec2(length(p.xz)-radius,p.y);
  crossSection=rotate(angle*1.5+uPhase)*crossSection;
  return (length(crossSection/vec2(0.24,0.082))-1.0)*0.082;
}
vec3 normalAt(vec3 p) {
  const float e=0.002;
  vec2 k=vec2(1.0,-1.0);
  return normalize(k.xyy*metal(p+k.xyy*e)+k.yyx*metal(p+k.yyx*e)
    +k.yxy*metal(p+k.yxy*e)+k.xxx*metal(p+k.xxx*e));
}
vec3 environment(vec3 direction) {
  vec3 warm=vec3(1.00,0.43,0.065);
  float softbox=pow(max(dot(direction,normalize(vec3(-0.25,0.7,1.0))),0.0),4.0);
  float strip=exp(-pow((direction.x+0.22)/0.13,2.0))*smoothstep(-0.3,0.6,direction.z);
  float edge=pow(max(dot(direction,normalize(vec3(0.1,-0.8,0.5))),0.0),22.0);
  return vec3(0.025,0.008,0.002)+warm*0.12
    +vec3(1.0,0.93,0.76)*softbox*3.0+vec3(1.0,0.84,0.45)*strip*7.5
    +vec3(1.0,0.19,0.025)*edge*3.0;
}
void main() {
  vec2 uv=gl_FragCoord.xy/uResolution;
  float aspect=uResolution.x/uResolution.y;
  vec2 screen=(uv-vec2(0.76,0.50))*vec2(aspect,1.0);
  vec3 background=vec3(0.035,0.018,0.020);
  background+=vec3(0.15,0.022,0.003)*exp(-dot(screen,screen)*5.0);
  vec3 eye=vec3(0.0,0.0,3.6);
  vec3 ray=normalize(vec3(screen*2.8,-3.0));
  // Restrict ray marching to the object's bounding sphere.
  float b=dot(eye,ray);
  float discriminant=b*b-dot(eye,eye)+1.22*1.22;
  vec3 color=background;
  if (discriminant>0.0) {
    float distance=max(0.0,-b-sqrt(discriminant));
    float end=-b+sqrt(discriminant);
    bool hit=false;
    vec3 point=eye+ray*distance;
    for (int i=0;i<72;i++) {
      point=eye+ray*distance;
      float stepSize=metal(point);
      if (stepSize<0.0012) { hit=true;break; }
      distance+=max(stepSize,0.001);
      if (distance>end) break;
    }
    if (hit) {
      vec3 n=normalAt(point);
      vec3 reflection=reflect(ray,n);
      float fresnel=pow(1.0-max(dot(n,-ray),0.0),3.0);
      float diffuse=max(dot(n,normalize(vec3(-0.8,0.9,1.1))),0.0);
      float folds=0.88+0.12*sin(point.y*28.0+point.x*12.0+sin(uPhase));
      color=environment(reflection)*vec3(1.0,0.88,0.62)*folds;
      color+=vec3(0.95,0.25,0.018)*diffuse*0.30;
      color+=vec3(1.0,0.72,0.23)*fresnel*0.44;
      color=color/(color+vec3(0.55));
      color=pow(color,vec3(0.82));
    }
  }
  outColor=vec4(color,1.0);
}
