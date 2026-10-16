import { Hand, Gauge, Radio } from "lucide-react";
import { GESTURES } from "../lib/gestures";
export default function GestureDashboard({gesture,tracking}){
 return <div className="glass rounded-2xl p-4">
  <div className="flex justify-between items-center"><div className="mono text-xs text-slate-400">GESTURE DASHBOARD</div><Radio size={15} className={tracking?"text-cyan-300":"text-slate-600"}/></div>
  <div className="mt-4 rounded-xl border border-cyan-300/10 p-4"><div className="text-2xl font-bold text-cyan-200">{gesture.name.replaceAll("_"," ").toUpperCase()}</div><div className="mt-2 grid grid-cols-2 gap-3 mono text-[10px] text-slate-500"><span className="flex gap-2"><Gauge size={13}/>CONFIDENCE {Math.round((gesture.confidence||0)*100)}%</span><span className="flex gap-2"><Hand size={13}/>HAND {(gesture.hand||"unknown").toUpperCase()}</span></div></div>
  <div className="grid grid-cols-2 gap-2 mt-3">{GESTURES.map(([id,label])=><div key={id} className={"rounded-lg border p-2 text-[11px] "+(id===gesture.name?"border-cyan-300/40 text-cyan-200":"border-white/5 text-slate-500")}>{label}</div>)}</div>
 </div>;
}
