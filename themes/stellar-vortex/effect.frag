#version 300 es
precision highp float;
uniform vec2 uResolution;
uniform float uPhase;
out vec4 outColor;
const float TAU=6.28318530718;
float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
vec3 particleLayer(float radius,float angle,float depth,float layer,float phase) {
  float sectors=96.0+layer*30.0;
  float turns=(angle+phase+depth*(0.35+layer*0.05))/TAU;
  vec2 grid=vec2(turns*sectors,depth*(7.0+layer*2.0)-phase/TAU*8.0);
  vec2 cell=floor(grid);
  cell=vec2(mod(cell.x,sectors),mod(cell.y,8.0));
  float seed=hash(cell+layer*13.7);
  vec2 local=fract(grid)-vec2(0.25+seed*0.50,0.22+hash(cell+5.3)*0.56);
  // Distant particles use shorter, dimmer tails to reduce peripheral motion.
  float peripheral=smoothstep(0.28,0.85,radius);
  float tail=exp(-local.x*local.x*(850.0+layer*350.0)-local.y*local.y*mix(28.0,110.0,peripheral));
  float core=exp(-dot(local,local)*1100.0);
  float opacity=step(0.39,seed)*smoothstep(0.03,0.19,radius);
  float energy=(tail*0.54+core*1.30)*opacity*(0.48+seed*0.70)/(1.0+layer*0.30);
  energy*=mix(1.0,0.52,peripheral);
  vec3 starColor=mix(vec3(0.52,0.22,1.0),vec3(0.13,0.76,1.0),seed);
  return starColor*energy+vec3(core*opacity*0.52)*mix(1.0,0.52,peripheral);
}
void main() {
  vec2 uv=gl_FragCoord.xy/uResolution;
  float aspect=uResolution.x/uResolution.y;
  vec2 p=(uv-vec2(0.745,0.50))*vec2(aspect,1.0);
  float radius=max(length(p),0.003);
  float angle=atan(p.y,p.x);
  float depth=log(radius);
  vec3 cyan=vec3(0.13,0.76,1.0);
  vec3 violet=vec3(0.52,0.22,1.0);
  vec3 color=vec3(0.009,0.012,0.036);
  // A 144-second master phase preserves the core's original 24-second orbit.
  // Integer phase multiples keep all speed bands seamless at the master wrap.
  float corePhase=uPhase*6.0;
  float middleWeight=smoothstep(0.22,0.44,radius);
  float outerWeight=smoothstep(0.52,0.82,radius);
  float haze=exp(-radius*4.8)*(0.46+0.30*sin(angle*3.0-depth*3.2-corePhase));
  color+=mix(violet,cyan,sin(angle+corePhase)*0.5+0.5)*haze*0.09;
  // Crossfade complete periodic fields rather than multiplying phase by radius,
  // which would cause an obvious particle jump at the bounded-time reset.
  for (int layer=0;layer<3;layer++) {
    float z=float(layer);
    if (middleWeight<1.0) color+=particleLayer(radius,angle,depth,z,corePhase)*(1.0-middleWeight);
    if (middleWeight>0.0 && outerWeight<1.0) color+=particleLayer(radius,angle,depth,z,uPhase*2.0)*middleWeight*(1.0-outerWeight);
    if (outerWeight>0.0) color+=particleLayer(radius,angle,depth,z,uPhase)*outerWeight;
  }
  // Accretion ribbons and a brilliant compact core anchor the depth field.
  float twist=angle+depth*2.6-corePhase;
  float ribbons=pow(sin(twist*2.0)*0.5+0.5,12.0)*exp(-pow((radius-0.145)/0.095,2.0));
  color+=mix(violet,cyan,sin(twist)*0.5+0.5)*ribbons*0.95;
  float ring=exp(-pow((radius-0.071)/0.009,2.0));
  color+=vec3(0.63,0.88,1.0)*ring*0.65;
  float core=exp(-radius*radius*1400.0);
  color+=vec3(0.87,0.93,1.0)*core*2.0;
  color+=cyan*exp(-radius*radius*50.0)*0.10;
  float flare=exp(-abs(p.y)*380.0)*exp(-abs(p.x)*3.6);
  color+=vec3(0.18,0.51,0.92)*flare*0.24;
  // Sparse distant stars stay still so the motion has a depth reference.
  vec2 dustGrid=uv*vec2(290.0,170.0);
  float dustSeed=hash(floor(dustGrid));
  vec2 dustPoint=fract(dustGrid)-0.5;
  color+=vec3(exp(-dot(dustPoint,dustPoint)*700.0)*step(0.986,dustSeed)*0.24);
  outColor=vec4(color,1.0);
}
