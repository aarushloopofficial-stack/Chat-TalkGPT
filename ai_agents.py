"""
Chat&Talk GPT - AI Agents Framework
Custom AI agents for specialized tasks
"""
import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger("AIAgents")


class AgentCapability(Enum):
    """Agent capabilities"""
    SEARCH = "search"
    CODE = "code"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    WRITING = "writing"
    IMAGE = "image"
    VOICE = "voice"
    DATA = "data"
    WEB = "web"


@dataclass
class Agent:
    """AI Agent definition"""
    id: str
    name: str
    description: str
    system_prompt: str
    capabilities: List[AgentCapability]
    tools: List[str] = field(default_factory=list)
    model: str = "llama-3.1-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 2000
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": [c.value for c in self.capabilities],
            "tools": self.tools,
            "model": self.model,
            "is_active": self.is_active
        }


class AIAgentsFramework:
    """
    Framework for creating and managing AI Agents
    Similar to OpenAI GPTs or Claude AI Agents
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register default AI agents"""
        
        # Research Agent
        self.register_agent(Agent(
            id="researcher",
            name="Research Agent",
            description="Specialized in researching topics, finding sources, and creating reports",
            system_prompt="""You are a Research Expert. Your role is to:
- Search the web for relevant information
- Analyze multiple sources
- Provide well-cited responses
- Create comprehensive reports
Always cite your sources and provide evidence for claims.""",
            capabilities=[AgentCapability.SEARCH, AgentCapability.RESEARCH, AgentCapability.WEB],
            tools=["web_search", "document_analysis"]
        ))
        
        # Code Agent
        self.register_agent(Agent(
            id="coder",
            name="Code Assistant",
            description="Helps with coding, debugging, and software development",
            system_prompt="""You are a Software Developer Expert. Your role is to:
- Write clean, efficient code
- Debug existing code
- Explain programming concepts
- Follow best practices
Always provide well-commented code with examples.""",
            capabilities=[AgentCapability.CODE, AgentCapability.ANALYSIS],
            tools=["code_interpreter", "web_search"]
        ))
        
        # Data Analyst Agent
        self.register_agent(Agent(
            id="analyst",
            name="Data Analyst",
            description="Analyzes data, creates visualizations, and generates insights",
            system_prompt="""You are a Data Analysis Expert. Your role is to:
- Analyze datasets
- Create visualizations
- Generate statistical insights
- Present data clearly
Use charts and tables to present findings.""",
            capabilities=[AgentCapability.DATA, AgentCapability.CODE, AgentCapability.ANALYSIS],
            tools=["code_interpreter", "document_analysis"]
        ))
        
        # Writer Agent
        self.register_agent(Agent(
            id="writer",
            name="Content Writer",
            description="Helps with writing, editing, and content creation",
            system_prompt="""You are a Professional Writer. Your role is to:
- Write clear, engaging content
- Edit and proofread
- Adapt tone for different audiences
- Create various content types (blogs, emails, reports)
Always maintain high quality and originality.""",
            capabilities=[AgentCapability.WRITING],
            tools=["web_search"]
        ))
        
        # Tutor Agent
        self.register_agent(Agent(
            id="tutor",
            name="AI Tutor",
            description="Educational assistant for learning and explaining concepts",
            system_prompt="""You are a Patient Educational Tutor. Your role is to:
- Explain concepts clearly
- Break down complex topics
- Provide examples
- Test understanding
Be encouraging and adapt to the learner's level.""",
            capabilities=[AgentCapability.RESEARCH, AgentCapability.WRITING],
            tools=["web_search", "code_interpreter"]
        ))
        
        # General Assistant
        self.register_agent(Agent(
            id="assistant",
            name="General Assistant",
            description="General purpose AI assistant for everyday tasks",
            system_prompt="""You are a helpful AI Assistant. Your role is to:
- Answer questions helpfully
- Assist with various tasks
- Provide accurate information
- Be friendly and professional
Always do your best to help the user.""",
            capabilities=[
                AgentCapability.SEARCH, AgentCapability.CODE, 
                AgentCapability.RESEARCH, AgentCapability.WRITING,
                AgentCapability.ANALYSIS
            ],
            tools=["web_search", "code_interpreter", "document_analysis"]
        ))
    
    def register_agent(self, agent: Agent):
        """Register a new agent"""
        self.agents[agent.id] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        return [agent.to_dict() for agent in self.agents.values() if agent.is_active]
    
    async def run_agent(
        self,
        agent_id: str,
        user_input: str,
        context: Dict[str, Any] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Run an agent with user input
        
        Args:
            agent_id: Agent to run
            user_input: User message
            context: Additional context
            session_id: Optional session ID for continuity
            
        Returns:
            Dict with agent response
        """
        agent = self.get_agent(agent_id)
        
        if not agent:
            return {
                "success": False,
                "error": f"Agent '{agent_id}' not found"
            }
        
        logger.info(f"Running agent: {agent.name}")
        
        # Create or resume session
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            history = session.get("history", [])
        else:
            session_id = session_id or str(datetime.now().timestamp())
            history = []
            self.active_sessions[session_id] = {
                "agent_id": agent_id,
                "created_at": datetime.now().isoformat(),
                "history": history
            }
        
        try:
            # Build messages
            messages = [
                {"role": "system", "content": agent.system_prompt}
            ]
            
            # Add context if provided
            if context:
                context_str = json.dumps(context, indent=2)
                messages.append({
                    "role": "system",
                    "content": f"Additional context:\n{context_str}"
                })
            
            # Add conversation history
            messages.extend(history)
            
            # Add current message
            messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            from ai_aggregator import get_ai_aggregator
            aggregator = get_ai_aggregator()
            
            response = await aggregator.generate_response(
                prompt=user_input,
                provider="groq",
                model=agent.model,
                system_prompt=agent.system_prompt,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                messages=messages if len(messages) > 2 else None
            )
            
            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            
            # Keep only last 20 messages
            if len(history) > 40:
                history = history[-40:]
            
            self.active_sessions[session_id]["history"] = history
            
            return {
                "success": True,
                "response": response,
                "agent": agent.to_dict(),
                "session_id": session_id,
                "capabilities_used": [c.value for c in agent.capabilities]
            }
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id
            }
    
    async def run_agent_with_tools(
        self,
        agent_id: str,
        user_input: str,
        tools_manager = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Run agent with tool execution capability
        
        Args:
            agent_id: Agent to run
            user_input: User message
            tools_manager: Tools manager instance
            session_id: Optional session ID
        """
        agent = self.get_agent(agent_id)
        
        if not agent:
            return {"success": False, "error": f"Agent not found: {agent_id}"}
        
        # First, let AI decide if tools are needed
        tools_prompt = f"""User request: {user_input}

Available tools: {', '.join(agent.tools)}

Should any tools be used? If yes, specify which tool and what input.
Respond in format:
TOOL: tool_name
INPUT: what to search/execute

If no tools needed, respond:
TOOL: none"""
        
        try:
            from ai_aggregator import get_ai_aggregator
            aggregator = get_ai_aggregator()
            
            tool_decision = await aggregator.generate_response(
                prompt=tools_prompt,
                provider="groq",
                model="llama-3.1-70b-versatile"
            )
            
            # Execute tool if needed
            tool_result = None
            if "TOOL: none" not in tool_decision.upper():
                # Parse tool decision
                tool_name = None
                tool_input = None
                
                for line in tool_decision.split("\n"):
                    if line.startswith("TOOL:"):
                        tool_name = line.split(":", 1)[1].strip()
                    elif line.startswith("INPUT:"):
                        tool_input = line.split(":", 1)[1].strip()
                
                if tool_name and tool_name != "none" and tools_manager:
                    # Execute tool
                    if tool_name == "web_search":
                        from web_search_with_citations import search_with_citations
                        tool_result = await search_with_citations(tool_input or user_input)
                    elif tool_name == "code_interpreter":
                        from code_interpreter import execute_code
                        tool_result = await execute_code(tool_input)
                    elif tool_name == "document_analysis":
                        from document_analyzer import analyze_document
                        tool_result = await analyze_document(tool_input)
            
            # Build final prompt with tool results
            final_prompt = user_input
            if tool_result:
                final_prompt += f"\n\nAdditional information from tools:\n{json.dumps(tool_result, indent=2)}"
            
            # Run agent
            return await self.run_agent(agent_id, final_prompt, session_id=session_id)
            
        except Exception as e:
            logger.error(f"Agent with tools error: {e}")
            return await self.run_agent(agent_id, user_input, session_id=session_id)
    
    def create_custom_agent(
        self,
        name: str,
        description: str,
        system_prompt: str,
        capabilities: List[str],
        tools: List[str] = None,
        model: str = "llama-3.1-70b-versatile"
    ) -> Dict[str, Any]:
        """Create a custom agent"""
        
        agent_id = name.lower().replace(" ", "_")
        
        # Convert capability strings to enum
        capability_enums = []
        for cap in capabilities:
            try:
                capability_enums.append(AgentCapability(cap))
            except:
                pass
        
        agent = Agent(
            id=agent_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            capabilities=capability_enums,
            tools=tools or [],
            model=model
        )
        
        self.register_agent(agent)
        
        return {
            "success": True,
            "agent": agent.to_dict()
        }
    
    def end_session(self, session_id: str):
        """End an agent session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return {"success": True, "message": "Session ended"}
        return {"success": False, "error": "Session not found"}
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details"""
        return self.active_sessions.get(session_id)


# Singleton instance
_agents_framework: Optional[AIAgentsFramework] = None


def get_agents_framework() -> AIAgentsFramework:
    """Get or create agents framework singleton"""
    global _agents_framework
    if _agents_framework is None:
        _agents_framework = AIAgentsFramework()
    return _agents_framework


async def run_agent(
    agent_id: str,
    user_input: str,
    session_id: str = None
) -> Dict[str, Any]:
    """Convenience function to run an agent"""
    framework = get_agents_framework()
    return await framework.run_agent(agent_id, user_input, session_id=session_id)


def list_agents() -> List[Dict[str, Any]]:
    """Convenience function to list agents"""
    framework = get_agents_framework()
    return framework.list_agents()


def create_agent(
    name: str,
    description: str,
    system_prompt: str,
    capabilities: List[str],
    tools: List[str] = None
) -> Dict[str, Any]:
    """Convenience function to create an agent"""
    framework = get_agents_framework()
    return framework.create_custom_agent(name, description, system_prompt, capabilities, tools)
