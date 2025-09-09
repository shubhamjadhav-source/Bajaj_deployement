from typing import Dict, Any, List
import json
from .base_agent import BaseDynamicAgent

class DynamicFeedbackAgent(BaseDynamicAgent):
    def __init__(self, audit_logger):
        super().__init__("feedback", audit_logger)
        
        # Demographic behavior models
        self.demographic_models = {
            "age_40_plus": {
                "communication_preferences": "clear, formal, trustworthy",
                "decision_factors": ["security", "reliability", "value"],
                "response_patterns": "methodical, risk-averse",
                "technology_comfort": "moderate"
            },
            "millennials": {
                "communication_preferences": "authentic, mobile-first, interactive",
                "decision_factors": ["convenience", "social_proof", "innovation"],
                "response_patterns": "quick, research-oriented",
                "technology_comfort": "high"
            },
            "business_customers": {
                "communication_preferences": "professional, data-driven, efficient",
                "decision_factors": ["ROI", "efficiency", "scalability"],
                "response_patterns": "analytical, time-conscious",
                "technology_comfort": "high"
            },
            "healthcare_patients": {
                "communication_preferences": "caring, private, informative",
                "decision_factors": ["trust", "convenience", "health_outcomes"],
                "response_patterns": "cautious, value-seeking",
                "technology_comfort": "varied"
            }
        }
    
    def _generate_dynamic_user_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Generate feedback-specific user prompt"""
        
        # Get messages from previous results
        messages = input_data.get('previous_results', {}).get('copywriter', {}).get('data', {}).get('messages', [])
        if not messages:
            messages = input_data.get('messages', [])
        
        # Determine demographic model
        audience = input_data.get('audience', 'general customers')
        age_group = input_data.get('age_group', 'all ages')
        demographic_key = self._map_to_demographic_model(audience, age_group, scenario)
        demographic_profile = self.demographic_models.get(demographic_key, self.demographic_models["millennials"])
        
        # Get scenario-specific context
        scenario_context = self._get_scenario_feedback_context(scenario)
        
        prompt_parts = [
            f"SCENARIO: {scenario}",
            f"TASK: Simulate realistic customer feedback for {len(messages)} messages",
            "",
            "CUSTOMER DEMOGRAPHIC PROFILE:",
            f"- Communication Preferences: {demographic_profile['communication_preferences']}",
            f"- Key Decision Factors: {', '.join(demographic_profile['decision_factors'])}",
            f"- Response Patterns: {demographic_profile['response_patterns']}",
            f"- Technology Comfort: {demographic_profile['technology_comfort']}",
            "",
            "SCENARIO CONTEXT:",
        ]
        
        for context_item in scenario_context:
            prompt_parts.append(f"- {context_item}")
        
        prompt_parts.extend([
            "",
            "MESSAGES TO EVALUATE:",
            json.dumps(messages, indent=2),
            "",
            "FEEDBACK SIMULATION REQUIREMENTS:",
            "1. Provide realistic sentiment scores (1-10)",
            "2. Assess clarity and comprehension (1-10)",
            "3. Rate likelihood to take action (1-10)",
            "4. Generate authentic customer comments",
            "5. Consider demographic and scenario factors",
            "6. Provide behavioral insights",
            "",
            "RETURN FORMAT: Valid JSON only:",
            '{"feedback_summary": {"avg_sentiment": 7.2, "predicted_response_rate": 0.15, "key_insights": ["insight1"]}, "message_feedback": [{"message_id": 1, "sentiment_score": 8, "clarity_score": 7, "action_likelihood": 6, "customer_comments": ["comment1"], "demographic_appeal": "high", "behavioral_prediction": "likely to engage"}]}'
        ])
        
        return "\n".join(prompt_parts)
    
    def _map_to_demographic_model(self, audience: str, age_group: str, scenario: str) -> str:
        """Map audience and age to demographic model"""
        if "40" in age_group or "above 40" in age_group.lower():
            return "age_40_plus"
        elif "business" in audience.lower() or "corporate" in audience.lower():
            return "business_customers"
        elif "health" in scenario or "patient" in audience.lower():
            return "healthcare_patients"
        else:
            return "millennials"
    
    def _get_scenario_feedback_context(self, scenario: str) -> List[str]:
        """Get scenario-specific feedback context"""
        context_map = {
            "insurance_renewal": [
                "Customers are evaluating policy value and trust in insurer",
                "Renewal decisions are often routine but price-sensitive",
                "Clear communication about benefits is crucial",
                "Timing of communication affects response rates"
            ],
            "healthcare_reminder": [
                "Patients prioritize health but value convenience",
                "Trust in healthcare provider is paramount",
                "Privacy concerns affect communication preferences",
                "Health anxiety may influence response patterns"
            ],
            "loan_reminder": [
                "Customers may be experiencing financial stress",
                "Clear, respectful communication is essential",
                "Payment convenience significantly affects response",
                "Trust and transparency build cooperation"
            ],
            "ecommerce_promotion": [
                "Customers are deal-conscious and comparison shop",
                "Mobile optimization affects engagement",
                "Social proof and urgency drive action",
                "Personalization increases relevance"
            ]
        }
        
        return context_map.get(scenario, [
            "General customer communication scenario",
            "Focus on clear value proposition",
            "Consider customer convenience",
            "Build trust through transparency"
        ])
    
    def _process_llm_response(self, response_content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Process feedback LLM response"""
        try:
            # Parse JSON response
            feedback_data = json.loads(response_content.strip())
            
            if not isinstance(feedback_data, dict):
                raise ValueError("Invalid feedback response format")
            
            # Enhance with additional analytics
            enhanced_feedback = self._enhance_feedback_analysis(feedback_data, input_data, scenario)
            
            # Generate behavioral insights
            behavioral_insights = self._generate_behavioral_insights(enhanced_feedback, scenario)
            
            return {
                **enhanced_feedback,
                "behavioral_insights": behavioral_insights,
                "scenario": scenario,
                "simulation_methodology": "LLM-based demographic modeling",
                "confidence_level": self._calculate_feedback_confidence(enhanced_feedback)
            }
            
        except json.JSONDecodeError:
            return self._fallback_feedback_analysis(response_content, input_data, scenario)
        except Exception as e:
            return {
                "feedback_summary": {"avg_sentiment": 5.0, "predicted_response_rate": 0.05},
                "message_feedback": [],
                "error": f"Failed to process feedback analysis: {str(e)}",
                "scenario": scenario
            }
    
    def _enhance_feedback_analysis(self, feedback_data: Dict[str, Any], input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Enhance feedback analysis with additional metrics"""
        
        message_feedback = feedback_data.get('message_feedback', [])
        
        if not message_feedback:
            return feedback_data
        
        # Calculate additional metrics
        sentiment_scores = [mf.get('sentiment_score', 5) for mf in message_feedback]
        clarity_scores = [mf.get('clarity_score', 5) for mf in message_feedback]
        action_scores = [mf.get('action_likelihood', 5) for mf in message_feedback]
        
        # Enhanced summary
        enhanced_summary = {
            **feedback_data.get('feedback_summary', {}),
            "avg_sentiment": sum(sentiment_scores) / len(sentiment_scores),
            "avg_clarity": sum(clarity_scores) / len(clarity_scores),
            "avg_action_likelihood": sum(action_scores) / len(action_scores),
            "sentiment_range": max(sentiment_scores) - min(sentiment_scores),
            "top_performing_message": max(message_feedback, key=lambda x: x.get('sentiment_score', 0)).get('message_id') if message_feedback else None
        }
        
        # Add scenario-specific metrics
        if scenario == "insurance_renewal":
            enhanced_summary["predicted_renewal_rate"] = enhanced_summary["avg_action_likelihood"] / 10 * 0.8  # Conservative estimate
        elif scenario == "healthcare_reminder":
            enhanced_summary["predicted_appointment_rate"] = enhanced_summary["avg_action_likelihood"] / 10 * 0.7
        elif scenario == "ecommerce_promotion":
            enhanced_summary["predicted_conversion_rate"] = enhanced_summary["avg_action_likelihood"] / 10 * 0.15
        
        return {
            **feedback_data,
            "feedback_summary": enhanced_summary,
            "analysis_depth": "enhanced"
        }
    
    def _generate_behavioral_insights(self, feedback_data: Dict[str, Any], scenario: str) -> List[str]:
        """Generate behavioral insights from feedback"""
        insights = []
        
        summary = feedback_data.get('feedback_summary', {})
        message_feedback = feedback_data.get('message_feedback', [])
        
        avg_sentiment = summary.get('avg_sentiment', 5)
        avg_clarity = summary.get('avg_clarity', 5)
        avg_action = summary.get('avg_action_likelihood', 5)
        
        # Sentiment insights
        if avg_sentiment >= 8:
            insights.append("High emotional resonance - messages strongly connect with audience")
        elif avg_sentiment <= 4:
            insights.append("Low emotional appeal - consider more engaging or relevant messaging")
        
        # Clarity insights
        if avg_clarity <= 5:
            insights.append("Clarity concerns - simplify language and structure")
        elif avg_clarity >= 8:
            insights.append("Excellent clarity - messages are easy to understand")
        
        # Action insights
        if avg_action >= 7:
            insights.append("Strong call-to-action effectiveness - high motivation to act")
        elif avg_action <= 4:
            insights.append("Weak action motivation - strengthen value proposition or urgency")
        
        # Scenario-specific insights
        if scenario == "insurance_renewal":
            if avg_sentiment > avg_action:
                insights.append("Good emotional connection but weak action drivers - add clearer next steps")
        elif scenario == "healthcare_reminder":
            if avg_clarity > avg_action:
                insights.append("Clear communication but low urgency - emphasize health importance")
        
        # Performance variance insights
        if message_feedback:
            scores = [mf.get('sentiment_score', 5) for mf in message_feedback]
            if max(scores) - min(scores) > 3:
                insights.append("High message performance variance - focus on top-performing elements")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _calculate_feedback_confidence(self, feedback_data: Dict[str, Any]) -> float:
        """Calculate confidence level in feedback simulation"""
        message_feedback = feedback_data.get('message_feedback', [])
        
        if not message_feedback:
            return 0.3
        
        # Factors affecting confidence
        sample_size_factor = min(len(message_feedback) / 5, 1.0)  # More messages = higher confidence
        consistency_factor = 1.0 - (feedback_data.get('feedback_summary', {}).get('sentiment_range', 0) / 10)  # Lower variance = higher confidence
        completeness_factor = 1.0 if all('customer_comments' in mf for mf in message_feedback) else 0.8
        
        confidence = (sample_size_factor + consistency_factor + completeness_factor) / 3
        return round(confidence, 2)
    
    def _fallback_feedback_analysis(self, content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Fallback feedback analysis when JSON parsing fails"""
        
        messages = input_data.get('previous_results', {}).get('copywriter', {}).get('data', {}).get('messages', [])
        if not messages:
            messages = input_data.get('messages', [])
        
        # Generate basic feedback for each message
        fallback_feedback = []
        
        for i, message in enumerate(messages):
            # Basic scoring based on message characteristics
            content = message.get('content', '')
            word_count = len(content.split())
            
            # Simple heuristics
            sentiment = 7 if word_count > 10 and word_count < 50 else 5
            clarity = 8 if word_count < 30 else 6
            action = 6 if any(word in content.lower() for word in ['please', 'now', 'today']) else 4
            
            fallback_feedback.append({
                "message_id": message.get('message_id', i+1),
                "sentiment_score": sentiment,
                "clarity_score": clarity,
                "action_likelihood": action,
                "customer_comments": ["Fallback analysis - detailed feedback unavailable"],
                "demographic_appeal": "moderate",
                "behavioral_prediction": "standard response expected"
            })
        
        avg_sentiment = sum(f['sentiment_score'] for f in fallback_feedback) / len(fallback_feedback) if fallback_feedback else 5
        
        return {
            "feedback_summary": {
                "avg_sentiment": avg_sentiment,
                "predicted_response_rate": 0.08,  # Conservative estimate
                "key_insights": ["Fallback analysis applied - limited insights available"]
            },
            "message_feedback": fallback_feedback,
            "scenario": scenario,
            "analysis_method": "fallback_heuristic",
            "note": "Used fallback analysis due to LLM parsing issues"
        }
