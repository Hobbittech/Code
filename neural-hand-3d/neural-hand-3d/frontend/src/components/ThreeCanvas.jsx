import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment, Sparkles } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function Shape({scene}){
 const ref=useRef();
 useFrame((_,delta)=>{ if(ref.current){ ref.current.rotation.x += delta*.08; ref.current.rotation.y += delta*.12; }});
 const material={color:scene.color,metalness:.55,roughness:.22,emissive:scene.color,emissiveIntensity:.16};
 let geometry;
 if(scene.shape==="sphere") geometry=<sphereGeometry args={[1,48,32]}/>;
 else if(scene.shape==="torus") geometry=<torusGeometry args={[.72,.28,32,80]}/>;
 else if(scene.shape==="cone") geometry=<coneGeometry args={[.9,1.7,48]}/>;
 else if(scene.shape==="pyramid") geometry=<coneGeometry args={[1,1.6,4]}/>;
 else geometry=<boxGeometry args={[1.5,1.5,1.5]}/>;
 return <mesh ref={ref} scale={scene.scale} rotation={[scene.rotation.x,scene.rotation.y,scene.rotation.z]} geometry={geometry}><meshStandardMaterial {...material}/></mesh>;
}
export default function ThreeCanvas({scene}){
 return <Canvas camera={{position:[0,0,4.3],fov:45}} gl={{antialias:true}}>
  <color attach="background" args={["#020408"]}/><ambientLight intensity={.7}/><pointLight position={[3,3,4]} intensity={30} color={scene.color}/><pointLight position={[-3,-2,2]} intensity={12} color="#356cff"/>
  <Shape scene={scene}/>{scene.particles&&<Sparkles count={160} scale={5} size={2} speed={.5} color={scene.color}/>}<gridHelper args={[10,20,"#07333a","#07151a"]}/><OrbitControls enablePan={false}/><Environment preset="night"/>
 </Canvas>;
}
