import { useState } from "react";
import { Bot, LoaderCircle, Send } from "lucide-react";
import { api } from "../lib/utils";
const initial=[{role:"assistant",text:"NEURAL AI online. Ask me to change the shape, color, scale, rotation, reset the scene, or spawn particles."}];
export default function AIAssistant({scene,onSceneChange}){
 const [messages,setMessages]=useState(initial),[input,setInput]=useState(""),[busy,setBusy]=useState(false);
 async function send(e){e?.preventDefault(); if(!input.trim()||busy)return; const text=input.trim(); setInput(""); setMessages(m=>[...m,{role:"user",text}]); setBusy(true);
  try{const data=await api("/api/chat",{method:"POST",body:JSON.stringify({session_id:"default",message:text,scene})}); setMessages(m=>[...m,{role:"assistant",text:data.response}]); if(data.action){const a=data.action;if(a.op==="reset")onSceneChange({...scene,shape:"cube",color:"#00F0FF",scale:1,rotation:{x:0,y:0,z:0},particles:false});else if(a.op==="set_color")onSceneChange({...scene,color:a.value});else if(a.op==="set_shape")onSceneChange({...scene,shape:a.value});else if(a.op==="set_scale")onSceneChange({...scene,scale:a.value});else if(a.op==="rotate")onSceneChange({...scene,rotation:{...scene.rotation,...a.value}});else if(a.op==="spawn_particles")onSceneChange({...scene,particles:Boolean(a.value)});} }
  catch(err){setMessages(m=>[...m,{role:"assistant",text:`Connection error: ${err.message}`}]);} finally{setBusy(false);}
 }
 return <div className="glass rounded-2xl p-4"><div className="flex items-center gap-2 mono text-xs text-slate-400 mb-3"><Bot size={15} className="text-cyan-300"/>NEURAL AI</div>
  <div className="h-44 overflow-y-auto scrollbar space-y-2 mb-3">{messages.map((m,i)=><div key={i} className={"text-xs rounded-lg p-2 "+(m.role==="user"?"bg-cyan-300/10 ml-8":"bg-white/[.03] mr-4 text-slate-300")}>{m.text}</div>)}</div>
  <form onSubmit={send} className="flex gap-2"><input value={input} onChange={e=>setInput(e.target.value)} placeholder="Command the scene..." className="min-w-0 flex-1 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs outline-none focus:border-cyan-300/40"/><button className="rounded-lg bg-cyan-300/15 px-3 text-cyan-200">{busy?<LoaderCircle size={16} className="animate-spin"/>:<Send size={16}/>}</button></form>
 </div>;
}
