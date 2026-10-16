import { motion } from "framer-motion";
import { ArrowRight, Camera, Cpu, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function Landing() {
  const navigate=useNavigate();
  return <div className="app-shell grid-bg min-h-screen flex items-center justify-center p-6">
    <div className="max-w-5xl w-full text-center">
      <motion.div initial={{opacity:0,y:25}} animate={{opacity:1,y:0}} transition={{duration:.7}}>
        <div className="mono text-cyan-300 text-sm tracking-[.4em] mb-5">SPATIAL COMPUTING / LOCAL WORKSTATION</div>
        <h1 className="text-6xl md:text-8xl font-black tracking-tight glow">NEURAL-HAND<br/><span className="text-cyan-300">3D WORKSTATION</span></h1>
        <p className="text-slate-400 max-w-2xl mx-auto mt-7 text-lg">A futuristic browser-based control deck where your webcam gestures and NEURAL AI manipulate a live Three.js scene.</p>
        <button onClick={()=>navigate("/workstation")} className="mt-9 inline-flex items-center gap-3 rounded-xl border border-cyan-300/40 bg-cyan-300/10 px-7 py-4 text-cyan-100 hover:bg-cyan-300/20 transition">
          Launch Workstation <ArrowRight size={19}/>
        </button>
      </motion.div>
      <div className="grid md:grid-cols-3 gap-4 mt-16">
        {[["MediaPipe Tasks Vision",Camera],["React Three Fiber",Cpu],["OpenAI + FastAPI",Sparkles]].map(([label,Icon],i)=>
          <motion.div key={label} initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:.2+i*.1}} className="glass rounded-2xl p-5 text-left">
            <Icon className="text-cyan-300 mb-4" size={22}/><div className="font-semibold">{label}</div><div className="mono text-xs text-slate-500 mt-1">LOCAL / REAL-TIME</div>
          </motion.div>
        )}
      </div>
    </div>
  </div>;
}
