"""
Task Planner Module
The "Brain" that orchestrates automation tools based on user prompts.
"""
import logging
import json
import re
from typing import Dict, Any, List, Optional
import asyncio

# Import our tools
from automation.system_control import SystemControl
from automation.file_manager import FileManager
from automation.browser_agent import BrowserAgent
from automation.input_controller import InputController
from automation.safety_guard import SafetyGuard
from automation.context_manager import ContextManager

logger = logging.getLogger(__name__)

class TaskPlanner:
    """
    Decomposes natural language requests into executable tool commands.
    Uses Persistent Context to resolve intent.
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client  # Expects GroqLLM or similar interface
        
        # Initialize Tools
        self.system = SystemControl()
        self.files = FileManager()
        self.browser = BrowserAgent()
        self.input = InputController()
        self.safety = SafetyGuard()
        self.ctx = ContextManager()
        
    async def execute_plan(self, user_prompt: str) -> str:
        """
        Main entry point:
        1. Load Context
        2. Resolve Intent (is it a knowledge query or action?)
        3. Break down step-by-step
        4. Execute
        """
        context = self.ctx.get_context()
        logger.info(f"Planning with context: {context}")
        
        # 1. Expand "it", "this" using Context Logic
        refined_prompt = self._resolve_references(user_prompt, context)
        logger.info(f"Refined Prompt: {refined_prompt}")
        
        # 2. Generate Plan using LLM
        plan = await self._generate_plan(refined_prompt, context)
        
        # 3. Validation
        if not plan or not plan.get("steps"):
            logger.info("No execution steps found. Treating as conversational/knowledge query.")
            # If the plan is empty, it means the LLM thinks it's not a PC automation task.
            # In this architecture, we return specific signal or string for the main loop to handle conversational reply.
            return "NO_ACTION_REQUIRED"

        # 4. Execution Loop
        results = []
        for step in plan.get("steps", []):
            tool = step.get("tool")
            action = step.get("action")
            params = step.get("params", {})
            
            # Safety Check
            is_safe, reason = self.safety.validate_action(tool, params)
            if not is_safe:
                logger.warning(f"Safety Block: {reason}")
                return f"I couldn't complete the task because: {reason}"
                
            # Execute
            try:
                res = self._run_tool(tool, action, params)
                
                # Intelligent Output Filtering
                # If tuple (True, "Message"), take message.
                # If tuple (True,), ignore.
                # If boolean, ignore.
                msg = ""
                if isinstance(res, tuple) and len(res) >= 2:
                    msg = str(res[1])
                elif isinstance(res, str):
                    msg = res
                
                # Only append meaningful messages
                if msg and "True" not in msg and "False" not in msg:
                    results.append(msg)
                    
            except Exception as e:
                logger.error(f"Execution Error on {action}: {e}")
                return f"Error executing step {action}: {e}"
        
        # 5. Summarize
        if not results:
            summary = "Done." # Fallback if only booleans returned
        else:
            summary = " and ".join(results)
            
        self.ctx.update_context({"last_task_summary": summary})
        
        # Return the clean summary to be spoken
        return summary

    def _resolve_references(self, text: str, ctx: Dict) -> str:
        """
        Replace pronouns with actual context paths.
        """
        lower_text = text.lower()
        
        # Priority resolution
        target_file = (
            ctx.get("last_modified_file") or 
            ctx.get("last_opened_file") or 
            ctx.get("last_created_file")
        )
        
        target_app = ctx.get("last_opened_app")
        
        if target_file and (" it" in lower_text or "that file" in lower_text or "the file" in lower_text):
            # Simple replacement strategy
            text = re.sub(r'\b(it|that file|the file)\b', f'the file "{target_file}"', text, flags=re.IGNORECASE)
        
        # Specific code fix resolution
        if target_file and ("fix the code" in lower_text or "modify the code" in lower_text):
             text = text.replace("the code", f'the code in "{target_file}"')
             
        if target_app and ("that app" in lower_text or "close it" in lower_text):
             text = re.sub(r'\b(that app)\b', f'{target_app}', text, flags=re.IGNORECASE)
            
        return text

    async def _generate_plan(self, prompt: str, context: Dict) -> Dict:
        """
        Ask LLM to generate a JSON plan.
        """
        if not self.llm:
            logger.warning("No LLM client available for planning.")
            return {"steps": []}
            
        system_prompt = """
        You are ANAY, an Execution-First AI Agent for Windows PC.
        Your goal is to convert user requests into a JSON series of tool executions.
        
        CURRENT SYSTEM CONTEXT:
        <<CONTEXT>>
        
        IMPORTANT PATHS:
        - Desktop: C:/Users/vansh/OneDrive/Desktop
        - Documents: C:/Users/vansh/OneDrive/Documents
        
        AVAILABLE TOOLS:
        
        1. system_control:
           - launch_app(app_name): e.g. "notepad", "chrome", "code", "spotify".
           - close_app(app_name): Close a running process.
           - shutdown(): Turn off PC.
           
        2. file_manager:
           - write_file(path, content): Create/Edit file. PATH MUST BE ABSOLUTE using FORWARD SLASHES.
           - read_file(path): Read content.
           - create_folder(path): Make new dir.
           - delete_item(path): Delete file/folder.
           - list_files(path): List dir contents.
           
        3. input_controller:
           - type_text(text): Types text.
           - press_key(key): Keys: 'enter', 'esc', 'tab', 'space', 'backspace'.
           - hotkey(keys): e.g. ['ctrl', 'l'] (Focus Address Bar/Search), ['ctrl', 'w'] (Close Tab).
           - wait(seconds): PAUSE for UI to load. CRITICAL for app launching.
           - media_play_pause(), media_next(), volume_up().
           
        RULES:
        1. **ACTION OVER CHAT**: Always execute if possible.
        2. **APP NAVIGATION**: You have keyboard control. Use it to search and navigate inside apps.
        3. **SPOTIFY SEARCH WORKFLOW**:
           - To "Play [Song]":
             1. `launch_app("spotify")`
             2. `wait(5.0)` (CRITICAL: Wait for the app to fully load and take focus)
             3. `hotkey(['ctrl', 'k'])` (Open Quick Search)
             4. `wait(2.0)` (Wait for Search UI to animate and focus)
             5. `type_text("[Song Name]")`
             6. `wait(1.0)` (Wait for results to populate)
             7. `press_key("enter")` (Play Top Result)
        4. **PATH FORMATTING**: Use FORWARD SLASHES (/).
        
        Example 1 (Complex Spotify):
        User: "Play 52 bars on spotify"
        JSON:
        {
            "steps": [
                {"tool": "system_control", "action": "launch_app", "params": {"app_name": "spotify"}},
                {"tool": "input_controller", "action": "wait", "params": {"seconds": 5.0}},
                {"tool": "input_controller", "action": "hotkey", "params": {"keys": ["ctrl", "k"]}},
                {"tool": "input_controller", "action": "wait", "params": {"seconds": 2.0}},
                {"tool": "input_controller", "action": "type_text", "params": {"text": "on top"}},
                {"tool": "input_controller", "action": "wait", "params": {"seconds": 1.0}},
                {"tool": "input_controller", "action": "press_key", "params": {"key": "enter"}}
            ]
        }
        
        Example 2 (File):
        User: "Create hello.txt on desktop"
        JSON:
        {
            "steps": [
                 {"tool": "file_manager", "action": "write_file", "params": {"path": "C:/Users/vansh/OneDrive/Desktop/hello.txt", "content": "Hello"}}
            ]
        }
        
        Example 3 (Chat/Knowledge):
        User: "Tell me a joke"
        JSON:
        { "steps": [] }
        """
        
        # Inject Context logic
        context_str = json.dumps(context, indent=2)
        system_prompt = system_prompt.replace("<<CONTEXT>>", context_str)
        
        try:
            # Call LLM
            user_msg = f"User Request: {prompt}\nJSON Plan:"
            
            # Check capabilities
            import inspect
            sig = inspect.signature(self.llm.generate_response)
            if 'system_prompt' in sig.parameters:
                response_text = await asyncio.to_thread(self.llm.generate_response, user_msg, system_prompt=system_prompt)
            else:
                response_text = await asyncio.to_thread(self.llm.generate_response, f"{system_prompt}\n\n{user_msg}")
            
            logger.info(f"Raw Planner Output: {response_text}")

            # Robust JSON Extraction
            # 1. Strip Markdown
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # 2. Extract from first { to last }
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_text = clean_text[start_idx : end_idx + 1]
            
            # Parse
            plan = json.loads(clean_text)
            return plan

        except Exception as e:
            logger.error(f"Planning failed/Parsing failed: {e}")
            logger.error(f"Failed Text: {response_text if 'response_text' in locals() else 'None'}")
            return {"steps": []}

    def _run_tool(self, tool_name: str, action: str, params: Dict):
        """Dynamic dispatch to tools."""
        tool_instance = getattr(self, tool_name.replace("_agent", "").replace("_controller", ""), None)
        
        # Map nice names to internal attributes
        if tool_name == "system_control": tool_instance = self.system
        elif tool_name == "file_manager": tool_instance = self.files
        elif tool_name == "browser_agent": tool_instance = self.browser
        elif tool_name == "input_controller": tool_instance = self.input

        if not tool_instance:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        method = getattr(tool_instance, action, None)
        if not method:
            raise ValueError(f"Unknown action: {action} in {tool_name}")
            
        return method(**params)
