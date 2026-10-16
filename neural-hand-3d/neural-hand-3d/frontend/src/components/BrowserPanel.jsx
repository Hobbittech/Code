import { useState } from "react";
import { ExternalLink, Globe } from "lucide-react";
export default function BrowserPanel(){
 const [url,setUrl]=useState("https://example.com"),[src,setSrc]=useState("https://example.com"),[blocked,setBlocked]=useState(false);
 function go(e){e.preventDefault();let value=url.trim();if(!/^https?:\/\//i.test(value))value="https://"+value;setUrl(value);setSrc(value);setBlocked(false);}
 return <div className="glass rounded-2xl p-4"><div className="flex items-center gap-2 mono text-xs text-slate-400 mb-3"><Globe size={15} className="text-cyan-300"/>BROWSER PANEL</div>
 <form onSubmit={go} className="flex gap-2 mb-3"><input value={url} onChange={e=>setUrl(e.target.value)} className="min-w-0 flex-1 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs"/><button className="rounded-lg border border-cyan-300/20 px-3 text-cyan-200">GO</button></form>
 <div className="h-44 rounded-xl overflow-hidden bg-black/30 border border-white/5 relative">{!blocked&&<iframe title="Embedded browser" src={src} className="w-full h-full bg-white" onError={()=>setBlocked(true)}/>}<div className="absolute bottom-2 left-2 right-2 pointer-events-none text-[9px] text-slate-500 bg-black/60 p-1 rounded">Some sites block iframe embedding for security reasons. If blank, open it externally.</div></div>
 <a href={src} target="_blank" rel="noreferrer" className="mt-2 inline-flex items-center gap-1 text-[10px] text-cyan-300">Open externally <ExternalLink size={11}/></a>
 </div>;
}
