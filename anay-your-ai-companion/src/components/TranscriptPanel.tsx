import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface TranscriptPanelProps {
  messages: Message[];
  isListening?: boolean;
}

const TranscriptPanel = ({ messages }: TranscriptPanelProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  return (
    <div className="anay-panel h-full flex flex-col bg-[#050505] border-[#1a1a1a] overflow-hidden relative">
      {/* Header */}
      <div className="p-3 flex items-center gap-2 flex-shrink-0">
        <div className="w-1.5 h-3 bg-primary/40 rounded-sm" />
        <h2 className="font-orbitron text-[10px] md:text-xs tracking-widest text-[#00f5d4] font-bold uppercase">
          TRANSCRIPT
        </h2>
      </div>

      {/* Messages - Scrollable Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-3 space-y-6 custom-scrollbar"
      >
        <AnimatePresence mode="popLayout">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              {/* Header Label */}
              <div className="flex items-center gap-2 mb-1 px-1">
                <span className={`text-[10px] font-orbitron font-black tracking-widest ${message.role === 'user' ? 'text-foreground/40' : 'text-[#00f5d4]'
                  }`}>
                  {message.role === 'user' ? 'YOU' : 'ANAY'}
                </span>
              </div>

              {/* Message Content */}
              <div className={`max-w-[90%] px-4 py-2.5 rounded-lg border text-[13px] leading-relaxed font-rajdhani font-medium ${message.role === 'user'
                ? 'bg-[#0a0a0a] border-white/5 text-foreground/80 rounded-tr-none'
                : 'bg-[#0f1a1a]/40 border-[#00f5d4]/10 text-foreground/90 rounded-tl-none'
                }`}>
                {message.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-foreground/10 tracking-[0.2em] py-20 uppercase font-orbitron font-bold">
            WAITING FOR INPUT...
          </div>
        )}
      </div>
    </div>
  );
};

export default TranscriptPanel;
