import './style.css'
import * as THREE from './node_modules/three/src/Three.js'
// import { Interaction } from 'three.interaction';

// Setup
const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector('#bg'),
})
// const interaction = new Interaction(renderer, scene, camera);
renderer.setPixelRatio(window.devicePixelRatio)
renderer.setSize(window.innerWidth, window.innerHeight)
camera.position.setZ(30)
renderer.render(scene, camera)

let apps = []
let imgArray1 = ['/img/screenshots/mynotes/3.png', '/img/screenshots/mynotes/2.png', '/img/screenshots/mynotes/1.png', '/img/screenshots/mynotes/4.png']
let imgArray2 = ['/img/screenshots/libria/1.png', '/img/screenshots/libria/2.png', '/img/screenshots/libria/3.png', '/img/screenshots/libria/4.png']
let imgArray3 = ['/img/screenshots/feecalc/1.png', '/img/screenshots/feecalc/2.png', '/img/screenshots/feecalc/3.png', '/img/screenshots/feecalc/4.png']
let imgArray4 = ['/img/screenshots/uuids/1.png', '/img/screenshots/uuids/2.png', '/img/screenshots/uuids/3.png', '/img/screenshots/uuids/4.png']
let imgArray5 = ['/img/screenshots/number_systems/1.png', '/img/screenshots/number_systems/2.png', '/img/screenshots/number_systems/3.png', '/img/screenshots/number_systems/4.png']

addApp(imgArray1, 40)
addApp(imgArray2, 140)
addApp(imgArray3, 240)
addApp(imgArray4, 340)
addApp(imgArray5, 440)

let skills = []
addSkills()

// Lights
const ambientLight = new THREE.AmbientLight(0xffffff)
scene.add(ambientLight)


const starGeometry = new THREE.SphereGeometry(0.25, 24, 24);
const starMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
Array(2000).fill().forEach(addStar)
animate()

const skillsButton = document.getElementById("skills")
skillsButton.onclick = rotateCamera

const contactButton = document.getElementById("contact")
let contactVisible = false
contactButton.onclick = showContact

const homeButton = document.getElementById("home")
homeButton.onclick = goHome

let scrollingEnabled = true
document.body.onscroll = moveCamera;

moveCamera()

//Creates single App element
function addApp(imgArray, position) {
  var geometry = new THREE.BoxGeometry(9, 16, 9)
            
  var materialArray = [];
  materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( imgArray[0]) }));
  materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( imgArray[1] ) }));
  materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( imgArray[0] ) }));
  materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( imgArray[1] ) }));
  materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( imgArray[2] ) }));
  materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( imgArray[3] ) }));
  
  var material = new THREE.MeshFaceMaterial(materialArray);
  var app = new THREE.Mesh(geometry, material);
  app.position.z = position

  scene.add(app);
  apps.push(app)
}

//Creates single skill element
function addSkill(img, x, y, z) {
  const appTexture = new THREE.TextureLoader().load(img)
  const skill = new THREE.Mesh(new THREE.BoxGeometry(100, 100, 100), new THREE.MeshBasicMaterial({ map: appTexture }))
  skill.position.x = x
  skill.position.y = y
  skill.position.z = z
  // app.on('click', function(ev) {alert('test')})
  scene.add(skill)
  skills.push(skill)
}

//Creates single star element
function addStar() {
  const star = new THREE.Mesh(starGeometry, starMaterial);
  const [x, y, z] = Array(3)
    .fill()
    .map(() => THREE.MathUtils.randFloatSpread(1750));

  star.position.set(x, y, z);
  scene.add(star);
}

// Rotate camera to show skill overview
function rotateCamera() {
  scrollingEnabled = false
  document.getElementById('body').style.overflow = 'hidden'
  if (camera.rotation.y == 0) {
    skillsButton.style.zIndex = 0
    skillsButton.style.opacity = 0
  }
  if (camera.rotation.y <= 2) {
    requestAnimationFrame(rotateCamera)
    renderer.render(scene, camera)

    camera.rotation.y += 0.1
  }
  if (camera.rotation.y >= 2) {
    window.scroll(0, 0)
    camera.position.z = 200
    document.getElementById('mainHeader').style.opacity = 0
    document.getElementById('mainHeader').style.zIndex = 0
    document.getElementById('mainSubtitle').style.opacity = 0
    document.getElementById('mainSubtitle').style.zIndex = 0
    document.getElementById('contact').style.opacity = 1
    document.getElementById('contact').style.zIndex = 100
  }
}

