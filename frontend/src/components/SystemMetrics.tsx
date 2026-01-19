import { useEffect, useState } from 'react';
import { useAnayChat } from '@/hooks/useAnayChat';
import { ANAYWebSocket } from '@/lib/websocket';

interface SystemMetricsProps {
  isOnline?: boolean;
}

interface SystemMetricsData {
  cpu_load: number;
  ram_usage: number;
  processes: Array<{ name: string; cpu: string; mem: string }>;
}

const SystemMetrics = ({ isOnline = true }: SystemMetricsProps) => {
  const [cpuLoad, setCpuLoad] = useState(0);
  const [ramUsage, setRamUsage] = useState(0);
  const [processes, setProcesses] = useState<Array<{ name: string; cpu: string; mem: string }>>([]);
  const { isConnected } = useAnayChat();

  useEffect(() => {
    if (!isConnected) {
      setCpuLoad(0);
      setRamUsage(0);
      setProcesses([]);
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    const ws = new ANAYWebSocket(wsUrl);

    const handleMetrics = (data: any) => {
      if (data.type === 'system_metrics' && data.data) {
        const metrics: SystemMetricsData = data.data;
        setCpuLoad(metrics.cpu_load || 0);
        setRamUsage(metrics.ram_usage || 0);
        setProcesses(metrics.processes || []);
      }
    };

    ws.on('system_metrics', handleMetrics);
    ws.on('open', () => {
      ws.send({ type: 'request_metrics' });
    });

    ws.connect().catch(console.error);

    return () => {
      ws.disconnect();
    };
  }, [isConnected]);

  return (
    <div className="anay-panel h-full flex flex-col bg-[#050505] border-[#1a1a1a] overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/5 flex items-center justify-between flex-shrink-0 bg-white/[0.02]">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse-slow" />
            <div className="absolute inset-0 bg-primary/40 rounded-full blur-[2px] animate-pulse" />
          </div>
          <h2 className="font-orbitron text-[10px] md:text-xs tracking-[0.3em] text-white font-black uppercase">
            CORE TELEMETRY
          </h2>
        </div>
        <div className="flex items-center gap-2 px-2 py-1 rounded-md bg-white/[0.03] border border-white/5">
          <div className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-anay-green shadow-[0_0_8px_#00f5d4]' : 'bg-destructive shadow-[0_0_8px_#ef4444]'}`} />
          <span className={`text-[8px] font-orbitron font-black tracking-widest ${isOnline ? 'text-anay-green' : 'text-red-400'}`}>
            {isOnline ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>
      </div>

      {/* Metrics Area */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-3 custom-scrollbar">
        {/* CPU & RAM Cards */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-[#111] border border-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-4 h-4 rounded-sm border border-primary/40 flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-primary/60" />
              </div>
              <span className="text-[9px] font-orbitron text-foreground/40 font-bold uppercase tracking-widest">CPU LOAD</span>
            </div>
            <div className="flex items-end gap-1">
              <span className="text-xl font-orbitron font-black text-foreground">{cpuLoad.toFixed(0)}</span>
              <span className="text-xs font-orbitron text-foreground/30 mb-1">%</span>
            </div>
          </div>

          <div className="bg-[#111] border border-white/5 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-4 h-4 rounded-full border border-[#d946ef]/40 flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-[#d946ef]/60 rounded-full" />
              </div>
              <span className="text-[9px] font-orbitron text-foreground/40 font-bold uppercase tracking-widest">RAM USAGE</span>
            </div>
            <div className="flex items-end gap-1">
              <span className="text-xl font-orbitron font-black text-foreground">{ramUsage.toFixed(0)}</span>
              <span className="text-xs font-orbitron text-foreground/30 mb-1">%</span>
              <span className="text-[9px] font-orbitron text-foreground/40 ml-auto mb-1">{(ramUsage * 0.16).toFixed(1)} GB</span>
            </div>
          </div>
        </div>

        {/* Processes Table */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 px-1">
            <div className="w-3 h-2 border-b-2 border-primary/40" />
            <span className="text-[9px] font-orbitron text-foreground/40 font-bold uppercase tracking-widest">TOP PROCESSES</span>
          </div>

          <div className="bg-[#111]/40 rounded-lg overflow-hidden border border-white/5">
            <div className="grid grid-cols-12 gap-1 px-3 py-1.5 border-b border-white/5 text-[8px] font-orbitron font-bold text-foreground/30 tracking-widest">
              <span className="col-span-8">APP NAME</span>
              <span className="col-span-2 text-right">CPU</span>
              <span className="col-span-2 text-right">MEM</span>
            </div>

            <div className="max-h-[180px] overflow-y-auto custom-scrollbar">
              {processes.length > 0 ? processes.map((proc, i) => (
                <div key={i} className="grid grid-cols-12 gap-1 px-3 py-1.5 border-b border-white/5 hover:bg-white/5 transition-colors group">
                  <span className="col-span-8 text-[10px] text-foreground/70 truncate font-rajdhani">{proc.name}</span>
                  <span className="col-span-2 text-right text-[10px] font-orbitron text-[#00f5d4] group-hover:text-primary transition-colors">{proc.cpu}</span>
                  <span className="col-span-2 text-right text-[10px] font-orbitron text-[#d946ef] group-hover:text-pink-400 transition-colors uppercase">{proc.mem}</span>
                </div>
              )) : (
                <div className="p-8 text-center text-[9px] font-orbitron text-foreground/20 italic tracking-widest">
                  FETCHING SYSTEM TELEMETRY...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMetrics;
