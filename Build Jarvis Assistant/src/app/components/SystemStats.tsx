import { useEffect, useState } from "react";
import { motion } from "motion/react";

interface Stat {
  label: string;
  value: number;
  unit?: string;
  color?: string;
}

const MOCK_STATS: Stat[] = [
  { label: "CPU CORE A", value: 34, unit: "%", color: "#00b4d8" },
  { label: "CPU CORE B", value: 71, unit: "%", color: "#00b4d8" },
  { label: "NEURAL NET", value: 88, unit: "%", color: "#00ffff" },
  { label: "MEMORY", value: 52, unit: "%", color: "#0077cc" },
];

export function SystemStats() {
  const [stats, setStats] = useState(MOCK_STATS);

  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) =>
        prev.map((s) => ({
          ...s,
          value: Math.max(10, Math.min(99, s.value + (Math.random() - 0.5) * 12)),
        }))
      );
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-2.5">
      {stats.map((stat) => (
        <div key={stat.label}>
          <div className="flex justify-between mb-1">
            <span
              className="text-muted-foreground uppercase tracking-wider"
              style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "9px", fontWeight: 600 }}
            >
              {stat.label}
            </span>
            <span
              style={{
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: "10px",
                color: stat.color,
              }}
            >
              {Math.round(stat.value)}
              {stat.unit}
            </span>
          </div>
          <div className="h-px w-full bg-cyan-900/40 relative overflow-hidden">
            <motion.div
              className="h-full absolute top-0 left-0"
              style={{ background: stat.color, boxShadow: `0 0 6px ${stat.color}` }}
              animate={{ width: `${stat.value}%` }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
