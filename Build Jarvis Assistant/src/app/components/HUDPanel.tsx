import { ReactNode } from "react";

interface HUDPanelProps {
  title: string;
  children: ReactNode;
  className?: string;
  accent?: boolean;
}

export function HUDPanel({ title, children, className = "", accent = false }: HUDPanelProps) {
  return (
    <div
      className={`relative border bg-card backdrop-blur-sm ${className}`}
      style={{
        borderColor: accent ? "rgba(0,255,255,0.3)" : "rgba(0,180,216,0.2)",
        boxShadow: accent
          ? "0 0 20px rgba(0,255,255,0.05), inset 0 0 20px rgba(0,180,216,0.03)"
          : "0 0 10px rgba(0,100,150,0.1), inset 0 0 10px rgba(0,180,216,0.02)",
      }}
    >
      {/* Corner brackets */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400/70" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400/70" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400/70" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400/70" />

      {/* Title bar */}
      <div className="flex items-center gap-2 px-3 py-1.5 border-b" style={{ borderColor: "rgba(0,180,216,0.15)" }}>
        <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" style={{ boxShadow: "0 0 6px #00ffff" }} />
        <span
          className="text-cyan-400/80 uppercase tracking-widest"
          style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "10px", fontWeight: 600 }}
        >
          {title}
        </span>
      </div>

      <div className="p-3">{children}</div>
    </div>
  );
}
