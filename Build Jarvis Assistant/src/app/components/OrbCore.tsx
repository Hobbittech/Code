import { motion } from "motion/react";

interface OrbCoreProps {
  isListening: boolean;
  isProcessing: boolean;
}

export function OrbCore({ isListening, isProcessing }: OrbCoreProps) {
  return (
    <div className="relative flex items-center justify-center w-64 h-64">
      {/* Outer rings */}
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          className="absolute rounded-full border border-cyan-500/20"
          style={{ width: `${i * 80}px`, height: `${i * 80}px` }}
          animate={{ rotate: 360 * (i % 2 === 0 ? 1 : -1) }}
          transition={{ duration: 8 + i * 4, repeat: Infinity, ease: "linear" }}
        />
      ))}

      {/* Pulsing rings */}
      {isListening && (
        <>
          {[0, 1, 2].map((i) => (
            <motion.div
              key={`pulse-${i}`}
              className="absolute rounded-full border border-cyan-400/40"
              style={{ width: "120px", height: "120px" }}
              animate={{ scale: [1, 2.5], opacity: [0.6, 0] }}
              transition={{ duration: 2, repeat: Infinity, delay: i * 0.6, ease: "easeOut" }}
            />
          ))}
        </>
      )}

      {/* Processing spin */}
      {isProcessing && (
        <motion.div
          className="absolute w-36 h-36 rounded-full border-2 border-transparent border-t-cyan-400 border-r-cyan-400/50"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      )}

      {/* Core glow layers */}
      <div className="absolute w-28 h-28 rounded-full bg-blue-500/10 blur-2xl" />
      <div className="absolute w-20 h-20 rounded-full bg-cyan-400/20 blur-xl" />

      {/* Core orb */}
      <motion.div
        className="relative w-16 h-16 rounded-full"
        style={{
          background: "radial-gradient(circle at 35% 35%, #ffffff, #00d4ff, #0066cc, #001133)",
          boxShadow: isListening
            ? "0 0 40px #00ffff, 0 0 80px #0099ff, 0 0 120px #0066ff"
            : isProcessing
            ? "0 0 30px #00ccff, 0 0 60px #0077ff"
            : "0 0 20px #0099cc, 0 0 40px #0055aa",
        }}
        animate={{
          scale: isListening ? [1, 1.15, 1] : [1, 1.04, 1],
        }}
        transition={{ duration: isListening ? 0.8 : 3, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Hex corner decorations */}
      {[0, 90, 180, 270].map((deg) => (
        <div
          key={deg}
          className="absolute w-3 h-3 border-t border-l border-cyan-400/60"
          style={{
            transform: `rotate(${deg}deg)`,
            top: deg === 0 || deg === 270 ? "12px" : "auto",
            bottom: deg === 180 || deg === 90 ? "12px" : "auto",
            left: deg === 0 || deg === 90 ? "12px" : "auto",
            right: deg === 180 || deg === 270 ? "12px" : "auto",
          }}
        />
      ))}
    </div>
  );
}
