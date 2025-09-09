from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

class SimpleWorkflowEngine:
    def __init__(self, agents: Dict[str, Any], audit_logger):
        self.agents = agents
        self.audit_logger = audit_logger
        
    async def execute_dynamic_workflow(
        self, 
        scenario: str, 
        input_data: Dict[str, Any],
        agent_sequence: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute workflow with dynamic scenario adaptation"""
        
        # Default sequence if none provided
        sequence = agent_sequence or ["copywriter", "compliance", "feedback", "decision"]
        
        results = {}
        workflow_context = {
            "scenario": scenario,
            "start_time": datetime.now(),
            "agent_results": {}
        }
        
        for agent_name in sequence:
            if agent_name not in self.agents:
                results[agent_name] = {
                    "success": False,
                    "error": f"Agent {agent_name} not available"
                }
                continue
            
            try:
                agent = self.agents[agent_name]
                
                # Prepare input with context
                agent_input = {
                    **input_data,
                    "workflow_context": workflow_context,
                    "previous_results": workflow_context["agent_results"]
                }
                
                # Execute agent
                response = await agent.process_dynamic(agent_input, scenario)
                results[agent_name] = response
                
                # Update workflow context
                workflow_context["agent_results"][agent_name] = response
                
                # If agent failed critically, stop workflow
                if not response.get("success", False) and response.get("critical", False):
                    break
                    
            except Exception as e:
                results[agent_name] = {
                    "success": False,
                    "error": str(e),
                    "agent_name": agent_name
                }
        
        # Add workflow summary
        results["workflow_summary"] = {
            "scenario": scenario,
            "total_agents": len(sequence),
            "successful_agents": sum(1 for r in results.values() if r.get("success", False)),
            "total_processing_time": (datetime.now() - workflow_context["start_time"]).total_seconds(),
            "sequence_used": sequence
        }
        
        return results
