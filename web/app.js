import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = id => document.getElementById(id);
const scene = new THREE.Scene();
scene.background = new THREE.Color('#e4e8df');
scene.fog = new THREE.Fog('#e4e8df', 40, 95);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
$('scene').appendChild(renderer.domElement);
const generator = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
scene.environment = generator.fromScene(room, .04).texture;
room.dispose(); generator.dispose();
const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, .1, 150);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.maxPolarAngle = Math.PI / 2.12;
controls.minDistance = 9; controls.maxDistance = 48;
const ambient = new THREE.HemisphereLight('#fff7e4', '#748779', 2);
scene.add(ambient);
const sun = new THREE.DirectionalLight('#fff1d2', 3.5);
sun.position.set(-12, 23, 12); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -24, right: 24, top: 24, bottom: -24 });
sun.shadow.normalBias = .04; scene.add(sun);

const material = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: .7, ...extra });
const concrete = material('#d7d8ca'), white = material('#eeeedd'), dark = material('#192c2c');
function box(parent, size, position, mat, radius = 0) {
  const mesh = new THREE.Mesh(radius ? new RoundedBoxGeometry(...size, 3, radius) : new THREE.BoxGeometry(...size), mat);
  mesh.position.set(...position); mesh.castShadow = true; mesh.receiveShadow = true;
  parent.add(mesh); return mesh;
}
function text(text, x, y, z, size = 1, color = '#e9eddf') {
  const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 128;
  const ctx = canvas.getContext('2d'); ctx.fillStyle = color; ctx.font = 'bold 70px sans-serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 256, 64);
  const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(size * 4, size), new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false }));
  mesh.rotation.x = -Math.PI / 2; mesh.position.set(x, y, z); scene.add(mesh); return mesh;
}

// Procedural asphalt: no external image assets are needed.
const asphaltCanvas = document.createElement('canvas'); asphaltCanvas.width = asphaltCanvas.height = 256;
const ctx = asphaltCanvas.getContext('2d'); const pixels = ctx.createImageData(256, 256);
let seed = 74;
for (let i = 0; i < pixels.data.length; i += 4) {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  const shade = 64 + (seed % 19);
  pixels.data.set([shade, shade + 5, shade + 3, 255], i);
}
ctx.putImageData(pixels, 0, 0);
const asphaltTexture = new THREE.CanvasTexture(asphaltCanvas);
asphaltTexture.wrapS = asphaltTexture.wrapT = THREE.RepeatWrapping; asphaltTexture.repeat.set(8, 6);
asphaltTexture.colorSpace = THREE.SRGBColorSpace;
box(scene, [200, .2, 200], [0, -.6, 0], material('#dbe2d2'));
box(scene, [26, .55, 20], [0, -.3, 0], concrete, .18);
box(scene, [23.5, .12, 17.5], [0, .01, 0], material('#ffffff', { map: asphaltTexture, roughness: .95 }), .1);
for (const z of [-8.8, 8.8]) box(scene, [24, .25, .24], [0, .13, z], white, .07);
for (const x of [-11.9, 11.9]) box(scene, [.24, .25, 17.7], [x, .13, 0], white, .07);

const slots = [-8, -4, 0, 4, 8];
for (const x of slots) {
  for (const side of [-1, 1]) {
    const z = side * 5.35;
    for (const edge of [-1.65, 1.65]) box(scene, [.06, .02, 5.1], [x + edge, .09, z], white);
    box(scene, [3.35, .02, .06], [x, .09, side * 7.9], white);
    box(scene, [1.7, .17, .22], [x, .16, side * 7.35], concrete, .04);
    text(`A–0${slots.indexOf(x) + 1}`, x, .105, side * 3.25, .32);
  }
}
const mint = material('#68d8af', { emissive: '#279b74', emissiveIntensity: .25 });
box(scene, [3.2, .012, 4.8], [0, .085, -5.35], material('#2b7060'));
for (const x of [-1.64, 1.64]) box(scene, [.07, .025, 5], [x, .11, -5.35], mint);
text('EV', 0, .12, -6.6, .6, '#b8f4cd');
for (let x = -10; x <= 10; x += 2) box(scene, [.85, .015, .055], [x, .09, 0], white);
text('→', -8, .1, 1.15, .8); text('→', 6, .1, 1.15, .8);

