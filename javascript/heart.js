const canvas = document.getElementById('heartCanvas');
const ctx = canvas.getContext('2d');

const CANVAS_WIDTH = canvas.width;
const CANVAS_HEIGHT = canvas.height;
const CANVAS_CENTER_X = CANVAS_WIDTH / 2;
const CANVAS_CENTER_Y = CANVAS_HEIGHT / 2;
const IMAGE_ENLARGEMENT = 11;
const HEART_COLOR = 'rgb(255, 33, 33)';
const FPS = 20;

function heartFunction(t, shrinkRatio = IMAGE_ENLARGEMENT) {
  const x = 16 * Math.pow(Math.sin(t), 3) * shrinkRatio;
  const y = (13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t)) * shrinkRatio;
  return [x + CANVAS_CENTER_X, -y + CANVAS_CENTER_Y];
}

function scatterInside(x, y, beta = 0.15) {
  const ratioX = beta * Math.log(Math.random());
  const ratioY = beta * Math.log(Math.random());
  const dx = ratioX * (x - CANVAS_CENTER_X);
  const dy = ratioY * (y - CANVAS_CENTER_Y);
  return [x - dx, y - dy];
}

function shrink(x, y, ratio) {
  const force = -1 / Math.pow((Math.pow(x - CANVAS_CENTER_X, 2) + Math.pow(y - CANVAS_CENTER_Y, 2)), 0.6);
  const dx = ratio * force * (x - CANVAS_CENTER_X);
  const dy = ratio * force * (y - CANVAS_CENTER_Y);
  return [x - dx, y - dy];
}

function curve(p) {
  return 2 * (2 * Math.sin(4 * p)) / (2 * Math.PI);
}

function distanceFromCenter(x, y) {
  return Math.sqrt(Math.pow(x - CANVAS_CENTER_X, 2) + Math.pow(y - CANVAS_CENTER_Y, 2));
}

function calculateLightingEffect(distance) {
  // Simulate lighting effect: closer points are brighter
  const maxDistance = Math.sqrt(Math.pow(CANVAS_WIDTH, 2) + Math.pow(CANVAS_HEIGHT, 2)); 
  const brightness = Math.max(0, Math.min(1, 1 - (distance / maxDistance)));
  return `rgb(${Math.floor(255 * brightness)}, ${Math.floor(33 * brightness)}, ${Math.floor(33 * brightness)})`;
}

class Heart {
  constructor(generateFrame = 20) {
    this.points = new Set();
    this.centerDiffusionPoints = new Set();
    this.innerScatteredPoints = new Set();
    this.allPoints = {};
    this.generateFrame = generateFrame;
    this.build(2000);

    for (let frame = 0; frame < generateFrame; frame++) {
      this.calc(frame);
    }
  }

  build(number) {
    for (let i = 0; i < number; i++) {
      const t = Math.random() * Math.PI * 2;
      const [x, y] = heartFunction(t);
      this.points.add(`${x},${y}`);
    }

    [...this.points].forEach(pt => {
      const [x, y] = pt.split(',').map(Number);
      for (let i = 0; i < 3; i++) {
        const [nx, ny] = scatterInside(x, y, 0.05);
        this.points.add(`${nx},${ny}`);
      }
    });

    const pointList = [...this.points].map(pt => pt.split(',').map(Number));

    for (let i = 0; i < 4000; i++) {
      const [x, y] = pointList[Math.floor(Math.random() * pointList.length)];
      const [nx, ny] = scatterInside(x, y, 0.17);
      this.centerDiffusionPoints.add(`${nx},${ny}`);
    }

    this.innerScatterPoints();
    for (let i = 0; i < 3500; i++) {
      const t = Math.random() * Math.PI * 2;
      let [x, y] = heartFunction(t, 7 + 3.5 * Math.random());
      x += Math.random() * 16 - 8;
      y += Math.random() * 16 - 8;
      const distance = distanceFromCenter(x, y);
      const densityFactor = 1 / (1 + distance / 100);
      if (Math.random() < densityFactor) {
        this.innerScatteredPoints.add(`${x},${y}`);
      }
    }
  }

