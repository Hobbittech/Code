import { useEffect, useRef, useState } from "react";
import { CameraOff, LoaderCircle } from "lucide-react";
import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";
import { api } from "../lib/utils";
import { classifyGesture } from "../lib/gestures";

export default function WebcamTracker({onGesture}){
 const videoRef=useRef(null),landmarkerRef=useRef(null),rafRef=useRef(null),lastSent=useRef(0),lastGesture=useRef("");
 const [status,setStatus]=useState("loading"),[error,setError]=useState("");
 useEffect(()=>{
  let stream;
  async function start(){
   try{
    setStatus("loading");
    stream=await navigator.mediaDevices.getUserMedia({video:{width:640,height:480},audio:false});
    videoRef.current.srcObject=stream; await videoRef.current.play();
    const vision=await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22/wasm");
    landmarkerRef.current=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:2,minHandDetectionConfidence:.5,minHandPresenceConfidence:.5,minTrackingConfidence:.5});
    setStatus("active"); loop();
   }catch(e){ console.error(e); setError("Camera or MediaPipe could not start. Check browser permission and internet access for the model."); setStatus("error"); }
  }
  function loop(){
   if(!videoRef.current||!landmarkerRef.current) return;
   const result=landmarkerRef.current.detectForVideo(videoRef.current,performance.now());
   if(result.landmarks?.length){
    const idx=0,g=classifyGesture(result.landmarks[idx]),hand=result.handednesses?.[idx]?.[0]?.categoryName||"unknown";
    const payload={...g,hand:hand.toLowerCase(),session_id:"default"};
    onGesture(payload);
    const now=Date.now();
    if(now-lastSent.current>1200 && (payload.name!==lastGesture.current || now-lastSent.current>2500)){
      lastSent.current=now; lastGesture.current=payload.name;
      api("/api/gestures",{method:"POST",body:JSON.stringify({session_id:"default",gesture:payload.name,confidence:payload.confidence,hand:payload.hand})}).catch(()=>{});
    }
   }
   rafRef.current=requestAnimationFrame(loop);
  }
  start();
  return ()=>{ cancelAnimationFrame(rafRef.current); stream?.getTracks().forEach(t=>t.stop()); };
 },[onGesture]);
 return <div className="glass rounded-2xl p-4">
  <div className="flex justify-between mb-3"><div className="mono text-xs text-slate-400">WEBCAM TRACKER</div><div className="mono text-[10px] text-cyan-300">{status.toUpperCase()}</div></div>
  <div className="aspect-video bg-black rounded-xl overflow-hidden relative">{status==="error"?<div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 text-xs text-center px-5"><CameraOff size={28} className="mb-2"/>{error}</div>:<><video ref={videoRef} muted playsInline className="w-full h-full object-cover scale-x-[-1]"/>{status==="loading"&&<div className="absolute inset-0 grid place-items-center bg-black/60"><LoaderCircle className="animate-spin text-cyan-300"/></div>}</>}</div>
 </div>;
}