function car(color, x, z, heading = 0) {
  const group = new THREE.Group(); scene.add(group); group.position.set(x, .1, z); group.rotation.y = heading;
  const paint = new THREE.MeshPhysicalMaterial({ color, metalness: .55, roughness: .25, clearcoat: 1, clearcoatRoughness: .12 });
  const glass = material('#17373d', { metalness: .65, roughness: .12 });
  box(group, [1.7, .48, 3.7], [0, .6, 0], paint, .22);
  box(group, [1.65, .19, 3.45], [0, .32, 0], dark, .08);
  box(group, [1.4, .53, 1.87], [0, 1.02, -.15], glass, .22);
  box(group, [1.29, .09, 1.35], [0, 1.3, -.24], paint, .07);
  for (const x of [-.69, .69]) box(group, [.055, .52, .08], [x, 1.02, -.2], paint, .02);
  box(group, [1.24, .07, .75], [0, .88, 1.12], paint, .04);
  box(group, [1.2, .13, .035], [0, .48, 1.85], dark, .03);
  const headlight = material('#f8ffe4', { emissive: '#f7ffe0', emissiveIntensity: 2.2 });
  const taillight = material('#b92226', { emissive: '#f12b2b', emissiveIntensity: 1.2 });
  for (const side of [-1, 1]) {
    box(group, [.47, .095, .08], [side * .53, .68, 1.8], headlight, .03);
    box(group, [.52, .08, .07], [side * .51, .69, -1.81], taillight, .025);
    box(group, [.23, .13, .3], [side * .87, .99, .35], paint, .06);
    box(group, [.03, .035, .22], [side * .846, .82, -.22], dark, .01);
  }
  const wheels = [];
  for (const side of [-1, 1]) for (const axle of [-1.15, 1.13]) {
    const pivot = new THREE.Group(); pivot.position.set(side * .83, .33, axle); group.add(pivot);
    const wheel = new THREE.Group(); pivot.add(wheel); wheels.push({ wheel, pivot, front: axle > 0 });
    const tire = new THREE.Mesh(new THREE.CylinderGeometry(.33, .33, .25, 24), material('#161b1c'));
    tire.rotation.z = Math.PI / 2; tire.castShadow = true; wheel.add(tire);
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(.23, .23, .265, 20), material('#adbdbb', { metalness: .9, roughness: .2 }));
    rim.rotation.z = Math.PI / 2; wheel.add(rim);
    for (let i = 0; i < 5; i++) {
      const spoke = box(wheel, [.28, .045, .39], [0, 0, 0], dark, .01); spoke.rotation.x = i * Math.PI / 5;
    }
  }
  group.userData.wheels = wheels; return group;
}
car('#466f72', -8, -5.35); car('#e2ded0', -4, -5.35); car('#923e36', 4, -5.35); car('#34424e', 8, -5.35);
car('#a4b9a4', -8, 5.35, Math.PI); car('#a5adb5', 4, 5.35, Math.PI); car('#e4c799', 8, 5.35, Math.PI);
const activeCar = car('#df8f36', -10, 0);

// Landscape and charging infrastructure frame the driving area.
function tree(x, z, scale = 1) {
  box(scene, [1.55, .4, 1.55], [x, .14, z], concrete, .12);
  box(scene, [1.3, .05, 1.3], [x, .37, z], material('#52674b'));
  box(scene, [.16, 1.5 * scale, .16], [x, .8 * scale, z], material('#897054'), .04);
  for (const [dx, dy, dz, radius] of [[0, 2.25, 0, .9], [.45, 1.9, .1, .6], [-.4, 2, -.2, .65]]) {
    const leaf = new THREE.Mesh(new THREE.IcosahedronGeometry(radius * scale, 2), material('#6c8c57'));
    leaf.position.set(x + dx, dy * scale, z + dz); leaf.castShadow = true; scene.add(leaf);
  }
}
for (const x of [-10, -5, 5, 10]) tree(x, -9.4, .85);
tree(-12.4, 5); tree(12.4, 4, 1.1);
for (const x of [-4, 0, 4]) {
  box(scene, [.5, 1.3, .35], [x, .7, -8.45], white, .09);
  box(scene, [.32, .45, .04], [x, .96, -8.24], dark, .03);
  box(scene, [.22, .06, .045], [x, 1.05, -8.21], mint);
}
const lamps = [];
for (const x of [-10.5, 10.5]) for (const z of [-7.8, 7.8]) {
  box(scene, [.1, 4, .1], [x, 2, z], dark, .025);
  box(scene, [1.1, .13, .4], [x, 4, z], dark, .04);
  box(scene, [.85, .035, .3], [x, 3.93, z], material('#fff0bb', { emissive: '#ffe5ac', emissiveIntensity: 2 }));
  const lamp = new THREE.PointLight('#ffe4b2', 0, 16, 2); lamp.position.set(x, 3.7, z); scene.add(lamp); lamps.push(lamp);
}
for (const x of [9.5, 10.4]) {
  box(scene, [.45, .07, .45], [x, .13, 2.3], dark, .03);
  const cone = new THREE.Mesh(new THREE.ConeGeometry(.18, .65, 16), material('#e29b50'));
  cone.position.set(x, .49, 2.3); cone.castShadow = true; scene.add(cone);
}