// Update camera view on scroll
function moveCamera() {
  if (!scrollingEnabled) return
  const t = document.body.getBoundingClientRect().top;
  camera.position.z = t * (-0.1)
}

//Open contact form and animate out the skills elements
function showContact() {
  scrollingEnabled = false
  if (skills[0].position.y < 1500) {
    for (let i=0; i<skills.length; i++) {
      skills[i].position.y += 20.1
      skills[i].position.z -= 1.1
      skills[i].rotation.y += 0.05
      skills[i].rotation.x += 0.05
    }
    if (skills[0].position.y >= 900)  {
      contactVisible = true
      document.getElementById('mail-adress').style.opacity = 1
      document.getElementById('mail-adress').style.zIndex = 101

      document.getElementById('mail').style.opacity = 1
      document.getElementById('mail').style.zIndex = 101

      document.getElementById('contact').style.zIndex = -1
      document.getElementById('contact').style.opacity = 0

      document.getElementById('home').style.opacity = 1
      document.getElementById('home').style.zIndex = 10

      document.getElementById('submit').style.opacity = 1
      document.getElementById('submit').style.zIndex = 101

      // document.getElementById('contactHeader').style.opacity = 1
      // document.getElementById('contactHeader').style.zIndex = 100

      document.getElementById('app').style.height = '5vh'
    }
    requestAnimationFrame(showContact)
    renderer.render(scene, camera)
  } 
}

function addSkills () {
  skills = []
    if (window.innerWidth > 1000) {
      addSkill('/img/vue.jpeg', -550, -150, 1000)
      addSkill('/img/go.png', -750, 50, 600)
      addSkill('/img/postgres.png', -850, 250, 200)
    
      addSkill('/img/docker.jpeg', -550, 50, 1000)
      addSkill('/img/css.jpeg', -750, 250, 600)
      addSkill('/img/js.png', -850, -150, 200)
    
      addSkill('/img/gcp.jpeg', -550, 250, 1000)
      addSkill('/img/bulma.png', -750, -150, 600)
      addSkill('/img/html.png', -850, 50, 200)
    } else {
      addSkill('/img/vue.jpeg', -650, -50, 600)
      addSkill('/img/go.png', -650, 150, 600)
      addSkill('/img/postgres.png', -650, 350, 600)
      addSkill('/img/docker.jpeg', -650, -250, 600)
    
      addSkill('/img/gcp.jpeg', -700, -50, 400)
      addSkill('/img/js.png', -700, 150, 400)
      addSkill('/img/bulma.png', -700, 350, 400)
      addSkill('/img/css.jpeg', -700, -250, 400)
    }
}

function goHome() {
  scrollingEnabled = true
    document.getElementById('body').style.overflow = 'visible'

    document.getElementById('app').style.height = '600vh'
    document.getElementById('mail-adress').style.opacity = 0
    document.getElementById('mail-adress').style.zIndex = 0

    document.getElementById('mail').style.opacity = 0
    document.getElementById('mail').style.zIndex = 0

    document.getElementById('submit').style.opacity = 0
    document.getElementById('submit').style.zIndex = 0

    document.getElementById('home').style.opacity = 0
    document.getElementById('home').style.zIndex = 0

    document.getElementById('skills').style.opacity = 1
    document.getElementById('skills').style.zIndex = 100

    document.getElementById('submit').style.opacity = 0
    document.getElementById('submit').style.zIndex = 0

    document.getElementById('home').style.opacity = 0
    document.getElementById('home').style.zIndex = 0
    
  if (camera.rotation.y >= 0) {
    requestAnimationFrame(goHome)
    renderer.render(scene, camera)
    camera.rotation.y -= 0.1
  } else {
    addSkills()
    setTimeout(200)
    window.scroll({
      top: 10,
      behavior: "smooth"
    });
    document.getElementById('mainHeader').style.opacity = 1
    document.getElementById('mainHeader').style.zIndex = 100

    document.getElementById('mainSubtitle').style.opacity = 1
    document.getElementById('mainSubtitle').style.zIndex = 100
  }
}

//continously Rerender the screen
function animate() {
  requestAnimationFrame(animate)
  renderer.render(scene, camera)

  for (let i=0; i<apps.length; i++) {
    apps[i].rotation.y += 0.008
  }
  for (let i=0; i<skills.length; i++) {
    if (i%2 === 0) {
      skills[i].rotation.y += 0.005
    } else {
      skills[i].rotation.y -= 0.005
    }
  }
}
