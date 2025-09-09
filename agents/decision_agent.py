from typing import Dict, Any, List
import json
from .base_agent import BaseDynamicAgent

class DynamicDecisionAgent(BaseDynamicAgent):
    def __init__(self, audit_logger):
        super().__init__("decision", audit_logger)
        
        # Scenario-specific decision criteria weights
        self.decision_weights = {
            "insurance_renewal": {
                "compliance_score": 0.4,
                "customer_sentiment": 0.3,
                "action_likelihood": 0.2,
                "clarity": 0.1
            },
            "healthcare_reminder": {
                "compliance_score": 0.5,
                "customer_sentiment": 0.2,
                "action_likelihood": 0.2,
                "clarity": 0.1
            },
            "loan_reminder": {
                "compliance_score": 0.45,
                "customer_sentiment": 0.25,
                "action_likelihood": 0.2,
                "clarity": 0.1
            },
            "ecommerce_promotion": {
                "compliance_score": 0.3,
                "customer_sentiment": 0.25,
                "action_likelihood": 0.35,
                "clarity": 0.1
            },
            "default": {
                "compliance_score": 0.35,
                "customer_sentiment": 0.3,
                "action_likelihood": 0.25,
                "clarity": 0.1
            }
        }
    
    def _generate_dynamic_user_prompt(self, input_data: Dict[str, Any], scenario: str, adaptations: Dict[str, Any]) -> str:
        """Generate decision-specific user prompt"""
        
        # Get results from previous agents with DEFENSIVE PROGRAMMING
        previous_results = input_data.get('previous_results', {})
        
        # SAFE DATA EXTRACTION with defaults
        copywriter_results = previous_results.get('copywriter', {}).get('data', {})
        compliance_results = previous_results.get('compliance', {}).get('data', {})
        feedback_results = previous_results.get('feedback', {}).get('data', {})
        
        # Ensure we have valid data structures
        if not copywriter_results:
            copywriter_results = {"messages": []}
        if not compliance_results:
            compliance_results = {"message_analyses": [], "overall_compliance": 50}
        if not feedback_results:
            feedback_results = {"message_feedback": [], "feedback_summary": {}}
        
        # Get business context with defaults
        business_objectives = input_data.get('business_objectives') or self._get_default_objectives(scenario)
        risk_tolerance = input_data.get('risk_tolerance', 'medium')
        
        # Get decision weights for scenario
        weights = self.decision_weights.get(scenario, self.decision_weights['default'])
        
        prompt_parts = [
            f"SCENARIO: {scenario}",
            f"TASK: Select the optimal message based on comprehensive analysis",
            "",
            "BUSINESS OBJECTIVES:",
        ]
        
        # SAFE iteration over business objectives
        if business_objectives:
            for objective in business_objectives:
                if objective and objective.strip():  # Avoid empty strings
                    prompt_parts.append(f"- {objective}")
        
        prompt_parts.extend([
            "",
            f"RISK TOLERANCE: {risk_tolerance}",
            "",
            "DECISION CRITERIA WEIGHTS:",
        ])
        
        for criterion, weight in weights.items():
            prompt_parts.append(f"- {criterion}: {weight*100:.0f}%")
        
        prompt_parts.extend([
            "",
            "ANALYSIS DATA:",
            "",
            "COPYWRITER RESULTS:",
            json.dumps(copywriter_results, indent=2),
            "",
            "COMPLIANCE RESULTS:",
            json.dumps(compliance_results, indent=2),
            "",
            "FEEDBACK RESULTS:",
            json.dumps(feedback_results, indent=2),
            "",
            "DECISION REQUIREMENTS:",
            "1. Rank all messages by composite score",
            "2. Consider scenario-specific priorities",
            "3. Account for risk tolerance level",
            "4. Provide strategic rationale",
            "5. Predict performance outcomes",
            "6. Suggest optimization opportunities",
            "",
            "RETURN FORMAT: Valid JSON only:",
            '{"recommended_message_id": 1, "confidence": 0.85, "composite_score": 87.3, "ranking": [{"message_id": 1, "score": 87.3, "rank": 1}], "rationale": "Strategic reasoning", "predicted_outcomes": {"response_rate": 0.12, "compliance_risk": "LOW", "customer_satisfaction": 8.2}, "optimization_suggestions": ["suggestion1"], "risk_assessment": "LOW"}'
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_default_objectives(self, scenario: str) -> List[str]:
        """Get default business objectives for scenario"""
        objectives_map = {
            "insurance_renewal": [
                "Maximize policy renewal rates",
                "Maintain regulatory compliance",
                "Preserve customer relationships",
                "Minimize complaints and churn"
            ],
            "healthcare_reminder": [
                "Improve appointment attendance",
                "Enhance patient satisfaction",
                "Ensure HIPAA compliance",
                "Reduce administrative overhead"
            ],
            "loan_reminder": [
                "Increase payment compliance",
                "Maintain customer relationships",
                "Ensure regulatory compliance",
                "Minimize default rates"
            ],
            "ecommerce_promotion": [
                "Maximize conversion rates",
                "Increase customer engagement",
                "Build brand loyalty",
                "Optimize marketing ROI"
            ]
        }
        
        return objectives_map.get(scenario, [
            "Achieve communication objectives",
            "Maintain compliance standards",
            "Optimize customer experience",
            "Maximize business outcomes"
        ])
    
    def _process_llm_response(self, response_content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Process decision LLM response with DEFENSIVE PROGRAMMING"""
        try:
            # Parse JSON response
            decision_data = json.loads(response_content.strip())
            
            if not isinstance(decision_data, dict):
                raise ValueError("Invalid decision response format")
            
            # Validate and enhance decision analysis
            enhanced_decision = self._enhance_decision_analysis(decision_data, input_data, scenario)
            
            # Generate deployment recommendations
            deployment_rec = self._generate_deployment_recommendations(enhanced_decision, scenario)
            
            # Calculate decision confidence
            decision_confidence = self._calculate_decision_confidence(enhanced_decision, input_data)
            
            return {
                **enhanced_decision,
                "deployment_recommendations": deployment_rec,
                "decision_confidence": decision_confidence,
                "scenario": scenario,
                "decision_methodology": "Multi-criteria LLM-based optimization",
                "weights_applied": self.decision_weights.get(scenario, self.decision_weights['default'])
            }
            
        except json.JSONDecodeError:
            return self._fallback_decision_analysis(response_content, input_data, scenario)
        except Exception as e:
            return {
                "recommended_message_id": 1,
                "confidence": 0.3,
                "error": f"Failed to process decision analysis: {str(e)}",
                "scenario": scenario,
                "fallback_applied": True
            }
    
    def _enhance_decision_analysis(self, decision_data: Dict[str, Any], input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Enhance decision analysis with additional calculations - DEFENSIVE VERSION"""
        
        # Get previous results with SAFE defaults
        previous_results = input_data.get('previous_results', {})
        compliance_data = previous_results.get('compliance', {}).get('data', {})
        feedback_data = previous_results.get('feedback', {}).get('data', {})
        
        # SAFE defaults for data structures
        if not compliance_data:
            compliance_data = {"message_analyses": [], "overall_compliance": 50}
        if not feedback_data:
            feedback_data = {"message_feedback": [], "feedback_summary": {}}
        
        # Validate recommended message exists
        recommended_id = decision_data.get('recommended_message_id', 1)
        message_analyses = compliance_data.get('message_analyses', [])
        
        # SAFE check for message existence
        if message_analyses and not any(m.get('message_id') == recommended_id for m in message_analyses):
            # Fall back to first available message
            recommended_id = message_analyses.get('message_id', 1)
            decision_data['recommended_message_id'] = recommended_id
        
        # Calculate comprehensive scores if not provided
        if 'ranking' not in decision_data:
            decision_data['ranking'] = self._calculate_message_ranking(compliance_data, feedback_data, scenario)
        
        # Add performance predictions if not provided
        if 'predicted_outcomes' not in decision_data:
            decision_data['predicted_outcomes'] = self._predict_performance_outcomes(
                recommended_id, compliance_data, feedback_data, scenario
            )
        
        # Add risk assessment if not provided
        if 'risk_assessment' not in decision_data:
            decision_data['risk_assessment'] = self._assess_overall_risk(
                recommended_id, compliance_data, feedback_data
            )
        
        return decision_data
    
    def _calculate_message_ranking(self, compliance_data: Dict[str, Any], feedback_data: Dict[str, Any], scenario: str) -> List[Dict[str, Any]]:
        """Calculate message ranking using scenario-specific weights - DEFENSIVE VERSION"""
        
        weights = self.decision_weights.get(scenario, self.decision_weights['default'])
        
        # SAFE data extraction with defaults
        message_analyses = compliance_data.get('message_analyses', [])
        feedback_analyses = feedback_data.get('message_feedback', [])
        
        # Return empty if no data
        if not message_analyses:
            return []
        
        # Create feedback lookup with SAFE handling
        feedback_lookup = {}
        if feedback_analyses:
            for f in feedback_analyses:
                if f and 'message_id' in f:
                    feedback_lookup[f['message_id']] = f
        
        rankings = []
        
        # SAFE iteration with None checking
        for compliance_analysis in message_analyses:
            if not compliance_analysis:
                continue
                
            message_id = compliance_analysis.get('message_id', 0)
            feedback = feedback_lookup.get(message_id, {})
            
            # Calculate weighted score with SAFE defaults
            compliance_score = compliance_analysis.get('compliance_score', 0) / 100
            sentiment_score = feedback.get('sentiment_score', 5) / 10
            action_score = feedback.get('action_likelihood', 5) / 10
            clarity_score = feedback.get('clarity_score', 5) / 10
            
            composite_score = (
                compliance_score * weights['compliance_score'] +
                sentiment_score * weights['customer_sentiment'] +
                action_score * weights['action_likelihood'] +
                clarity_score * weights['clarity']
            ) * 100
            
            rankings.append({
                "message_id": message_id,
                "composite_score": round(composite_score, 1),
                "component_scores": {
                    "compliance": round(compliance_score * 100, 1),
                    "sentiment": round(sentiment_score * 10, 1),
                    "action": round(action_score * 10, 1),
                    "clarity": round(clarity_score * 10, 1)
                }
            })
        
        # Sort by composite score
        rankings.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Add ranks
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
        
        return rankings
    
    def _predict_performance_outcomes(self, message_id: int, compliance_data: Dict[str, Any], feedback_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Predict performance outcomes for recommended message - DEFENSIVE VERSION"""
        
        # SAFE data extraction with defaults
        message_analyses = compliance_data.get('message_analyses', [])
        feedback_analyses = feedback_data.get('message_feedback', [])
        
        # Find message data with SAFE handling
        message_compliance = {}
        message_feedback = {}
        
        # SAFE search for message data
        if message_analyses:
            for m in message_analyses:
                if m and m.get('message_id') == message_id:
                    message_compliance = m
                    break
        
        if feedback_analyses:
            for f in feedback_analyses:
                if f and f.get('message_id') == message_id:
                    message_feedback = f
                    break
        
        # Calculate scores with SAFE defaults
        compliance_score = message_compliance.get('compliance_score', 70) / 100
        sentiment_score = message_feedback.get('sentiment_score', 5) / 10
        action_score = message_feedback.get('action_likelihood', 5) / 10
        
        # Scenario-specific outcome predictions
        if scenario == "insurance_renewal":
            base_renewal_rate = 0.75
            response_rate = min(0.25, action_score * 0.3)
            renewal_rate = base_renewal_rate * (0.8 + sentiment_score * 0.2)
            
            outcomes = {
                "response_rate": round(response_rate, 3),
                "renewal_rate": round(renewal_rate, 3),
                "customer_satisfaction": round(sentiment_score * 10, 1),
                "compliance_risk": message_compliance.get('risk_level', 'MEDIUM')
            }
            
        elif scenario == "healthcare_reminder":
            base_attendance_rate = 0.8
            response_rate = min(0.4, action_score * 0.5)
            attendance_rate = base_attendance_rate * (0.9 + sentiment_score * 0.1)
            
            outcomes = {
                "response_rate": round(response_rate, 3),
                "appointment_attendance": round(attendance_rate, 3),
                "patient_satisfaction": round(sentiment_score * 10, 1),
                "compliance_risk": message_compliance.get('risk_level', 'MEDIUM')
            }
            
        elif scenario == "ecommerce_promotion":
            response_rate = min(0.2, action_score * 0.25)
            conversion_rate = response_rate * sentiment_score * 0.6
            
            outcomes = {
                "response_rate": round(response_rate, 3),
                "conversion_rate": round(conversion_rate, 3),
                "engagement_score": round(sentiment_score * 10, 1),
                "compliance_risk": message_compliance.get('risk_level', 'MEDIUM')
            }
            
        else:
            # Default predictions
            outcomes = {
                "response_rate": round(min(0.15, action_score * 0.2), 3),
                "engagement_score": round(sentiment_score * 10, 1),
                "compliance_risk": message_compliance.get('risk_level', 'MEDIUM')
            }
        
        return outcomes
    
    def _assess_overall_risk(self, message_id: int, compliance_data: Dict[str, Any], feedback_data: Dict[str, Any]) -> str:
        """Assess overall risk for recommended message - DEFENSIVE VERSION"""
        
        # SAFE data extraction
        message_analyses = compliance_data.get('message_analyses', [])
        
        # Find message compliance data
        message_compliance = {}
        if message_analyses:
            for m in message_analyses:
                if m and m.get('message_id') == message_id:
                    message_compliance = m
                    break
        
        # SAFE assessment with defaults
        compliance_risk = message_compliance.get('risk_level', 'MEDIUM')
        compliance_score = message_compliance.get('compliance_score', 70)
        violations = len(message_compliance.get('violations', []))
        
        if compliance_risk == 'HIGH' or compliance_score < 60 or violations > 2:
            return 'HIGH'
        elif compliance_risk == 'MEDIUM' or compliance_score < 80 or violations > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_deployment_recommendations(self, decision_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Generate deployment recommendations - DEFENSIVE VERSION"""
        
        risk_level = decision_data.get('risk_assessment', 'MEDIUM')
        confidence = decision_data.get('confidence', 0.5)
        predicted_outcomes = decision_data.get('predicted_outcomes', {})
        compliance_risk = predicted_outcomes.get('compliance_risk', 'MEDIUM')
        
        if risk_level == 'LOW' and confidence >= 0.8 and compliance_risk == 'LOW':
            deployment_status = "APPROVED_FOR_IMMEDIATE_DEPLOYMENT"
            recommendations = [
                "Message is ready for deployment",
                "Monitor initial performance metrics",
                "Track customer feedback and compliance"
            ]
        elif risk_level == 'MEDIUM' or confidence >= 0.6:
            deployment_status = "APPROVED_WITH_MONITORING"
            recommendations = [
                "Deploy with enhanced monitoring",
                "Review performance after 24-48 hours",
                "Be prepared to make adjustments",
                "Consider A/B testing with alternative messages"
            ]
        else:
            deployment_status = "REQUIRES_REVIEW"
            recommendations = [
                "Message requires additional review before deployment",
                "Address identified compliance concerns",
                "Consider regenerating messages with different parameters",
                "Seek legal/compliance team approval if needed"
            ]
        
        return {
            "deployment_status": deployment_status,
            "recommendations": recommendations,
            "monitoring_requirements": self._get_monitoring_requirements(scenario),
            "success_metrics": self._get_success_metrics(scenario)
        }
    
    def _get_monitoring_requirements(self, scenario: str) -> List[str]:
        """Get scenario-specific monitoring requirements"""
        monitoring_map = {
            "insurance_renewal": [
                "Monitor renewal completion rates",
                "Track customer service inquiries",
                "Watch for compliance complaints",
                "Analyze response timing patterns"
            ],
            "healthcare_reminder": [
                "Monitor appointment scheduling rates",
                "Track patient satisfaction scores",
                "Watch for privacy-related concerns",
                "Analyze no-show rates"
            ],
            "ecommerce_promotion": [
                "Monitor click-through rates",
                "Track conversion rates",
                "Watch unsubscribe rates",
                "Analyze customer engagement patterns"
            ]
        }
        
        return monitoring_map.get(scenario, [
            "Monitor response rates",
            "Track customer feedback",
            "Watch for compliance issues",
            "Analyze performance metrics"
        ])
    
    def _get_success_metrics(self, scenario: str) -> List[str]:
        """Get scenario-specific success metrics"""
        metrics_map = {
            "insurance_renewal": [
                "Renewal rate > 80%",
                "Customer satisfaction > 8.0",
                "Compliance score > 85%",
                "Response time < 24 hours"
            ],
            "healthcare_reminder": [
                "Appointment attendance > 85%",
                "Patient satisfaction > 8.5",
                "Compliance score > 90%",
                "Privacy incidents = 0"
            ],
            "ecommerce_promotion": [
                "Conversion rate > baseline + 15%",
                "Engagement rate > 12%",
                "Unsubscribe rate < 2%",
                "Customer satisfaction > 7.5"
            ]
        }
        
        return metrics_map.get(scenario, [
            "Response rate > 10%",
            "Customer satisfaction > 7.0",
            "Compliance score > 80%",
            "No major issues reported"
        ])
    
    def _calculate_decision_confidence(self, decision_data: Dict[str, Any], input_data: Dict[str, Any]) -> float:
        """Calculate confidence in decision quality - DEFENSIVE VERSION"""
        
        # Factors affecting confidence
        factors = []
        
        # Data quality factor
        previous_results = input_data.get('previous_results', {})
        has_compliance = 'compliance' in previous_results and previous_results['compliance'].get('success', False)
        has_feedback = 'feedback' in previous_results and previous_results['feedback'].get('success', False)
        has_copywriter = 'copywriter' in previous_results and previous_results['copywriter'].get('success', False)
        
        data_quality = (has_compliance + has_feedback + has_copywriter) / 3
        factors.append(data_quality)
        
        # Decision consistency factor (if ranking is provided)
        ranking = decision_data.get('ranking', [])
        if len(ranking) >= 2:
            top_score = ranking.get('composite_score', 0)
            second_score = ranking[31].get('composite_score', 0)
            consistency = min(1.0, (top_score - second_score) / 20)  # Higher gap = higher confidence
            factors.append(consistency)
        else:
            factors.append(0.5)
        
        # Risk assessment factor
        risk_level = decision_data.get('risk_assessment', 'MEDIUM')
        risk_factor = 1.0 if risk_level == 'LOW' else (0.7 if risk_level == 'MEDIUM' else 0.3)
        factors.append(risk_factor)
        
        # LLM confidence factor
        llm_confidence = decision_data.get('confidence', 0.5)
        factors.append(llm_confidence)
        
        # Calculate overall confidence
        overall_confidence = sum(factors) / len(factors)
        return round(overall_confidence, 2)
    
    def _fallback_decision_analysis(self, content: str, input_data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Fallback decision analysis when JSON parsing fails - DEFENSIVE VERSION"""
        
        # Get available data with SAFE defaults
        previous_results = input_data.get('previous_results', {})
        compliance_data = previous_results.get('compliance', {}).get('data', {})
        feedback_data = previous_results.get('feedback', {}).get('data', {})
        
        # Simple rule-based decision with SAFE handling
        message_scores = []
        
        compliance_analyses = compliance_data.get('message_analyses', [])
        feedback_analyses = feedback_data.get('message_feedback', [])
        
        # SAFE feedback lookup
        feedback_lookup = {}
        if feedback_analyses:
            for f in feedback_analyses:
                if f and 'message_id' in f:
                    feedback_lookup[f['message_id']] = f
        
        # SAFE scoring
        if compliance_analyses:
            for compliance_analysis in compliance_analyses:
                if not compliance_analysis:
                    continue
                    
                message_id = compliance_analysis.get('message_id', 1)
                feedback = feedback_lookup.get(message_id, {})
                
                # Simple scoring with defaults
                compliance_score = compliance_analysis.get('compliance_score', 0)
                sentiment_score = feedback.get('sentiment_score', 5) * 10
                
                composite_score = (compliance_score * 0.6) + (sentiment_score * 0.4)
                
                message_scores.append({
                    "message_id": message_id,
                    "composite_score": composite_score,
                    "compliance_score": compliance_score,
                    "sentiment_score": sentiment_score
                })
        
        # Select best message with SAFE handling
        if message_scores:
            best_message = max(message_scores, key=lambda x: x['composite_score'])
            recommended_id = best_message['message_id']
            composite_score = best_message['composite_score']
        else:
            recommended_id = 1
            composite_score = 70
        
        return {
            "recommended_message_id": recommended_id,
            "confidence": 0.6,
            "composite_score": composite_score,
            "rationale": "Fallback decision based on compliance and sentiment scores",
            "predicted_outcomes": {
                "response_rate": 0.08,
                "compliance_risk": "MEDIUM"
            },
            "risk_assessment": "MEDIUM",
            "scenario": scenario,
            "analysis_method": "fallback_rule_based",
            "note": "Used fallback analysis due to LLM parsing issues"
        }
