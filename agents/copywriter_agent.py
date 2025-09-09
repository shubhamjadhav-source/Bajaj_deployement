from typing import Dict, Any, List
import json
from .base_agent import BaseDynamicAgent

class DynamicCopywriterAgent(BaseDynamicAgent):
    def __init__(self, audit_logger):
        super().__init__("copywriter", audit_logger)
    
    def _generate_dynamic_user_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Generate copywriter-specific user prompt"""
        
        # Extract key information
        audience = input_data.get('audience', 'general audience')
        channel = input_data.get('channel', 'email')
        tone = input_data.get('tone', 'professional')
        placeholders = input_data.get('placeholders', {})
        num_messages = input_data.get('num_messages', 5)
        
        # Build dynamic prompt based on scenario
        prompt_parts = [
            f"SCENARIO: {scenario}",
            f"TASK: Generate {num_messages} unique messages for {audience} via {channel}",
            f"TONE: {tone}",
            "",
            "SCENARIO-SPECIFIC REQUIREMENTS:",
        ]
        
        # Add scenario-specific requirements
        if scenario == "insurance_renewal":
            prompt_parts.extend([
                "- Emphasize policy benefits and protection",
                "- Create urgency around renewal deadline",
                "- Build trust and reliability",
                "- Include clear next steps"
            ])
        elif scenario == "healthcare_reminder":
            prompt_parts.extend([
                "- Focus on health importance",
                "- Be supportive and caring",
                "- Make scheduling convenient",
                "- Respect patient privacy"
            ])
        elif scenario == "ecommerce_promotion":
            prompt_parts.extend([
                "- Highlight value and savings",
                "- Create urgency with limited time",
                "- Showcase product benefits",
                "- Include clear call-to-action"
            ])
        
        # Add placeholders information
        if placeholders:
            prompt_parts.extend([
                "",
                "AVAILABLE PLACEHOLDERS:",
                json.dumps(placeholders, indent=2)
            ])
        
        # Add adaptation-specific instructions
        adaptation_instructions = adaptations.get('adaptation_instructions', '')
        if adaptation_instructions:
            prompt_parts.extend([
                "",
                "ADAPTATION INSTRUCTIONS:",
                adaptation_instructions
            ])
        
        prompt_parts.extend([
            "",
            "IMPORTANT: Return ONLY a valid JSON array of messages in this exact format:",
            '[{"message_id": 1, "content": "message text with {placeholders}", "features": ["feature1", "feature2"], "channel_optimized": true, "scenario_alignment": "explanation"}]'
        ])
        
        return "\n".join(prompt_parts)
    
    def _process_llm_response(self, response_content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Process copywriter LLM response"""
        try:
            # Parse JSON response
            messages = json.loads(response_content.strip())
            
            if not isinstance(messages, list):
                raise ValueError("Response is not a list of messages")
            
            # Validate and enhance messages
            processed_messages = []
            for i, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    msg = {"message_id": i+1, "content": str(msg), "features": []}
                
                # Ensure required fields
                msg.setdefault("message_id", i+1)
                msg.setdefault("features", [])
                msg.setdefault("scenario_alignment", "Generated for " + scenario)
                
                # Add dynamic enhancements
                msg["word_count"] = len(msg.get("content", "").split())
                msg["character_count"] = len(msg.get("content", ""))
                msg["placeholder_count"] = len([p for p in input_data.get('placeholders', {}).keys() 
                                              if f"{{{p}}}" in msg.get("content", "")])
                
                processed_messages.append(msg)
            
            return {
                "messages": processed_messages,
                "total_generated": len(processed_messages),
                "scenario": scenario,
                "generation_summary": {
                    "avg_word_count": sum(m["word_count"] for m in processed_messages) / len(processed_messages) if processed_messages else 0,
                    "avg_character_count": sum(m["character_count"] for m in processed_messages) / len(processed_messages) if processed_messages else 0,
                    "placeholder_usage": sum(m["placeholder_count"] for m in processed_messages)
                }
            }
            
        except json.JSONDecodeError:
            # Fallback parsing for non-JSON responses
            return self._fallback_message_parsing(response_content, input_data, scenario)
        except Exception as e:
            return {
                "messages": [],
                "error": f"Failed to process messages: {str(e)}",
                "raw_response": response_content[:500] + "..." if len(response_content) > 500 else response_content
            }
    
    def _fallback_message_parsing(self, content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Fallback parsing when JSON fails"""
        lines = content.strip().split('\n')
        messages = []
        current_message = ""
        message_id = 1
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('['):
                if any(keyword in line.lower() for keyword in ['message', 'option', str(message_id)]):
                    if current_message:
                        messages.append({
                            "message_id": len(messages) + 1,
                            "content": current_message.strip(),
                            "features": ["fallback_parsed"],
                            "scenario_alignment": f"Fallback parsed for {scenario}"
                        })
                        current_message = ""
                    message_id += 1
                else:
                    current_message += line + " "
        
        # Add last message
        if current_message:
            messages.append({
                "message_id": len(messages) + 1,
                "content": current_message.strip(),
                "features": ["fallback_parsed"],
                "scenario_alignment": f"Fallback parsed for {scenario}"
            })
        
        # Ensure minimum messages
        while len(messages) < 3:
            messages.append({
                "message_id": len(messages) + 1,
                "content": f"Generated message {len(messages) + 1} for {scenario}",
                "features": ["auto_generated"],
                "scenario_alignment": f"Auto-generated for {scenario}"
            })
        
        return {
            "messages": messages,
            "total_generated": len(messages),
            "scenario": scenario,
            "parsing_method": "fallback",
            "generation_summary": {
                "note": "Used fallback parsing due to non-JSON response"
            }
        }
