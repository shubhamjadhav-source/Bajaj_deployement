from typing import Dict, Any, List
import json
import re
from .base_agent import BaseDynamicAgent

class DynamicComplianceAgent(BaseDynamicAgent):
    def __init__(self, audit_logger):
        super().__init__("compliance", audit_logger)
        
        # Dynamic compliance rules that adapt to scenarios
        self.base_compliance_rules = {
            "financial_services": [
                {"pattern": r"guaranteed|promise|100%", "severity": "HIGH", "rule": "No absolute guarantees"},
                {"pattern": r"click here|act now|urgent", "severity": "MEDIUM", "rule": "Avoid high-pressure language"},
                {"pattern": r"free money|instant cash", "severity": "HIGH", "rule": "No misleading financial claims"}
            ],
            "healthcare": [
                {"pattern": r"cure|guaranteed healing|miracle", "severity": "HIGH", "rule": "No medical claims"},
                {"pattern": r"personal health info", "severity": "HIGH", "rule": "HIPAA compliance required"},
                {"pattern": r"diagnose|treatment guarantee", "severity": "HIGH", "rule": "No medical advice"}
            ],
            "general": [
                {"pattern": r"winner|you've won|congratulations", "severity": "MEDIUM", "rule": "Avoid spam-like language"},
                {"pattern": r"limited time|expires soon|hurry", "severity": "LOW", "rule": "Moderate urgency language"}
            ]
        }
    
    def _generate_dynamic_user_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Generate compliance-specific user prompt"""
        
        messages = input_data.get('previous_results', {}).get('copywriter', {}).get('data', {}).get('messages', [])
        if not messages:
            messages = input_data.get('messages', [])
        
        channel = input_data.get('channel', 'email')
        jurisdiction = input_data.get('jurisdiction', 'US')
        industry = input_data.get('industry', 'general')
        
        # Get scenario-specific compliance focus
        compliance_focus = self._get_compliance_focus(scenario)
        
        prompt_parts = [
            f"SCENARIO: {scenario}",
            f"TASK: Analyze {len(messages)} messages for compliance violations",
            f"CHANNEL: {channel}",
            f"JURISDICTION: {jurisdiction}",
            f"INDUSTRY: {industry}",
            "",
            "COMPLIANCE FOCUS AREAS:",
        ]
        
        for focus_area in compliance_focus:
            prompt_parts.append(f"- {focus_area}")
        
        prompt_parts.extend([
            "",
            "MESSAGES TO ANALYZE:",
            json.dumps(messages, indent=2),
            "",
            "ANALYSIS REQUIREMENTS:",
            "1. Identify specific regulatory violations",
            "2. Assess risk level for each violation",
            "3. Provide improvement suggestions",
            "4. Calculate compliance score (0-100)",
            "5. Consider scenario-specific regulations",
            "",
            "RETURN FORMAT: Valid JSON only:",
            '{"overall_compliance": 85, "total_messages_analyzed": 5, "message_analyses": [{"message_id": 1, "compliance_score": 90, "violations": [{"type": "rule_type", "severity": "HIGH", "description": "violation description", "suggestion": "improvement suggestion"}], "risk_level": "LOW"}], "scenario_risks": ["risk1"], "recommendations": ["rec1"]}'
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_compliance_focus(self, scenario: str) -> List[str]:
        """Get compliance focus areas based on scenario"""
        focus_map = {
            "insurance_renewal": [
                "TCPA compliance for automated messages",
                "Clear opt-out mechanisms",
                "Accurate policy information",
                "No misleading claims about coverage"
            ],
            "healthcare_reminder": [
                "HIPAA privacy protection",
                "No medical advice or diagnosis",
                "Secure communication requirements",
                "Patient consent verification"
            ],
            "loan_reminder": [
                "FDCPA debt collection rules",
                "Clear creditor identification",
                "No harassment or threats",
                "Accurate payment information"
            ],
            "ecommerce_promotion": [
                "CAN-SPAM compliance",
                "Clear unsubscribe options",
                "Truthful advertising claims",
                "GDPR privacy requirements"
            ]
        }
        
        return focus_map.get(scenario, [
            "General consumer protection",
            "Anti-spam regulations",
            "Clear communication requirements",
            "Opt-out mechanisms"
        ])
    
    def _process_llm_response(self, response_content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Process compliance LLM response"""
        try:
            # Parse JSON response
            compliance_data = json.loads(response_content.strip())
            
            # Validate and enhance compliance analysis
            if not isinstance(compliance_data, dict):
                raise ValueError("Invalid compliance response format")
            
            # Apply additional rule-based checks
            enhanced_analysis = self._apply_rule_based_checks(compliance_data, input_data, scenario)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(enhanced_analysis)
            
            return {
                **enhanced_analysis,
                "risk_metrics": risk_metrics,
                "scenario": scenario,
                "analysis_timestamp": input_data.get('workflow_context', {}).get('start_time', '').isoformat() if input_data.get('workflow_context', {}).get('start_time') else '',
                "compliance_methodology": "LLM + Rule-based hybrid analysis"
            }
            
        except json.JSONDecodeError:
            return self._fallback_compliance_analysis(response_content, input_data, scenario)
        except Exception as e:
            return {
                "overall_compliance": 50,
                "error": f"Failed to process compliance analysis: {str(e)}",
                "scenario": scenario,
                "fallback_applied": True
            }
    
    def _apply_rule_based_checks(self, llm_analysis: Dict[str, Any], input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Apply additional rule-based compliance checks"""
        
        # Determine rule set based on scenario
        if "insurance" in scenario or "financial" in scenario:
            rule_set = "financial_services"
        elif "health" in scenario:
            rule_set = "healthcare"
        else:
            rule_set = "general"
        
        rules = self.base_compliance_rules.get(rule_set, self.base_compliance_rules["general"])
        
        # Get messages to check
        messages = input_data.get('previous_results', {}).get('copywriter', {}).get('data', {}).get('messages', [])
        if not messages:
            messages = input_data.get('messages', [])
        
        # Apply rule-based checks
        enhanced_analyses = []
        for message_analysis in llm_analysis.get('message_analyses', []):
            message_id = message_analysis.get('message_id')
            message_content = ""
            
            # Find corresponding message content
            for msg in messages:
                if msg.get('message_id') == message_id:
                    message_content = msg.get('content', '')
                    break
            
            # Apply rules
            rule_violations = []
            for rule in rules:
                if re.search(rule['pattern'], message_content, re.IGNORECASE):
                    rule_violations.append({
                        "type": "rule_based_check",
                        "severity": rule['severity'],
                        "description": rule['rule'],
                        "matched_pattern": rule['pattern'],
                        "suggestion": f"Revise content to comply with {rule['rule']}"
                    })
            
            # Merge with LLM violations
            existing_violations = message_analysis.get('violations', [])
            all_violations = existing_violations + rule_violations
            
            # Recalculate compliance score
            high_violations = len([v for v in all_violations if v.get('severity') == 'HIGH'])
            medium_violations = len([v for v in all_violations if v.get('severity') == 'MEDIUM'])
            low_violations = len([v for v in all_violations if v.get('severity') == 'LOW'])
            
            compliance_score = max(0, 100 - (high_violations * 25) - (medium_violations * 10) - (low_violations * 5))
            
            enhanced_analysis = {
                **message_analysis,
                "violations": all_violations,
                "compliance_score": compliance_score,
                "rule_based_checks_applied": len(rule_violations),
                "risk_level": "HIGH" if high_violations > 0 else ("MEDIUM" if medium_violations > 0 else "LOW")
            }
            
            enhanced_analyses.append(enhanced_analysis)
        
        # Update overall compliance
        if enhanced_analyses:
            overall_compliance = sum(a['compliance_score'] for a in enhanced_analyses) / len(enhanced_analyses)
        else:
            overall_compliance = llm_analysis.get('overall_compliance', 50)
        
        return {
            **llm_analysis,
            "message_analyses": enhanced_analyses,
            "overall_compliance": round(overall_compliance, 1),
            "rule_set_applied": rule_set,
            "total_rule_violations": sum(a['rule_based_checks_applied'] for a in enhanced_analyses)
        }
    
    def _calculate_risk_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        message_analyses = analysis.get('message_analyses', [])
        
        if not message_analyses:
            return {"overall_risk": "UNKNOWN"}
        
        high_risk_messages = len([m for m in message_analyses if m.get('risk_level') == 'HIGH'])
        medium_risk_messages = len([m for m in message_analyses if m.get('risk_level') == 'MEDIUM'])
        low_risk_messages = len([m for m in message_analyses if m.get('risk_level') == 'LOW'])
        
        total_violations = sum(len(m.get('violations', [])) for m in message_analyses)
        avg_compliance_score = analysis.get('overall_compliance', 0)
        
        # Determine overall risk
        if high_risk_messages > 0 or avg_compliance_score < 60:
            overall_risk = "HIGH"
        elif medium_risk_messages > 0 or avg_compliance_score < 80:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"
        
        return {
            "overall_risk": overall_risk,
            "high_risk_messages": high_risk_messages,
            "medium_risk_messages": medium_risk_messages,
            "low_risk_messages": low_risk_messages,
            "total_violations": total_violations,
            "avg_compliance_score": avg_compliance_score,
            "deployment_recommendation": "APPROVED" if overall_risk == "LOW" else ("REVIEW_REQUIRED" if overall_risk == "MEDIUM" else "NOT_APPROVED")
        }
    
    def _fallback_compliance_analysis(self, content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Fallback compliance analysis when JSON parsing fails"""
        
        # Basic rule-based analysis as fallback
        messages = input_data.get('previous_results', {}).get('copywriter', {}).get('data', {}).get('messages', [])
        if not messages:
            messages = input_data.get('messages', [])
        
        fallback_analyses = []
        
        for i, message in enumerate(messages):
            content = message.get('content', '')
            violations = []
            
            # Basic compliance checks
            if re.search(r'guaranteed|promise|100%', content, re.IGNORECASE):
                violations.append({
                    "type": "absolute_claims",
                    "severity": "HIGH",
                    "description": "Contains absolute guarantees",
                    "suggestion": "Use qualified language like 'may' or 'potential'"
                })
            
            if re.search(r'click here|act now|urgent', content, re.IGNORECASE):
                violations.append({
                    "type": "high_pressure",
                    "severity": "MEDIUM", 
                    "description": "High-pressure language detected",
                    "suggestion": "Use gentler call-to-action language"
                })
            
            compliance_score = max(0, 100 - (len([v for v in violations if v['severity'] == 'HIGH']) * 30) - 
                                         (len([v for v in violations if v['severity'] == 'MEDIUM']) * 15))
            
            fallback_analyses.append({
                "message_id": message.get('message_id', i+1),
                "compliance_score": compliance_score,
                "violations": violations,
                "risk_level": "HIGH" if any(v['severity'] == 'HIGH' for v in violations) else ("MEDIUM" if violations else "LOW")
            })
        
        overall_compliance = sum(a['compliance_score'] for a in fallback_analyses) / len(fallback_analyses) if fallback_analyses else 0
        
        return {
            "overall_compliance": round(overall_compliance, 1),
            "message_analyses": fallback_analyses,
            "scenario": scenario,
            "analysis_method": "fallback_rule_based",
            "note": "Used fallback analysis due to LLM parsing issues"
        }
