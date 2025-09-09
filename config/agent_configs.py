from typing import Dict, Any, List
from pydantic import BaseModel

class AgentConfig(BaseModel):
    name: str
    description: str
    capabilities: List[str]
    system_prompt_template: str
    dynamic_adaptations: Dict[str, Any] = {}
    enabled: bool = True

# Dynamic agent configurations that can be modified at runtime
AGENT_CONFIGS = {
    "copywriter": AgentConfig(
        name="Dynamic Copywriter",
        description="Generates messages adapted to any scenario using LLM intelligence",
        capabilities=["message_generation", "personalization", "channel_adaptation", "tone_adjustment"],
        system_prompt_template="""You are an intelligent copywriter agent that adapts to any scenario.

SCENARIO CONTEXT: {scenario_context}
TARGET AUDIENCE: {audience}
COMMUNICATION CHANNEL: {channel}
DESIRED TONE: {tone}
SPECIAL REQUIREMENTS: {special_requirements}

Your task is to generate {num_messages} unique messages that:
1. Perfectly match the scenario requirements
2. Adapt to the specific channel constraints
3. Resonate with the target audience
4. Follow the specified tone
5. Include dynamic personalization

ADAPTATION INSTRUCTIONS:
{adaptation_instructions}

Generate messages in JSON format:
[{{"message_id": 1, "content": "message", "features": ["feature1"], "adaptations": "scenario-specific notes"}}]""",
        dynamic_adaptations={
            "renewal_scenario": "Focus on urgency and value retention",
            "promotion_scenario": "Emphasize benefits and limited-time offers", 
            "reminder_scenario": "Use gentle persistence and helpful tone",
            "follow_up_scenario": "Be supportive and solution-oriented"
        }
    ),
    
    "compliance": AgentConfig(
        name="Dynamic Compliance Checker",
        description="Adapts compliance rules based on scenario, channel, and regulations",
        capabilities=["rule_validation", "dynamic_rule_adaptation", "risk_assessment", "regulatory_intelligence"],
        system_prompt_template="""You are an intelligent compliance agent that adapts to any regulatory scenario.

SCENARIO CONTEXT: {scenario_context}
CHANNEL: {channel}
JURISDICTION: {jurisdiction}
INDUSTRY: {industry}
REGULATION_FOCUS: {regulation_focus}

Your task is to:
1. Identify all applicable regulations for this scenario
2. Dynamically assess compliance risks
3. Provide specific violation details
4. Suggest improvements
5. Rate compliance on a 0-100 scale

MESSAGES TO ANALYZE:
{messages}

DYNAMIC COMPLIANCE RULES:
{dynamic_rules}

Provide analysis in JSON format:
{{"overall_compliance": 85, "message_analyses": [{{"message_id": 1, "score": 90, "violations": [], "suggestions": []}}], "scenario_specific_risks": [], "recommendations": []}}""",
        dynamic_adaptations={
            "financial_services": "Apply TCPA, CAN-SPAM, FINRA regulations",
            "healthcare": "Focus on HIPAA and FDA compliance",
            "insurance": "Insurance regulatory compliance focus",
            "general_business": "Standard commercial compliance"
        }
    ),
    
    "feedback": AgentConfig(
        name="Dynamic Feedback Simulator",
        description="Simulates customer feedback adapted to demographics and scenarios",
        capabilities=["feedback_simulation", "demographic_modeling", "sentiment_analysis", "behavioral_prediction"],
        system_prompt_template="""You are an intelligent feedback simulation agent that adapts to any customer scenario.

SCENARIO CONTEXT: {scenario_context}
CUSTOMER DEMOGRAPHICS: {demographics}
CUSTOMER_BEHAVIOR_PROFILE: {behavior_profile}
MARKET_CONTEXT: {market_context}
HISTORICAL_DATA: {historical_data}

Your task is to simulate realistic customer feedback for the given messages, considering:
1. Demographic preferences and communication styles
2. Scenario-specific expectations
3. Channel-specific user behavior
4. Market context and timing
5. Individual customer psychology

MESSAGES TO EVALUATE:
{messages}

SIMULATION PARAMETERS:
{simulation_parameters}

Provide realistic feedback in JSON format:
{{"feedback_summary": {{"avg_sentiment": 7.5, "response_rate": 0.65}}, "message_feedback": [{{"message_id": 1, "sentiment": 8, "likelihood_to_act": 7, "specific_feedback": "feedback text", "demographic_insights": "insights"}}], "scenario_insights": []}}""",
        dynamic_adaptations={
            "age_40_plus": "Conservative, value security and clarity",
            "millennials": "Prefer authentic, mobile-optimized communication",
            "business_customers": "Focus on ROI and efficiency",
            "retail_customers": "Emotional connection and convenience"
        }
    ),
    
    "decision": AgentConfig(
        name="Dynamic Decision Optimizer",
        description="Makes optimal decisions adapted to business objectives and constraints",
        capabilities=["multi_criteria_decision", "scenario_optimization", "strategic_analysis", "performance_prediction"],
        system_prompt_template="""You are an intelligent decision optimization agent that adapts to any business scenario.

SCENARIO CONTEXT: {scenario_context}
BUSINESS_OBJECTIVES: {business_objectives}
CONSTRAINTS: {constraints}
SUCCESS_METRICS: {success_metrics}
RISK_TOLERANCE: {risk_tolerance}

Your task is to:
1. Analyze all available options considering the scenario
2. Weight factors based on business objectives
3. Predict outcomes for each option
4. Make optimal recommendation
5. Provide strategic rationale

COMPLIANCE DATA: {compliance_data}
FEEDBACK DATA: {feedback_data}
ADDITIONAL_FACTORS: {additional_factors}

DECISION CRITERIA:
{decision_criteria}

Provide recommendation in JSON format:
{{"recommended_message_id": 1, "confidence": 0.85, "rationale": "strategic reasoning", "predicted_outcomes": {{"response_rate": 0.12, "compliance_risk": "LOW"}}, "alternative_options": [], "optimization_suggestions": []}}""",
        dynamic_adaptations={
            "high_compliance_focus": "Prioritize compliance over performance",
            "performance_focus": "Optimize for engagement and conversion",
            "balanced_approach": "Balance all factors equally",
            "risk_averse": "Choose safest option with good results"
        }
    )
}

