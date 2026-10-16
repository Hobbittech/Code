import { useEffect, useState } from "react";
import { Activity, Bot, Camera, CircleDot, Database, ExternalLink, Hand, RotateCcw } from "lucide-react";
import { motion } from "framer-motion";
import "../App.css";
import WebcamTracker from "../components/WebcamTracker";
import ThreeCanvas from "../components/ThreeCanvas";
import GestureDashboard from "../components/GestureDashboard";
import AIAssistant from "../components/AIAssistant";
import BrowserPanel from "../components/BrowserPanel";
import TelemetryLog from "../components/TelemetryLog";
import { api } from "../lib/utils";

const DEFAULT={session_id:"default",shape:"cube",color:"#00F0FF",scale:1,rotation:{x:0,y:0,z:0},particles:false};

export default function Workstation(){
 const [scene,setScene]=useState(DEFAULT),[gesture,setGesture]=useState({name:"open_palm",confidence:0,hand:"unknown"}),[events,setEvents]=useState([]),[tracking,setTracking]=useState(false);
 useEffect(()=>{ api("/api/scene/default").then(setScene).catch(()=>{}); api("/api/gestures/recent?session_id=default&limit=20").then(setEvents).catch(()=>{}); },[]);
 const updateScene=(patch)=>setScene(s=>({...s,...patch,rotation:{...s.rotation,...(patch.rotation||{})}}));
 const saveScene=(next)=>{setScene(next); api("/api/scene",{method:"POST",body:JSON.stringify(next)}).catch(()=>{});};
 const onGesture=(g)=>{setGesture(g); setTracking(g.name!=="unknown"); setEvents(e=>[{...g,timestamp:new Date().toISOString()},...e].slice(0,20));};
 const gestureScene=(g)=>{ if(g.name==="open_palm") saveScene(DEFAULT); if(g.name==="point") updateScene({rotation:{...scene.rotation,y:scene.rotation.y+0.12}}); if(g.name==="three_finger") updateScene({scale:Math.min(4,scene.scale+.1)}); };
 useEffect(()=>{if(gesture.name!=="unknown") gestureScene(gesture);},[gesture.name]); 
 return <div className="app-shell min-h-screen">
  <header className="h-16 border-b border-cyan-300/10 flex items-center justify-between px-5">
   <div className="flex items-center gap-3"><CircleDot className="text-cyan-300"/><div><div className="font-bold tracking-widest">NEURAL-HAND</div><div className="mono text-[10px] text-slate-500">3D CONTROL DECK</div></div></div>
   <div className="flex gap-4 mono text-[10px] text-slate-500"><span className="flex gap-1 items-center"><Camera size={13}/>CAMERA {tracking?"ONLINE":"STANDBY"}</span><span className="flex gap-1 items-center"><Database size={13}/>MONGO OPTIONAL</span><span className="flex gap-1 items-center"><Bot size={13}/>OPENAI</span></div>
  </header>
  <main className="p-4 grid grid-cols-12 gap-4 max-w-[1700px] mx-auto">
   <section className="col-span-12 xl:col-span-8 space-y-4">
    <div className="glass rounded-2xl overflow-hidden h-[520px] relative"><ThreeCanvas scene={scene} onSceneChange={updateScene}/><div className="absolute top-3 left-3 mono text-[10px] text-cyan-200/70 flex items-center gap-2"><Activity size={13}/>SPATIAL VIEWPORT / LIVE</div></div>
    <div className="grid md:grid-cols-2 gap-4"><WebcamTracker onGesture={onGesture}/><TelemetryLog events={events}/></div>
   </section>
   <aside className="col-span-12 xl:col-span-4 space-y-4">
    <GestureDashboard gesture={gesture} tracking={tracking}/>
    <AIAssistant scene={scene} onSceneChange={saveScene}/>
    <BrowserPanel/>
   </aside>
  </main>
 </div>;
}
