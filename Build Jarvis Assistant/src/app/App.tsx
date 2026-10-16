import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { OrbCore } from "./components/OrbCore";
import { HUDPanel } from "./components/HUDPanel";
import { Transcript, Message } from "./components/Transcript";
import { SystemStats } from "./components/SystemStats";
import { projectId, publicAnonKey } from "/utils/supabase/info";

const SERVER_URL = `https://${projectId}.supabase.co/functions/v1/make-server-a8430a6a`;

const SUGGESTED_QUERIES = [
  "What time is it?",
  "Weather in New York?",
  "Tell me about quantum entanglement.",
  "Who designed the Eiffel Tower?",
  "Run a system diagnostic.",
  "What is the speed of light?",
];

// Speech synthesis — pick a deep/british-ish voice
function speak(text: string, onEnd?: () => void) {
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate = 0.92;
  utt.pitch = 0.85;
  utt.volume = 1;

  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(
    (v) =>
      v.name.toLowerCase().includes("daniel") ||
      v.name.toLowerCase().includes("google uk") ||
      v.name.toLowerCase().includes("british") ||
      v.name.toLowerCase().includes("male") ||
      (v.lang === "en-GB" && !v.name.toLowerCase().includes("female"))
  );
  if (preferred) utt.voice = preferred;

  if (onEnd) utt.onend = onEnd;
  window.speechSynthesis.speak(utt);
}

function useDateTime() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return now;
}