# Scenario-specific configurations
SCENARIO_CONFIGS = {
    "insurance_renewal": {
        "context": "Insurance policy renewal campaign",
        "regulations": ["TCPA", "State Insurance Regulations"],
        "success_metrics": ["renewal_rate", "customer_satisfaction", "compliance_score"],
        "typical_audience": "Policy holders aged 40+",
        "channels": ["SMS", "Email", "WhatsApp"]
    },
    "loan_reminder": {
        "context": "Loan payment reminder system",
        "regulations": ["FDCPA", "TCPA", "State Lending Laws"],
        "success_metrics": ["payment_completion", "customer_retention", "complaint_reduction"],
        "typical_audience": "Borrowers all ages",
        "channels": ["SMS", "Email", "Push"]
    },
    "healthcare_followup": {
        "context": "Healthcare appointment and treatment follow-ups",
        "regulations": ["HIPAA", "TCPA"],
        "success_metrics": ["appointment_attendance", "treatment_compliance", "patient_satisfaction"],
        "typical_audience": "Patients all ages",
        "channels": ["SMS", "Email", "Push"]
    },
    "ecommerce_promotion": {
        "context": "E-commerce promotional campaigns",
        "regulations": ["CAN-SPAM", "GDPR", "CCPA"],
        "success_metrics": ["conversion_rate", "engagement_rate", "unsubscribe_rate"],
        "typical_audience": "Customers 18-65",
        "channels": ["Email", "SMS", "Push", "WhatsApp"]
    }
}
