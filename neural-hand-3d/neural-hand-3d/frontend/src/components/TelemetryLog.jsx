import { Activity } from "lucide-react";
export default function TelemetryLog({events}){
 return <div className="glass rounded-2xl p-4"><div className="flex items-center gap-2 mono text-xs text-slate-400 mb-3"><Activity size={15} className="text-cyan-300"/>TELEMETRY / EVENT LOG</div>
 <div className="h-56 overflow-y-auto scrollbar space-y-1">{events.length===0?<div className="text-xs text-slate-600">Waiting for gesture telemetry...</div>:events.map((e,i)=><div key={i} className="mono text-[10px] border-b border-white/5 py-2 flex justify-between gap-2"><span className="text-cyan-200">{e.gesture||e.name}</span><span className="text-slate-600">{e.hand||"?"} / {Math.round((e.confidence||0)*100)}%</span></div>)}</div>
 </div>;
}
