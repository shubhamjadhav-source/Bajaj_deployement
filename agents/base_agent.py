from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from utils.llm_client import EnhancedLLMClient
from utils.audit_logger import DynamicAuditLogger
from config.agent_configs import AGENT_CONFIGS
from config.scenarios import SCENARIOS
import json
from datetime import datetime
import asyncio

class BaseDynamicAgent(ABC):
    def __init__(self, agent_key: str, audit_logger: DynamicAuditLogger):
        self.agent_key = agent_key
        self.config = AGENT_CONFIGS[agent_key]
        self.llm_client = EnhancedLLMClient()
        self.audit_logger = audit_logger
        self.adaptation_cache = {}
        
    async def process_dynamic(self, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Main dynamic processing method"""
        start_time = datetime.now()
        
        try:
            # Get scenario-specific adaptations
            adaptations = self._get_scenario_adaptations(scenario)
            
            # Generate dynamic prompts
            system_prompt = self._generate_dynamic_system_prompt(input_data, scenario, adaptations)
            user_prompt = self._generate_dynamic_user_prompt(input_data, scenario, adaptations)
            
            # Execute with LLM
            llm_response = await self.llm_client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=adaptations.get("temperature", 0.7),
                max_tokens=adaptations.get("max_tokens", 2000),
                response_format="json"
            )
            
            if not llm_response.success:
                raise Exception(f"LLM call failed: {llm_response.error}")
            
            # Process response
            processed_data = self._process_llm_response(llm_response.content, input_data, scenario)
            
            # Calculate performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "agent_name": self.config.name,
                "scenario": scenario,
                "data": processed_data,
                "adaptations_used": adaptations,
                "performance": {
                    "processing_time": processing_time,
                    "tokens_used": llm_response.usage["total_tokens"],
                    "model_used": llm_response.model_used
                },
                "metadata": {
                    "timestamp": start_time.isoformat(),
                    "agent_key": self.agent_key
                }
            }
            
            # Log execution
            self.audit_logger.log_dynamic_execution(
                agent_name=self.config.name,
                scenario=scenario,
                action="dynamic_processing",
                input_data=input_data,
                output_data=result,
                adaptations=adaptations,
                performance=result["performance"],
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            error_result = {
                "success": False,
                "agent_name": self.config.name,
                "scenario": scenario,
                "error": str(e),
                "performance": {
                    "processing_time": processing_time,
                    "tokens_used": 0
                }
            }
            
            # Log error
            self.audit_logger.log_dynamic_execution(
                agent_name=self.config.name,
                scenario=scenario,
                action="dynamic_processing",
                input_data=input_data,
                output_data=error_result,
                success=False
            )
            
            return error_result
    
    def _get_scenario_adaptations(self, scenario: str) -> Dict[str, Any]:
        """Get scenario-specific adaptations for this agent"""
        scenario_config = SCENARIOS.get(scenario, {})
        agent_adaptations = scenario_config.get("agent_adaptations", {}).get(self.agent_key, {})
        
        # Merge with base config adaptations
        base_adaptations = self.config.dynamic_adaptations
        
        return {**base_adaptations, **agent_adaptations}
    
    def _generate_dynamic_system_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Generate dynamic system prompt based on scenario and adaptations"""
        template = self.config.system_prompt_template
        
        # Prepare template variables
        template_vars = {
            "scenario_context": scenario,
            "adaptations": adaptations,
            **input_data,
            **adaptations
        }
        
        # Add scenario-specific context
        if scenario in SCENARIOS:
            scenario_info = SCENARIOS[scenario]
            template_vars["scenario_name"] = scenario_info["name"]
            template_vars["scenario_description"] = scenario_info.get("description", "")
        
        try:
            return template.format(**template_vars)
        except KeyError as e:
            # Fallback for missing template variables
            return template.replace(f"{{{e.args[0]}}}", str(template_vars.get(e.args[0], "N/A")))
    
    def _generate_dynamic_user_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Generate dynamic user prompt"""
        # This can be overridden by specific agents
        return self._build_default_user_prompt(input_data, scenario, adaptations)
    
    def _build_default_user_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Build default user prompt"""
        prompt_parts = [
            f"SCENARIO: {scenario}",
            f"INPUT DATA: {json.dumps(input_data, indent=2)}",
            f"ADAPTATIONS: {json.dumps(adaptations, indent=2)}",
            "",
            "Please process this request according to your role and the provided scenario context."
        ]
        
        return "\n".join(prompt_parts)
    
    @abstractmethod
    def _process_llm_response(self, response_content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Process the LLM response - must be implemented by each agent"""
        pass
