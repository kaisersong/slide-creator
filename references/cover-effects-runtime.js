// Shared lifecycle for the Molten Flow and Stellar Vortex cover-only effects.
// Embedded in each starter at build time; generated HTML has no runtime imports.
(function () {
  "use strict";
  const definition = window.__coverEffectDefinition;
  const canvas = document.getElementById("cover-effect-canvas");
  const cover = document.getElementById("slide-1");
  if (!definition || !canvas || !cover) return;
  const vertexCode = `#version 300 es
void main() {
  float x=float((gl_VertexID << 1) & 2);
  float y=float(gl_VertexID & 2);
  gl_Position=vec4(x*2.0-1.0,y*2.0-1.0,0.0,1.0);
}`;
  class CoverEffectController {
    constructor() {
      this.ready=false; this.failed=false; this.active=false; this.contextLost=false;
      this.rafId=0; this.drawCount=0; this.lastFrame=0; this.elapsed=0; this.fixedTime=null;
      this.printing=false; this.pageHidden=false; this.reason=null; this.gl=null;
      this.motion=matchMedia("(prefers-reduced-motion: reduce)");
      this.frame=now => {
        this.rafId=0;
        if (!this.shouldDraw()) { this.sync(); return; }
        if (!this.lastFrame || now-this.lastFrame>=32) {
          if (this.lastFrame) this.elapsed+=Math.min(now-this.lastFrame,100)/1000;
          this.lastFrame=now; this.draw();
        }
        this.start();
      };
      this.bind(); this.sync();
    }
    suspended() {
      return document.hidden || this.pageHidden || this.printing || this.motion.matches || this.contextLost || document.body.classList.contains("presenting-black");
    }
    shouldDraw() { return this.ready && this.active && !this.failed && !this.suspended(); }
    isCoverActive() {
      if (document.body.classList.contains("presenting")) return cover.classList.contains("p-on");
      if (!cover.classList.contains("visible") && document.querySelector(".slide.visible")) return false;
      const rect=cover.getBoundingClientRect();
      return rect.height>1 && rect.top<=innerHeight/2 && rect.bottom>innerHeight/2;
    }
    stop() {
      if (this.rafId) cancelAnimationFrame(this.rafId);
      this.rafId=0; this.lastFrame=0;
    }
    start() {
      if (this.shouldDraw() && this.fixedTime===null && !this.rafId) this.rafId=requestAnimationFrame(this.frame);
    }
    dispose() {
      if (this.gl && this.program) this.gl.deleteProgram(this.program);
      if (this.gl && this.vao) this.gl.deleteVertexArray(this.vao);
      this.program=null; this.vao=null;
    }
    fallback(reason) {
      this.failed=true; this.ready=false; this.reason=reason; this.stop(); this.dispose();
      canvas.dataset.fallbackReason=reason; canvas.hidden=true;
      document.body.dataset.coverEffectReady="false";
    }
    init() {
      if (this.ready || this.failed || this.contextLost) return;
      let vertex=null,fragment=null;
      try {
        const gl=canvas.getContext("webgl2",{alpha:false,antialias:false,depth:false,stencil:false,powerPreference:"low-power"});
        if (!gl) throw new Error("webgl2-unavailable");
        this.gl=gl;
        const compile=(type,code) => {
          const shader=gl.createShader(type);
          gl.shaderSource(shader,code);gl.compileShader(shader);
          if (!gl.getShaderParameter(shader,gl.COMPILE_STATUS)) {
            gl.deleteShader(shader);throw new Error("shader-compilation-failed");
          }
          return shader;
        };
        vertex=compile(gl.VERTEX_SHADER,vertexCode);
        fragment=compile(gl.FRAGMENT_SHADER,definition.fragment);
        this.program=gl.createProgram();
        gl.attachShader(this.program,vertex);gl.attachShader(this.program,fragment);gl.linkProgram(this.program);
        if (!gl.getProgramParameter(this.program,gl.LINK_STATUS)) throw new Error("program-link-failed");
        this.resolution=gl.getUniformLocation(this.program,"uResolution");
        this.phase=gl.getUniformLocation(this.program,"uPhase");
        this.vao=gl.createVertexArray();this.ready=true;
      } catch (error) { this.fallback(error.message || "initialization-failed"); }
      finally {
        if (this.gl && vertex) this.gl.deleteShader(vertex);
        if (this.gl && fragment) this.gl.deleteShader(fragment);
      }
    }
    resize() {
      const rect=canvas.getBoundingClientRect();
      if (rect.width<2 || rect.height<2) return false;
      const ratio=Math.min(devicePixelRatio || 1,1.25)*(definition.resolutionScale || 1);
      const limit=Math.min(4096,this.gl.getParameter(this.gl.MAX_TEXTURE_SIZE));
      const width=Math.max(2,Math.min(limit,Math.round(rect.width*ratio)));
      const height=Math.max(2,Math.min(limit,Math.round(rect.height*ratio)));
      if (canvas.width!==width) canvas.width=width;
      if (canvas.height!==height) canvas.height=height;
      return true;
    }
    draw() {
      if (!this.shouldDraw()) return;
      try {
        const gl=this.gl;
        if (gl.isContextLost()) return;
        const seconds=this.fixedTime===null ? this.elapsed : this.fixedTime;
        const phase=(Math.max(0,seconds)*Math.PI*2/(definition.period || 36))%(Math.PI*2);
        gl.viewport(0,0,canvas.width,canvas.height);gl.useProgram(this.program);gl.bindVertexArray(this.vao);
        gl.uniform2f(this.resolution,canvas.width,canvas.height);gl.uniform1f(this.phase,phase);
        gl.drawArrays(gl.TRIANGLES,0,3);this.drawCount++;
        document.body.dataset.coverEffectReady="true";
      } catch (error) { this.fallback("draw-failed"); }
    }
    sync() {
      this.active=this.isCoverActive();
      if (!this.active || this.suspended() || this.failed) {
        this.stop();canvas.hidden=true;document.body.dataset.coverEffectReady="false";return;
      }
      if (!this.ready) this.init();
      if (!this.ready) return;
      canvas.hidden=false;
      if (!this.resize()) { this.stop();return; }
      if (this.fixedTime!==null) this.stop();
      if (!this.rafId) this.draw();
      this.start();
    }
    bind() {
      canvas.addEventListener("webglcontextlost",event => {
        event.preventDefault();this.contextLost=true;this.ready=false;this.reason="webgl-context-lost";
        this.stop();this.dispose();this.sync();
      });
      canvas.addEventListener("webglcontextrestored",() => {
        this.contextLost=false;this.reason=null;this.sync();
      });
      for (const event of ["scroll","resize","fullscreenchange"]) addEventListener(event,() => this.sync(),{passive:true});
      document.addEventListener("visibilitychange",() => this.sync());
      addEventListener("beforeprint",() => { this.printing=true;this.sync(); });
      addEventListener("afterprint",() => { this.printing=false;this.sync(); });
      addEventListener("pagehide",() => { this.pageHidden=true;this.sync(); });
      addEventListener("pageshow",() => { this.pageHidden=false;this.sync(); });
      this.motion.addEventListener("change",() => this.sync());
      this.observer=new MutationObserver(() => this.sync());
      this.observer.observe(document.body,{attributes:true,attributeFilter:["class"]});
      document.querySelectorAll(".slide").forEach(slide => this.observer.observe(slide,{attributes:true,attributeFilter:["class"]}));
      this.resizeObserver=new ResizeObserver(() => this.sync());this.resizeObserver.observe(cover);
    }
    state() {
      return {effect:definition.name,backend:"webgl2",active:this.active,ready:this.ready,rafActive:Boolean(this.rafId),drawCount:this.drawCount,canvasHidden:canvas.hidden,reason:this.reason,contextLost:this.contextLost,reducedMotion:this.motion.matches};
    }
  }
  const controller=new CoverEffectController();
  window.__coverEffectQA={
    state:() => controller.state(),
    setTime:value => { controller.fixedTime=value;controller.sync();return controller.state(); },
    forceFallback:() => { controller.fallback("qa-forced-fallback");return controller.state(); },
    capturePoster:() => {
      if (!controller.shouldDraw()) throw new Error("Show an eligible, initialized cover before capturing its poster");
      controller.fixedTime=0;controller.sync();
      // Read in the same task as the draw: WebGL otherwise clears its buffer after compositing.
      return canvas.toDataURL("image/webp",0.9);
    },
    loseContext:() => {
      controller.lossExtension=controller.gl && controller.gl.getExtension("WEBGL_lose_context");
      if (controller.lossExtension) controller.lossExtension.loseContext();
      return Boolean(controller.lossExtension);
    },
    restoreContext:() => { if (controller.lossExtension) controller.lossExtension.restoreContext(); },
    sync:() => controller.sync()
  };
})();
