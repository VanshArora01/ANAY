"""
System Control Module (Refactored)
Focuses on OS-level process management, app launching, and system info.
"""
import logging
import psutil
import subprocess
import os
import platform
from typing import List, Dict
from automation.context_manager import ContextManager

logger = logging.getLogger(__name__)

class SystemControl:
    """Controls OS processes and applications."""
    
    def __init__(self):
        self.os_type = platform.system()
        self.ctx_mgr = ContextManager()
        
    def get_system_stats(self) -> Dict:
        """Get CPU/RAM usage."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "battery": self._get_battery(),
            "os": self.os_type
        }

    def _get_battery(self):
        try:
            battery = psutil.sensors_battery()
            return {"percent": battery.percent, "plugged": battery.power_plugged} if battery else "Unknown"
        except: return "No Battery"

    def launch_app(self, app_name: str):
        """Intelligent application launcher."""
        try:
            # Common paths map (Simplified)
            common_apps = {
                "calculator": "calc.exe",
                "notepad": "notepad.exe",
                "chrome": "chrome.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "spotify": "spotify.exe",
                "code": "code", # VS Code
                "vscode": "code",
                "cursor": os.path.expanduser("~/AppData/Local/Programs/cursor/Cursor.exe"),
                "comet": "comet.exe" # Assuming in path
            }
            
            cmd = common_apps.get(app_name.lower(), app_name)
            
            # Special handling for VS Code if not in path
            if app_name.lower() in ["code", "vs code", "vscode"]:
                cmd = "code"
                
            # Special handling for Cursor
            if app_name.lower() == "cursor":
                cursor_path = os.path.expanduser("~/AppData/Local/Programs/cursor/Cursor.exe")
                if os.path.exists(cursor_path):
                    cmd = cursor_path
                else:
                    cmd = "Cursor.exe" # Hope it's in path
            
            if self.os_type == "Windows":
                 subprocess.Popen(cmd, shell=True)
            elif self.os_type == "Darwin": # MacOS
                 subprocess.Popen(["open", "-a", app_name])
            else:
                 subprocess.Popen([app_name])
                 
            self.ctx_mgr.update_context({"last_opened_app": app_name})
            return True, f"Launched {app_name}"
        except Exception as e:
            return False, f"Failed to launch: {e}"

    def close_app(self, app_name: str):
        """Kill a process by name."""
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if app_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed_count > 0:
            return True, f"Closed {killed_count} instances of {app_name}"
        return False, f"No running process found for {app_name}"

    def shutdown(self):
        if self.os_type == "Windows":
            os.system("shutdown /s /t 10")
        else:
            os.system("shutdown now")
        return True, "Initiating shutdown in 10s"
