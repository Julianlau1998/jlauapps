import * as THREE from './node_modules/three/src/Three.js'

function addStar() {
    const geometry = new THREE.SphereGeometry(0.25, 24, 24);
    const material = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const star = new THREE.Mesh(geometry, material);
    
    const [x, y, z] = Array(3)
        .fill()
        .map(() => THREE.MathUtils.randFloatSpread(500));
    
    star.position.set(x, y, z);
    scene.add(star);
}
  
  
function moveCamera() {
    const t = document.body.getBoundingClientRect().top;
    firstApp.rotation.x += 0.05;
    firstApp.rotation.y += 0.075;
    firstApp.rotation.z += 0.05;
  
    camera.position.z = t * -0.01;
    camera.position.x = t * -0.0002;
    camera.rotation.y = t * -0.0002;
}
  
  
function animate() {
    requestAnimationFrame(animate)
    renderer.render(scene, camera);
    
    firstApp.rotation.y += 0.002;
}  