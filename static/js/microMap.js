/**
 * 60 FPS Canvas Micro-Map Illustration
 * Renders futuristic cyber-grid, moving drone courier, radar sweeps, and live beacons.
 */

export class MicroMapCanvas {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.flightRatio = 0.05; // 0.0 to 1.0
    this.targetFlightRatio = 0.05;
    this.radarAngle = 0;
    this.pulsePhase = 0;
    this.animationFrameId = null;

    if (this.canvas) {
      this.resize();
      window.addEventListener('resize', () => this.resize());
      this.startLoop();
    }
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
  }

  setFlightProgress(ratio) {
    this.targetFlightRatio = Math.max(0.02, Math.min(1.0, ratio));
  }

  startLoop() {
    const render = () => {
      this.update();
      this.draw();
      this.animationFrameId = requestAnimationFrame(render);
    };
    render();
  }

  stopLoop() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }

  update() {
    // Smooth interpolation towards target flight ratio
    this.flightRatio += (this.targetFlightRatio - this.flightRatio) * 0.08;
    this.radarAngle += 0.04;
    this.pulsePhase = (this.pulsePhase + 0.03) % (Math.PI * 2);
  }

  draw() {
    if (!this.ctx || !this.width || !this.height) return;
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    ctx.clearRect(0, 0, w, h);

    // 1. Draw cyber background grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
    ctx.lineWidth = 1;
    const gridSize = 24;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // 2. Trajectory waypoints
    const startX = 50;
    const startY = h - 60;
    const endX = w - 60;
    const endY = 60;
    const controlX = w * 0.45;
    const controlY = h * 0.15;

    // Draw flight corridor path (dashed curved bezier)
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.quadraticCurveTo(controlX, controlY, endX, endY);
    ctx.strokeStyle = 'rgba(204, 255, 0, 0.2)';
    ctx.lineWidth = 3;
    ctx.setLineDash([6, 6]);
    ctx.stroke();
    ctx.setLineDash([]);

    // 3. Completed path glow line
    const t = this.flightRatio;
    const currentX = (1 - t) * (1 - t) * startX + 2 * (1 - t) * t * controlX + t * t * endX;
    const currentY = (1 - t) * (1 - t) * startY + 2 * (1 - t) * t * controlY + t * t * endY;

    // 4. Kitchen Launch Pad Beacon (Start)
    ctx.fillStyle = '#1A1A24';
    ctx.beginPath();
    ctx.arc(startX, startY, 14, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.fillStyle = '#CCFF00';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('🍳 KITCHEN', startX, startY + 28);

    // 5. Customer Landing Zone Beacon (End)
    const pulseRadius = 14 + Math.sin(this.pulsePhase) * 8;
    ctx.strokeStyle = `rgba(0, 240, 255, ${0.8 - (pulseRadius - 14) / 10})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(endX, endY, pulseRadius, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = '#00F0FF';
    ctx.beginPath();
    ctx.arc(endX, endY, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#00F0FF';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('🛸 DESTINATION', endX, endY - 18);

    // 6. Drone / Courier
    this.drawDrone(ctx, currentX, currentY);

    // 7. Radar sweep at current drone position
    ctx.save();
    ctx.translate(currentX, currentY);
    ctx.strokeStyle = 'rgba(204, 255, 0, 0.4)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(0, 0, 32, 0, Math.PI * 2);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(this.radarAngle) * 32, Math.sin(this.radarAngle) * 32);
    ctx.strokeStyle = 'rgba(204, 255, 0, 0.8)';
    ctx.stroke();
    ctx.restore();
  }

  drawDrone(ctx, x, y) {
    ctx.save();
    ctx.translate(x, y);

    // Thruster glow
    const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, 18);
    grad.addColorStop(0, 'rgba(204, 255, 0, 0.8)');
    grad.addColorStop(1, 'transparent');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(0, 0, 18, 0, Math.PI * 2);
    ctx.fill();

    // Quadcopter arms
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-12, -12);
    ctx.lineTo(12, 12);
    ctx.moveTo(12, -12);
    ctx.lineTo(-12, 12);
    ctx.stroke();

    // Rotors
    ctx.fillStyle = 'rgba(204, 255, 0, 0.85)';
    [[-12, -12], [12, -12], [12, 12], [-12, 12]].forEach(([rx, ry]) => {
      ctx.beginPath();
      ctx.arc(rx, ry, 4, 0, Math.PI * 2);
      ctx.fill();
    });

    // Central Pod
    ctx.fillStyle = '#0F0F12';
    ctx.beginPath();
    ctx.arc(0, 0, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#CCFF00';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.restore();
  }
}