// Visual trajectory only: state is not supplied by the Python simulator.
const path = new THREE.CurvePath();
path.add(new THREE.LineCurve3(new THREE.Vector3(-10, .1, 0), new THREE.Vector3(-3, .1, 0)));
path.add(new THREE.CubicBezierCurve3(new THREE.Vector3(-3, .1, 0), new THREE.Vector3(-1, .1, 0), new THREE.Vector3(0, .1, -1), new THREE.Vector3(0, .1, -3)));
path.add(new THREE.LineCurve3(new THREE.Vector3(0, .1, -3), new THREE.Vector3(0, .1, -5.35)));
const route = new THREE.Line(new THREE.BufferGeometry().setFromPoints(path.getSpacedPoints(160)), new THREE.LineDashedMaterial({ color: '#83f0cf', dashSize: .22, gapSize: .15 }));
route.position.y = .035; route.computeLineDistances(); scene.add(route);
let elapsed = 0, paused = false, completed = false;
const duration = 19, length = path.getLength();
function positionAt(t) { return path.getPointAt(t); }
function reset() {
  elapsed = 0; completed = paused = false;
  activeCar.position.copy(positionAt(0)); activeCar.rotation.y = Math.PI / 2;
  $('pause').disabled = false; $('pause').textContent = 'Pausar';
  $('status').textContent = 'Recorrido automático'; $('progress').style.width = '0%';
  activeCar.userData.wheels.forEach(({ wheel, pivot }) => { wheel.rotation.x = 0; pivot.rotation.y = 0; });
}
function view() {
  const mode = $('camera').value;
  controls.enabled = mode === 'orbit';
  if (mode === 'top') { camera.position.set(0, 35, .01); controls.target.set(0, 0, 0); }
  if (mode === 'orbit') { camera.position.set(24, 25, 30); controls.target.set(-2.5, 0, 0); }
  controls.update();
}
$('camera').onchange = view;
$('pause').onclick = () => { if (completed) return; paused = !paused; $('pause').textContent = paused ? 'Continuar' : 'Pausar'; $('status').textContent = paused ? 'Simulación pausada' : 'Recorrido automático'; };
$('reset').onclick = reset;
$('route').onchange = () => { route.visible = $('route').checked; };
$('night').onchange = () => {
  const night = $('night').checked; document.body.classList.toggle('night', night);
  scene.background.set(night ? '#142629' : '#e4e8df'); scene.fog.color.copy(scene.background);
  sun.intensity = night ? .35 : 3.5; ambient.intensity = night ? .5 : 2;
  renderer.toneMappingExposure = night ? .85 : 1.2; lamps.forEach(light => { light.intensity = night ? 75 : 0; });
};
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
reset(); view();
const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), .05);
  let velocity = 0;
  if (!paused && !completed) {
    const oldPosition = activeCar.position.clone();
    elapsed = Math.min(duration, elapsed + dt);
    const t = elapsed / duration;
    // Ease acceleration and braking while sampling the path by distance.
    const progress = t * t * (3 - 2 * t);
    activeCar.position.copy(positionAt(progress));
    const tangent = path.getTangentAt(Math.min(progress, .99999));
    const desired = Math.atan2(tangent.x, tangent.z);
    const delta = Math.atan2(Math.sin(desired - activeCar.rotation.y), Math.cos(desired - activeCar.rotation.y));
    activeCar.rotation.y += delta;
    const traveled = activeCar.position.distanceTo(oldPosition); velocity = dt > 0 ? traveled / dt : 0;
    activeCar.userData.wheels.forEach(({ wheel, pivot, front }) => {
      wheel.rotation.x += traveled / .33;
      if (front) pivot.rotation.y = THREE.MathUtils.clamp(delta * 12, -.45, .45);
    });
    $('progress').style.width = `${progress * 100}%`;
    if (elapsed >= duration) { completed = true; $('status').textContent = 'Maniobra completada'; $('pause').textContent = 'Completado'; $('pause').disabled = true; velocity = 0; }
  }
  $('speed').textContent = (velocity * 3.6).toFixed(1);
  $('distance').textContent = activeCar.position.distanceTo(positionAt(1)).toFixed(1);
  if ($('camera').value === 'follow') {
    const offset = new THREE.Vector3(0, 5, -9).applyAxisAngle(new THREE.Vector3(0, 1, 0), activeCar.rotation.y);
    camera.position.lerp(activeCar.position.clone().add(offset), 1 - Math.exp(-3 * dt));
    controls.target.copy(activeCar.position).add(new THREE.Vector3(0, .6, 0));
  }
  controls.update(); renderer.render(scene, camera);
});
