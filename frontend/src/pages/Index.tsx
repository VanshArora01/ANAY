import { useState, useCallback, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import NavigationBar from '@/components/NavigationBar';
import VideoFeed from '@/components/VideoFeed';
import SystemMetrics from '@/components/SystemMetrics';
import CoreSystem from '@/components/CoreSystem';
import TranscriptPanel from '@/components/TranscriptPanel';
import ChatInput from '@/components/ChatInput';
import Contacts from './Contacts';
import Notes from './Notes';
import Connect from './Connect';
import Phone from './Phone';
import { useAnayChat } from '@/hooks/useAnayChat';
import { useRealtimeVoice } from '@/hooks/useRealtimeVoice';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isVideoOn, setIsVideoOn] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [status, setStatus] = useState<'idle' | 'listening' | 'processing' | 'speaking'>('idle');

  // Clear chat history on component mount (new session)
  useEffect(() => {
    localStorage.removeItem('chatHistory');
  }, []);

  const { toast } = useToast();
  const { messages, isProcessing, isConnected, sendMessage } = useAnayChat();

  // Debug messages
  useEffect(() => {
    console.log('📋 Current messages:', messages);
  }, [messages]);

  const stateRef = useRef({
    audioLevel: 0,
    status: 'idle' as 'idle' | 'listening' | 'processing' | 'speaking'
  });

  useEffect(() => {
    stateRef.current.status = status;
  }, [status]);


  const {
    isListening,
    isSpeaking,
    toggleListening,
    stopListening
  } = useRealtimeVoice({
    stateRef,
    onTranscript: (text, isFinal) => {
      if (isFinal) console.log('Final Transcript:', text);
    },
    onAiText: () => {
      setStatus('speaking');
    },
    onError: (err) => toast({ title: "Voice Error", description: err, variant: "destructive" })
  });

  const handleTextSend = useCallback(async (message: string) => {
    if (!message.trim()) return;
    setStatus('processing');
    await sendMessage(message);
    setStatus('idle');
  }, [sendMessage]);

  const handleMicToggle = useCallback(() => {
    toggleListening();
    if (!isListening) {
      setStatus('listening');
    } else {
      setStatus('idle');
    }
  }, [isListening, toggleListening]);

  const handleSessionStart = useCallback(async () => {
    // Send /start message to wake up ANAY
    await sendMessage("/start");
    setIsSessionActive(true);
    toast({
      title: "ANAY Activated! 🚀",
      description: "Aur yaar, kesa hai?",
    });
  }, [sendMessage, toast]);

  const handleSessionEnd = useCallback(() => {
    stopListening();
    setStatus('idle');
    setIsSessionActive(false);
    toast({
      title: "Session Ended",
      description: "Milte hain yaar, bye!",
    });
  }, [stopListening, toast]);

  const handleEnd = useCallback(() => {
    stopListening();
    setStatus('idle');
    toast({
      title: "Session Ended",
      description: "ANAY session has ended.",
    });
  }, [stopListening, toast]);

  const handleVideoToggle = useCallback(() => {
    setIsVideoOn(prev => !prev);
  }, []);

  // Render different pages based on activeTab
  const renderContent = () => {
    switch (activeTab) {
      case 'contacts':
        return <Contacts />;
      case 'notes':
        return <Notes />;
      case 'connect':
        return <Connect />;
      case 'phone':
        return <Phone />;
      default:
        // Dashboard view
        return (
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-0">
            {/* Left column: Visual Input & System Metrics */}
            <div className="lg:col-span-3 flex flex-col gap-3 min-h-0">
              <div className="h-[40%] flex-shrink-0">
                <VideoFeed isVideoOn={isVideoOn} onToggle={handleVideoToggle} />
              </div>
              <div className="flex-1 min-h-0">
                <SystemMetrics isOnline={isConnected} />
              </div>
            </div>

            {/* Center column: Core System (The biggest) */}
            <div className="lg:col-span-6 flex flex-col min-h-0">
              <CoreSystem
                stateRef={stateRef}
                isListening={isListening}
                isSpeaking={isSpeaking}
                isVideoOn={isVideoOn}
                onMicToggle={handleMicToggle}
                onVideoToggle={handleVideoToggle}
                onEnd={handleSessionEnd}
                onStart={handleSessionStart}
                isSessionActive={isSessionActive}
                status={isProcessing ? 'processing' : status}
              />
            </div>

            {/* Right column: Transcript */}
            <div className="lg:col-span-3 flex flex-col min-h-0 gap-3">
              <div className="flex-1 min-h-0">
                <TranscriptPanel messages={messages} isListening={isListening} />
              </div>
              <div className="flex-shrink-0">
                <ChatInput
                  onSend={handleTextSend}
                  isProcessing={isProcessing}
                  isListening={isListening}
                  onMicToggle={handleMicToggle}
                  onVoiceInput={handleTextSend}
                />
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="h-screen w-screen bg-[#020202] text-foreground overflow-hidden flex flex-col p-3 md:p-4 gap-3 font-rajdhani">
      {/* Top Navigation */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex-shrink-0"
      >
        <NavigationBar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          isOnline={isConnected}
        />
      </motion.div>

      {/* Main Content */}
      {renderContent()}

      {/* Footer Credits */}
      <div className="flex-shrink-0 flex items-center justify-center py-1 opacity-40">
        <span className="text-[8px] md:text-[10px] font-orbitron font-bold tracking-[0.3em] uppercase">
          CREATED WITH <span className="text-red-500 mx-1">❤</span> DATA DYNAMO
        </span>
      </div>
    </div>
  );
};

export default Index;