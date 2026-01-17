"""System monitoring module for real-time metrics."""
import psutil
import platform
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitors system resources and processes."""
    
    def __init__(self):
        self.platform = platform.system()
    
    def get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.error(f"Error getting CPU percent: {e}")
            return 0.0
    
    def get_memory_percent(self) -> float:
        """Get current memory usage percentage."""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logger.error(f"Error getting memory percent: {e}")
            return 0.0
    
    def get_top_processes(self, limit: int = 4) -> List[Dict[str, any]]:
        """Get top processes by CPU usage."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is None:
                        proc_info['cpu_percent'] = 0.0
                    if proc_info['memory_percent'] is None:
                        proc_info['memory_percent'] = 0.0
                    
                    processes.append({
                        'name': proc_info['name'] or 'Unknown',
                        'cpu': proc_info['cpu_percent'],
                        'mem': proc_info['memory_percent'],
                        'pid': proc_info['pid']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU usage and get top N
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            top_processes = processes[:limit]
            
            # Format for display
            formatted = []
            for proc in top_processes:
                formatted.append({
                    'name': proc['name'][:20],  # Truncate long names
                    'cpu': f"{proc['cpu']:.1f}%",
                    'mem': f"{proc['mem']:.1f}%"
                })
            
            return formatted
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return [
                {'name': 'ANAY Core', 'cpu': '0.0%', 'mem': '0.0%'},
                {'name': 'System', 'cpu': '0.0%', 'mem': '0.0%'}
            ]
    
    def get_system_info(self) -> Dict[str, any]:
        """Get comprehensive system information."""
        try:
            cpu_percent = self.get_cpu_percent()
            memory_percent = self.get_memory_percent()
            top_processes = self.get_top_processes(4)
            
            return {
                'cpu_load': round(cpu_percent, 1),
                'ram_usage': round(memory_percent, 1),
                'processes': top_processes,
                'platform': self.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                'cpu_load': 0.0,
                'ram_usage': 0.0,
                'processes': [],
                'platform': 'Unknown',
                'cpu_count': 0,
                'memory_total_gb': 0.0,
                'memory_used_gb': 0.0,
            }


# Global system monitor instance
system_monitor = SystemMonitor()