export default function App() {
  const now = useDateTime();
  const [messages, setMessages] = useState<Message[]>([]);
  // history for API — role: user|assistant
  const historyRef = useRef<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [status, setStatus] = useState<"STANDBY" | "ACTIVE" | "PROCESSING" | "SPEAKING">("STANDBY");
  const recognitionRef = useRef<any>(null);

  // Load voices async
  useEffect(() => {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isProcessing || isSpeaking) return;

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        text: text.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setIsProcessing(true);
      setStatus("PROCESSING");

      historyRef.current = [...historyRef.current, { role: "user", content: text.trim() }];

      try {
        const res = await fetch(`${SERVER_URL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${publicAnonKey}`,
          },
          body: JSON.stringify({ messages: historyRef.current }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? "Server error");

        const responseText = data.text;
        historyRef.current = [...historyRef.current, { role: "assistant", content: responseText }];

        const jarvisMsg: Message = {
          id: crypto.randomUUID(),
          role: "jarvis",
          text: responseText,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, jarvisMsg]);
        setIsProcessing(false);
        setIsSpeaking(true);
        setStatus("SPEAKING");

        speak(responseText, () => {
          setIsSpeaking(false);
          setStatus("ACTIVE");
        });
      } catch (e) {
        console.error("Chat error:", e);
        const errMsg: Message = {
          id: crypto.randomUUID(),
          role: "jarvis",
          text: `I'm afraid I encountered an error, sir: ${e}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errMsg]);
        setIsProcessing(false);
        setStatus("ACTIVE");
      }
    },
    [isProcessing, isSpeaking]
  );

  const toggleListen = useCallback(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Try Chrome.");
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      setStatus(messages.length > 0 ? "ACTIVE" : "STANDBY");
      return;
    }

    const rec = new SpeechRecognition();
    rec.lang = "en-US";
    rec.continuous = false;
    rec.interimResults = false;

    rec.onstart = () => {
      setIsListening(true);
      setStatus("ACTIVE");
    };

    rec.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      setIsListening(false);
      sendMessage(transcript);
    };

    rec.onerror = () => {
      setIsListening(false);
      setStatus(messages.length > 0 ? "ACTIVE" : "STANDBY");
    };

    rec.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = rec;
    rec.start();
  }, [isListening, messages.length, sendMessage]);

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setStatus("ACTIVE");
  };

  const statusColor =
    status === "STANDBY"
      ? "#4a9ebb"
      : status === "PROCESSING"
      ? "#ffaa00"
      : status === "SPEAKING"
      ? "#aa44ff"
      : "#00ffff";

  const statusLabel =
    status === "STANDBY"
      ? "STANDING BY"
      : status === "PROCESSING"
      ? "PROCESSING"
      : status === "SPEAKING"
      ? "SPEAKING"
      : "ONLINE";

  const statusSub =
    status === "STANDBY"
      ? "PLEASE COMMAND ⬥ WHISPER ⬥ TYPE AWAY"
      : status === "PROCESSING"
      ? "COMPUTING RESPONSE ⬥ PLEASE HOLD"
      : status === "SPEAKING"
      ? "JARVIS IS SPEAKING ⬥ CLICK STOP TO INTERRUPT"
      : "SESSION ACTIVE ⬥ READY FOR INPUT";

  return (
    <div
      className="size-full flex flex-col overflow-hidden select-none"
      style={{
        background: "radial-gradient(ellipse at 50% 60%, #041830 0%, #020c18 60%, #010810 100%)",
        fontFamily: "'Share Tech Mono', monospace",
      }}
    >
      {/* Scanline overlay */}
      <div
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,180,216,0.15) 2px, rgba(0,180,216,0.15) 4px)",
        }}
      />

      {/* TOP BAR */}
      <div
        className="flex items-center justify-between px-6 py-3 border-b shrink-0"
        style={{ borderColor: "rgba(0,180,216,0.15)" }}
      >
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-1 rounded-full bg-cyan-400"
                style={{ height: `${8 + i * 4}px` }}
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
              />
            ))}
          </div>
          <div>
            <h1
              className="tracking-[0.3em] text-cyan-300"
              style={{ fontFamily: "'Orbitron', sans-serif", fontSize: "13px", fontWeight: 700 }}
            >
              J.A.R.V.I.S.
            </h1>
            <p
              className="text-muted-foreground uppercase tracking-widest"
              style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "8px", fontWeight: 500 }}
            >
              Just A Rather Very Intelligent System
            </p>
          </div>
        </div>

        <div className="hidden md:flex items-center gap-2">
          <motion.div
            className="w-2 h-2 rounded-full"
            style={{ background: statusColor, boxShadow: `0 0 8px ${statusColor}` }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <span
            className="tracking-widest uppercase"
            style={{
              fontFamily: "'Rajdhani', sans-serif",
              fontSize: "10px",
              fontWeight: 600,
              color: statusColor,
            }}
          >
            {statusLabel}
          </span>
        </div>

        <div className="text-right">
          <div
            className="text-cyan-300 tracking-widest"
            style={{ fontFamily: "'Orbitron', sans-serif", fontSize: "18px", fontWeight: 600 }}
          >
            {now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </div>
          <div
            className="text-muted-foreground uppercase tracking-widest"
            style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "9px" }}
          >
            {now
              .toLocaleDateString([], {
                weekday: "short",
                day: "numeric",
                month: "short",
                year: "numeric",
              })
              .toUpperCase()}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-[220px_1fr_260px] gap-0 overflow-hidden">
        {/* LEFT PANEL */}
        <div
          className="flex-col gap-4 p-4 border-r overflow-y-auto hidden md:flex"
          style={{ borderColor: "rgba(0,180,216,0.1)", scrollbarWidth: "none" }}
        >
          <HUDPanel title="System Diagnostics">
            <SystemStats />
          </HUDPanel>

          <HUDPanel title="Suggested Queries">
            <div className="space-y-1.5">
              {SUGGESTED_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  disabled={isProcessing || isSpeaking}
                  className="w-full text-left px-2 py-1.5 transition-all duration-200 disabled:opacity-40"
                  style={{
                    fontFamily: "'Share Tech Mono', monospace",
                    fontSize: "10px",
                    color: "#4a9ebb",
                    background: "transparent",
                    border: "none",
                    cursor: isProcessing || isSpeaking ? "not-allowed" : "pointer",
                  }}
                  onMouseEnter={(e) => {
                    if (!isProcessing && !isSpeaking) {
                      e.currentTarget.style.color = "#00ffff";
                      e.currentTarget.style.background = "rgba(0,255,255,0.04)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = "#4a9ebb";
                    e.currentTarget.style.background = "transparent";
                  }}
                >
                  <span className="opacity-40 mr-1">›</span>
                  {q}
                </button>
              ))}
            </div>
          </HUDPanel>
        </div>

        {/* CENTER */}
        <div className="flex flex-col items-center justify-between py-6 px-4 overflow-hidden">
          <div className="flex-1 flex flex-col items-center justify-center gap-4">
            <OrbCore
              isListening={isListening}
              isProcessing={isProcessing || isSpeaking}
            />

            <AnimatePresence mode="wait">
              <motion.div
                key={statusLabel}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}
                className="text-center"
              >
                <p
                  className="tracking-[0.5em] uppercase"
                  style={{
                    fontFamily: "'Orbitron', sans-serif",
                    fontSize: "11px",
                    color: statusColor,
                    fontWeight: 500,
                  }}
                >
                  {statusLabel}
                </p>
                <p
                  className="mt-1 tracking-widest text-muted-foreground uppercase"
                  style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "8px" }}
                >
                  {statusSub}
                </p>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Control buttons */}
          <div className="flex gap-4 mb-4">
            {/* MIC */}
            <button
              onClick={toggleListen}
              disabled={isProcessing || isSpeaking}
              className="w-12 h-12 rounded-full border transition-all duration-200 disabled:opacity-40"
              style={{
                fontFamily: "'Orbitron', sans-serif",
                fontSize: "8px",
                fontWeight: 700,
                color: isListening ? "#020c18" : "#4a9ebb",
                background: isListening ? "#00ffff" : "transparent",
                borderColor: isListening ? "#00ffff" : "rgba(0,180,216,0.4)",
                boxShadow: isListening ? "0 0 20px #00ffff" : "none",
                cursor: isProcessing || isSpeaking ? "not-allowed" : "pointer",
              }}
              title="Hold to speak"
            >
              🎙
            </button>

            {/* STOP / CLR */}
            <button
              onClick={isSpeaking ? stopSpeaking : () => { setMessages([]); historyRef.current = []; setStatus("STANDBY"); }}
              className="w-12 h-12 rounded-full border transition-all duration-200"
              style={{
                fontFamily: "'Orbitron', sans-serif",
                fontSize: "7px",
                fontWeight: 700,
                color: isSpeaking ? "#ff4444" : "#4a9ebb",
                background: "transparent",
                borderColor: isSpeaking ? "#ff4444" : "rgba(0,180,216,0.4)",
                boxShadow: isSpeaking ? "0 0 12px #ff444488" : "none",
                cursor: "pointer",
              }}
              title={isSpeaking ? "Stop speaking" : "Clear chat"}
            >
              {isSpeaking ? "STOP" : "CLR"}
            </button>

            {/* SYS */}
            <button
              onClick={() => sendMessage("Run a full system diagnostic report.")}
              disabled={isProcessing || isSpeaking || isListening}
              className="w-12 h-12 rounded-full border transition-all duration-200 disabled:opacity-40"
              style={{
                fontFamily: "'Orbitron', sans-serif",
                fontSize: "8px",
                fontWeight: 700,
                color: "#4a9ebb",
                background: "transparent",
                borderColor: "rgba(0,180,216,0.4)",
                cursor: isProcessing || isSpeaking || isListening ? "not-allowed" : "pointer",
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#00ffff"; e.currentTarget.style.color = "#00ffff"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(0,180,216,0.4)"; e.currentTarget.style.color = "#4a9ebb"; }}
            >
              SYS
            </button>
          </div>
        </div>

        {/* RIGHT PANEL — TRANSCRIPT */}
        <div
          className="flex flex-col border-l overflow-hidden"
          style={{ borderColor: "rgba(0,180,216,0.1)" }}
        >
          <div
            className="flex items-center gap-2 px-4 py-3 border-b shrink-0"
            style={{ borderColor: "rgba(0,180,216,0.1)" }}
          >
            <div
              className="w-1.5 h-1.5 rounded-full bg-cyan-400"
              style={{ boxShadow: "0 0 6px #00ffff" }}
            />
            <span
              className="text-cyan-400/80 uppercase tracking-widest"
              style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "10px", fontWeight: 600 }}
            >
              Transcript
            </span>
            <span
              className="ml-auto text-muted-foreground"
              style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: "9px" }}
            >
              {messages.length} msg{messages.length !== 1 ? "s" : ""}
            </span>
          </div>

          <div className="flex-1 overflow-hidden p-3">
            <Transcript messages={messages} isProcessing={isProcessing} />
          </div>
        </div>
      </div>

      {/* BOTTOM INPUT */}
      <div
        className="flex items-center gap-3 px-4 py-3 border-t shrink-0"
        style={{ borderColor: "rgba(0,180,216,0.15)", background: "rgba(0,10,25,0.8)" }}
      >
        <span
          className="text-cyan-400/60 shrink-0"
          style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: "12px" }}
        >
          &gt;_
        </span>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") sendMessage(input); }}
          placeholder={
            isListening
              ? "Listening..."
              : isProcessing
              ? "Processing..."
              : isSpeaking
              ? "JARVIS is speaking..."
              : "Type a command or question..."
          }
          disabled={isProcessing || isSpeaking || isListening}
          className="flex-1 bg-transparent outline-none disabled:opacity-50"
          style={{
            fontFamily: "'Share Tech Mono', monospace",
            fontSize: "12px",
            color: "#a8d8ea",
            caretColor: "#00ffff",
          }}
        />
        {input.trim() && !isProcessing && !isSpeaking && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => sendMessage(input)}
            className="px-4 py-1.5 border transition-all duration-200"
            style={{
              fontFamily: "'Rajdhani', sans-serif",
              fontSize: "10px",
              fontWeight: 700,
              color: "#00ffff",
              borderColor: "rgba(0,255,255,0.4)",
              background: "rgba(0,255,255,0.05)",
              cursor: "pointer",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
            }}
          >
            SEND
          </motion.button>
        )}
      </div>

      {/* Footer */}
      <div
        className="flex items-center justify-between px-4 py-1.5 shrink-0"
        style={{ borderTop: "1px solid rgba(0,180,216,0.08)" }}
      >
        <span
          className="text-muted-foreground/40 uppercase tracking-widest"
          style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "8px" }}
        >
          STARK INDUSTRIES ⬥ A.I. DIVISION ⬥ BUILD v8.3.1
        </span>
        <span
          className="text-muted-foreground/40 uppercase tracking-widest"
          style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: "8px" }}
        >
          ENCRYPTION: AES-256 ⬥ AI: CLAUDE HAIKU
        </span>
      </div>
    </div>
  );
}