  innerScatterPoints() {
    for (let i = 0; i < 30000; i++) {
      const t = Math.random() * Math.PI * 2;
      let [x, y] = heartFunction(t, 7 + 3.5 * Math.random());
      x += Math.random() * 16 - 8;
      y += Math.random() * 16 - 8;
      const distance = distanceFromCenter(x, y);
      const densityFactor = 1 / (1 + (distance * distance) / 40);
      if (Math.random() < densityFactor) {
        this.innerScatteredPoints.add(`${x},${y}`);
      }
    }
  }

  calcPosition(x, y, ratio) {
    const force = 1 / Math.pow(Math.pow(x - CANVAS_CENTER_X, 2) + Math.pow(y - CANVAS_CENTER_Y, 2), 0.520);
    const dx = ratio * force * (x - CANVAS_CENTER_X) + (Math.random() * 2 - 1);
    const dy = ratio * force * (y - CANVAS_CENTER_Y) + (Math.random() * 2 - 1);
    return [x - dx, y - dy];
  }

  calc(frame) {
    const ratio = 10 * curve(frame / 20 * Math.PI);
    const haloRadius = 4 + 6 * (1 + curve(frame / 10 * Math.PI));
    const haloNumber = 3000 + 4000 * Math.abs(Math.pow(curve(frame / 10 * Math.PI), 2));

    const allPoints = [];
    const heartHaloPoints = new Set();

    for (let i = 0; i < haloNumber; i++) {
      const t = Math.random() * Math.PI * 2;
      let [x, y] = heartFunction(t, 11.6);
      [x, y] = shrink(x, y, haloRadius);
      const key = `${Math.round(x)},${Math.round(y)}`;
      if (!heartHaloPoints.has(key)) {
        heartHaloPoints.add(key);
        x += Math.random() * 28 - 14;
        y += Math.random() * 28 - 14;
        const size = [1, 2, 3][Math.floor(Math.random() * 3)];
        allPoints.push({ x, y, size });
      }
    }

    [...this.points].forEach(pt => {
      let [x, y] = pt.split(',').map(Number);
      [x, y] = this.calcPosition(x, y, ratio);
      const size = Math.floor(Math.random() * 3) + 1;
      const distance = distanceFromCenter(x, y);
      const color = calculateLightingEffect(distance);
      allPoints.push({ x, y, size, color });
    });

    [...this.centerDiffusionPoints].forEach(pt => {
      let [x, y] = pt.split(',').map(Number);
      [x, y] = this.calcPosition(x, y, ratio);
      const size = Math.floor(Math.random() * 2) + 1;
      const distance = distanceFromCenter(x, y);
      const color = calculateLightingEffect(distance);
      allPoints.push({ x, y, size, color });
    });

    [...this.innerScatteredPoints].forEach(pt => {
      let [x, y] = pt.split(',').map(Number);
      [x, y] = this.calcPosition(x, y, ratio);
      const size = [1, 2][Math.floor(Math.random() * 2)];
      const distance = distanceFromCenter(x, y);
      const color = calculateLightingEffect(distance);
      allPoints.push({ x, y, size, color });
    });

    this.allPoints[frame] = allPoints;
  }

  render(ctx, frame) {
    this.allPoints[frame % this.generateFrame].forEach(pt => {
      ctx.fillStyle = pt.color || HEART_COLOR;
      ctx.fillRect(pt.x, pt.y, pt.size, pt.size);
    });
  }
}

const heart = new Heart(20);
let frame = 1;

function animate() {
  ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  heart.render(ctx, frame);
  frame++;
  setTimeout(() => {
    requestAnimationFrame(animate);
  }, 1000 / FPS);
}

animate();
