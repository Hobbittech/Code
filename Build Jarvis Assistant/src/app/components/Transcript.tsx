import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";

export interface Message {
  id: string;
  role: "user" | "jarvis";
  text: string;
  timestamp: Date;
}

interface TranscriptProps {
  messages: Message[];
  isProcessing: boolean;
}

export function Transcript({ messages, isProcessing }: TranscriptProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing]);

  return (
    <div
      className="h-full overflow-y-auto space-y-3 pr-1"
      style={{ scrollbarWidth: "none" }}
    >
      {messages.length === 0 && (
        <div
          className="text-center mt-8 text-muted-foreground"
          style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: "11px" }}
        >
          <p className="mb-1 opacity-60">// AWAITING INPUT</p>
          <p className="opacity-40">Speak or type to initialize session</p>
        </div>
      )}

      <AnimatePresence initial={false}>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, x: msg.role === "user" ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex flex-col gap-0.5 ${msg.role === "user" ? "items-end" : "items-start"}`}
          >
            <span
              className="uppercase tracking-widest opacity-50"
              style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "9px", fontWeight: 600 }}
            >
              {msg.role === "user" ? "YOU" : "J.A.R.V.I.S."} —{" "}
              {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
            </span>
            <div
              className={`px-3 py-2 max-w-[85%] ${
                msg.role === "user"
                  ? "border-r-2 text-right"
                  : "border-l-2"
              }`}
              style={{
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: "12px",
                lineHeight: "1.6",
                borderColor: msg.role === "user" ? "rgba(0,255,255,0.5)" : "rgba(0,180,216,0.4)",
                background:
                  msg.role === "user"
                    ? "rgba(0,255,255,0.04)"
                    : "rgba(0,100,200,0.06)",
                color: msg.role === "user" ? "#a8d8ea" : "#7ecfea",
              }}
            >
              {msg.text}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {isProcessing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-start gap-2"
        >
          <div
            className="px-3 py-2 border-l-2"
            style={{
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: "12px",
              borderColor: "rgba(0,180,216,0.4)",
              background: "rgba(0,100,200,0.06)",
              color: "#4a9ebb",
            }}
          >
            <ProcessingDots />
          </div>
        </motion.div>
      )}

      <div ref={endRef} />
    </div>
  );
}

function ProcessingDots() {
  return (
    <span className="inline-flex gap-1">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          animate={{ opacity: [0.2, 1, 0.2] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.3 }}
        >
          ■
        </motion.span>
      ))}
    </span>
  );
}
