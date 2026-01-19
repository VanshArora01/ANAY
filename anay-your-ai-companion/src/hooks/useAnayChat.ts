import { useState, useCallback, useEffect, useRef } from 'react';
import { ANAYWebSocket, ServerMessage } from '@/lib/websocket';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const useAnayChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<ANAYWebSocket | null>(null);
  const pendingResolveRef = useRef<((value: string) => void) | null>(null);

  // Load messages from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatHistory');
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        // Convert string dates back to Date objects
        const messagesWithDates = parsedMessages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(messagesWithDates);
      } catch (error) {
        console.error('Failed to parse saved messages:', error);
        setMessages([]);
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    try {
      // Convert Date objects to strings for storage
      const messagesForStorage = messages.map(({ timestamp, ...rest }) => ({
        ...rest,
        timestamp: timestamp.toISOString()
      }));
      localStorage.setItem('chatHistory', JSON.stringify(messagesForStorage));
    } catch (error) {
      console.error('Failed to save messages:', error);
    }
  }, [messages]);

  // Initialize WebSocket connection
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    console.log('🔌 Connecting to WebSocket (Shared Instance):', wsUrl);
    const ws = ANAYWebSocket.getInstance(wsUrl);
    wsRef.current = ws;

    // Listener functions for proper cleanup
    const onOpen = () => {
      setIsConnected(true);
      console.log('✅ WebSocket connected');
    };

    // Check initial connection state
    if (ws.isConnected()) {
      onOpen();
    }

    const onClose = () => {
      setIsConnected(false);
      console.log('❌ WebSocket disconnected');
    };

    const onErrorEvent = (data: any) => {
      console.error('❌ WebSocket error:', data);
      setIsConnected(false);
    };

    const onMessage = (data: ServerMessage) => {
      console.log('📬 useAnayChat received message:', data.type, data);
    };

    const onUserMessage = (data: ServerMessage) => {
      if (data.type === 'user_message') {
        const content = data.content || data.message || data.text || '';
        if (content.trim()) {
          console.log('📝 Adding user message to transcript:', content);
          const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: content,
            timestamp: new Date(),
          };
          setMessages(prev => {
            const exists = prev.some(msg =>
              msg.content === content &&
              msg.role === 'user' &&
              Math.abs(msg.timestamp.getTime() - userMsg.timestamp.getTime()) < 1000
            );
            if (exists) return prev;
            return [...prev, userMsg];
          });
        }
      }
    };

    const onFinalTranscript = (data: ServerMessage) => {
      if (data.type === 'final_transcript') {
        const content = data.payload || data.text || '';
        if (content.trim()) {
          console.log('📝 Adding final transcript to transcript:', content);
          const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: content,
            timestamp: new Date(),
          };
          setMessages(prev => {
            const exists = prev.some(msg => msg.content === content && msg.role === 'user');
            if (exists) return prev;
            return [...prev, userMsg];
          });
        }
      }
    };

    const onTranscript = (data: ServerMessage) => {
      if (data.type === 'transcript') {
        const content = data.text || data.payload || '';
        const role = (data as any).role === 'assistant' ? 'assistant' : 'user';
        if (content.trim()) {
          console.log('📝 Adding transcript to chat:', content, 'role:', role);
          const newMsg: Message = {
            id: Date.now().toString(),
            role: role,
            content: content,
            timestamp: new Date(),
          };
          setMessages(prev => {
            const exists = prev.some(msg =>
              msg.content === content &&
              msg.role === role &&
              Math.abs(msg.timestamp.getTime() - newMsg.timestamp.getTime()) < 2000
            );
            if (exists) return prev;
            return [...prev, newMsg];
          });
        }
      }
    };

    const onResponse = (data: ServerMessage) => {
      if (data.type === 'response') {
        const content = data.content || data.message || data.text || '';
        if (content.trim()) {
          console.log('🤖 Adding AI response to transcript:', content);
          const aiMsg: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: content,
            timestamp: new Date(),
          };
          setMessages(prev => {
            const exists = prev.some(msg =>
              msg.content === content &&
              msg.role === 'assistant' &&
              Math.abs(msg.timestamp.getTime() - aiMsg.timestamp.getTime()) < 2000
            );
            if (exists) return prev;
            return [...prev, aiMsg];
          });
          setIsProcessing(false);
          if (pendingResolveRef.current) {
            pendingResolveRef.current(content);
            pendingResolveRef.current = null;
          }
        }
      }
    };

    const onAiMessage = (data: ServerMessage) => {
      if (data.type === 'ai_message') {
        const content = data.content || data.text || '';
        if (content.trim()) {
          const aiMsg: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: content,
            timestamp: new Date(),
          };
          setMessages(prev => {
            const exists = prev.some(msg =>
              msg.content === content &&
              msg.role === 'assistant' &&
              Math.abs(msg.timestamp.getTime() - aiMsg.timestamp.getTime()) < 2000
            );
            if (exists) return prev;
            return [...prev, aiMsg];
          });
          setIsProcessing(false);
        }
      }
    };

    const onAiText = (data: ServerMessage) => {
      if (data.type === 'ai_text' && data.payload) {
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.payload,
          timestamp: new Date(),
        };
        setMessages(prev => {
          const exists = prev.some(msg =>
            msg.content === data.payload &&
            msg.role === 'assistant' &&
            Math.abs(msg.timestamp.getTime() - aiMsg.timestamp.getTime()) < 2000
          );
          if (exists) return prev;
          return [...prev, aiMsg];
        });
        setIsProcessing(false);
        if (pendingResolveRef.current) {
          pendingResolveRef.current(data.payload);
          pendingResolveRef.current = null;
        }
      }
    };

    const onStatus = (data: ServerMessage) => {
      if (data.type === 'status') {
        if (data.status === 'processing') setIsProcessing(true);
        else if (data.status === 'idle') setIsProcessing(false);
      }
    };

    const onSystemAction = (data: ServerMessage) => {
      if (data.type === 'system_action') {
        console.log('System action:', data);
      }
    };

    const onError = (data: ServerMessage) => {
      if (data.type === 'error') {
        const errorMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || 'माफ करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMsg]);
        setIsProcessing(false);
        if (pendingResolveRef.current) {
          pendingResolveRef.current(errorMsg.content);
          pendingResolveRef.current = null;
        }
      }
    };

    // Register listeners
    ws.on('open', onOpen);
    ws.on('close', onClose);
    ws.on('error', onErrorEvent);
    ws.on('message', onMessage);
    ws.on('user_message', onUserMessage);
    ws.on('final_transcript', onFinalTranscript);
    ws.on('transcript', onTranscript);
    ws.on('response', onResponse);
    ws.on('ai_message', onAiMessage);
    ws.on('ai_text', onAiText);
    ws.on('status', onStatus);
    ws.on('system_action', onSystemAction);
    ws.on('error', onError);

    // Connect to WebSocket
    ws.connect().catch(console.error);

    // Cleanup on unmount
    return () => {
      ws.off('open', onOpen);
      ws.off('close', onClose);
      ws.off('error', onErrorEvent);
      ws.off('message', onMessage);
      ws.off('user_message', onUserMessage);
      ws.off('final_transcript', onFinalTranscript);
      ws.off('transcript', onTranscript);
      ws.off('response', onResponse);
      ws.off('ai_message', onAiMessage);
      ws.off('ai_text', onAiText);
      ws.off('status', onStatus);
      ws.off('system_action', onSystemAction);
      ws.off('error', onError);
    };
  }, []);

  const sendMessage = useCallback(async (userMessage: string): Promise<string> => {
    if (!userMessage.trim()) return '';

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsProcessing(true);

    return new Promise<string>((resolve) => {
      if (!wsRef.current || !wsRef.current.isConnected()) {
        // Try to connect first
        wsRef.current?.connect().then(() => {
          if (wsRef.current?.isConnected()) {
            pendingResolveRef.current = resolve;
            wsRef.current.send({
              type: 'message',
              content: userMessage,
            });
          } else {
            setIsProcessing(false);
            const errorMsg: Message = {
              id: (Date.now() + 1).toString(),
              role: 'assistant',
              content: 'Connection error: Please check backend server.',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMsg]);
            resolve(errorMsg.content);
          }
        }).catch(() => {
          setIsProcessing(false);
          const errorMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: 'कनेक्शन समस्या: कृपया बैकएंड सर्वर चेक करें।',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMsg]);
          resolve(errorMsg.content);
        });
      } else {
        pendingResolveRef.current = resolve;
        wsRef.current.send({
          type: 'message',
          content: userMessage,
        });
      }
    });
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem('chatHistory');
  }, []);

  return {
    messages,
    isProcessing,
    isConnected,
    sendMessage,
    clearMessages,
  };
};