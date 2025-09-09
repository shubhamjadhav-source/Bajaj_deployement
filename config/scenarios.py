from typing import Dict, Any

SCENARIOS = {
    "financial_renewal": {
        "name": "Financial Services Renewal",
        "agent_adaptations": {
            "copywriter": {
                "focus": "Trust, security, value proposition",
                "tone_adjustment": "Professional yet warm",
                "personalization_level": "high"
            },
            "compliance": {
                "primary_regulations": ["TCPA", "FINRA", "State Financial"],
                "risk_threshold": "low",
                "special_requirements": ["opt_out_language", "clear_identification"]
            },
            "feedback": {
                "demographic_model": "conservative_investors",
                "response_patterns": "security_focused",
                "decision_factors": ["trust", "clarity", "value"]
            },
            "decision": {
                "optimization_priority": "compliance_first",
                "success_weight": {"compliance": 0.4, "engagement": 0.3, "conversion": 0.3}
            }
        }
    },
    
    "healthcare_reminder": {
        "name": "Healthcare Appointment Reminder",
        "agent_adaptations": {
            "copywriter": {
                "focus": "Health importance, convenience, care",
                "tone_adjustment": "Caring and supportive",
                "personalization_level": "medium"
            },
            "compliance": {
                "primary_regulations": ["HIPAA", "HITECH"],
                "risk_threshold": "very_low",
                "special_requirements": ["phi_protection", "secure_messaging"]
            },
            "feedback": {
                "demographic_model": "health_conscious",
                "response_patterns": "appointment_focused",
                "decision_factors": ["convenience", "health_importance", "trust"]
            },
            "decision": {
                "optimization_priority": "patient_care",
                "success_weight": {"compliance": 0.5, "patient_satisfaction": 0.3, "attendance": 0.2}
            }
        }
    },
    
    "ecommerce_promotion": {
        "name": "E-commerce Promotional Campaign",
        "agent_adaptations": {
            "copywriter": {
                "focus": "Value, urgency, benefits",
                "tone_adjustment": "Energetic and persuasive",
                "personalization_level": "high"
            },
            "compliance": {
                "primary_regulations": ["CAN-SPAM", "GDPR"],
                "risk_threshold": "medium",
                "special_requirements": ["unsubscribe_link", "sender_identification"]
            },
            "feedback": {
                "demographic_model": "online_shoppers",
                "response_patterns": "deal_focused",
                "decision_factors": ["value", "urgency", "trust"]
            },
            "decision": {
                "optimization_priority": "conversion",
                "success_weight": {"conversion": 0.4, "engagement": 0.3, "compliance": 0.3}
            }
        }
    }
}
