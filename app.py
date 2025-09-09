import streamlit as st
import asyncio
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

# Import all components
from agents import (
    DynamicCopywriterAgent, 
    DynamicComplianceAgent, 
    DynamicFeedbackAgent, 
    DynamicDecisionAgent
)
from utils.workflow_engine import SimpleWorkflowEngine
from utils.audit_logger import DynamicAuditLogger
from config.scenarios import SCENARIOS
from config.agent_configs import SCENARIO_CONFIGS

# Page configuration
st.set_page_config(
    page_title="Gen AI Communication Tool",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'audience': 'Existing Customers',
        'category': 'CRT Renewals',
        'channels': [],
        'tone': 'Friendly',
        'custom_message': '',
        'use_suggestions': False,
        'selected_suggestion': '',
        'placeholders': {},
        'generated_messages': [],
        'compliance_results': [],
        'final_message': '',
        'compliance_issues': []
    }

if 'audit_logger' not in st.session_state:
    st.session_state.audit_logger = DynamicAuditLogger()

if 'agents_initialized' not in st.session_state:
    audit_logger = st.session_state.audit_logger
    st.session_state.agents = {
        'copywriter': DynamicCopywriterAgent(audit_logger),
        'compliance': DynamicComplianceAgent(audit_logger),
        'feedback': DynamicFeedbackAgent(audit_logger),
        'decision': DynamicDecisionAgent(audit_logger)
    }
    st.session_state.workflow_engine = SimpleWorkflowEngine(st.session_state.agents, audit_logger)
    st.session_state.agents_initialized = True

def run_async(coro):
    """Run async function in streamlit"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def show_progress_bar():
    """Show progress bar based on current step"""
    progress_labels = ["Communication Setup", "Message Details", "Final Results"]
    
    cols = st.columns(3)
    for i, label in enumerate(progress_labels, 1):
        with cols[i-1]:
            if i < st.session_state.step:
                st.markdown(f"✅ **{label}**")
            elif i == st.session_state.step:
                st.markdown(f"🔵 **{label}**")
            else:
                st.markdown(f"⚪ {label}")

def step_1_communication_setup():
    """Step 1: Communication Setup - FIXED: Only one category selected"""
    st.header("📋 Communication Setup")
    show_progress_bar()
    
    st.markdown("---")
    
    # Key Audience Segment (this part is fine)
    st.subheader("Select Key Audience Segment")
    audience = st.radio(
        "",
        ["Existing Customers", "New Leads", "Policyholders at Risk", "Age Group"],
        index=0,
        key="audience_radio"
    )
    
    st.markdown("---")
    
    # **FIXED: Category Selection - Single Radio with All Options**
    st.subheader("Select Category")
    
    # Combine all categories into one list
    all_categories = [
        "Claims", 
        "CX I-Serv", 
        "Group Claims", 
        "iAhead",
        "CRT Renewals",
        "CX IVR", 
        "Group Operations",
        "Logistics",
        "Others"
    ]
    
    # Get current category from session state or default
    current_category = st.session_state.form_data.get('category', 'CRT Renewals')
    
    # Single radio button with all options
    selected_category = st.radio(
        "",
        all_categories,
        index=all_categories.index(current_category),
        key="category_selection",
        label_visibility="collapsed"
    )
    
    # Handle "Others" option
    if selected_category == "Others":
        custom_category = st.text_input("Specify other category:", key="custom_category_input")
        if custom_category:
            selected_category = custom_category
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state.form_data['audience'] = audience
            st.session_state.form_data['category'] = selected_category
            st.session_state.step = 2
            st.rerun()


def step_2_message_details():
    """Step 2: Message Details"""
    st.header("📝 Message Details")
    show_progress_bar()
    
    st.markdown("---")
    
    # Communication Channel Selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Communication Channel")
        st.caption("Multiple options can be selected at once")
        
        channels = []
        if st.checkbox("WhatsApp", key="whatsapp_check"):
            channels.append("WhatsApp")
        if st.checkbox("SMS", key="sms_check"):
            channels.append("SMS")
        if st.checkbox("Email", key="email_check"):
            channels.append("Email")
        if st.checkbox("Push Notification", key="push_check"):
            channels.append("Push Notification")
    
    with col2:
        st.subheader("Select Tone")
        tone = st.selectbox(
            "",
            ["Friendly", "Professional", "Urgency", "Caring", "Casual"],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Message Input Section
    st.subheader("Message Content")
    
    # Tab selection for input method
    tab1, tab2 = st.tabs(["✍️ Enter Custom Message", "💡 Use Suggestions"])
    
    with tab1:
        custom_message = st.text_area(
            "Enter your message here or paste it:",
            height=150,
            placeholder="Type your message here..."
        )
        use_suggestions = False
        selected_suggestion = ""
    
    with tab2:
        st.write("**Pre-defined suggestions based on most used combinations:**")
        
        # Generate dynamic suggestions based on selections
        suggestions = generate_suggestions(
            st.session_state.form_data['audience'], 
            st.session_state.form_data['category']
        )
        
        selected_suggestion = ""
        for i, suggestion in enumerate(suggestions, 1):
            if st.button(f"📝 Suggestion {i}", key=f"suggestion_{i}", use_container_width=True):
                selected_suggestion = suggestion
                use_suggestions = True
                
        if selected_suggestion:
            st.text_area("Selected suggestion:", selected_suggestion, height=100, disabled=True)
    
    # Placeholders section
    with st.expander("🏷️ Configure Placeholders (Optional)"):
        st.write("Add dynamic placeholders for personalization:")
        
        placeholder_count = st.number_input("Number of placeholders", 1, 8, 4)
        placeholders = {}
        
        cols = st.columns(2)
        for i in range(placeholder_count):
            col_idx = i % 2
            with cols[col_idx]:
                key = st.text_input(f"Placeholder {i+1} Name", value=f"Name{i+1}", key=f"ph_key_{i}")
                value = st.text_input(f"Sample Value", value="Sample", key=f"ph_val_{i}")
                if key and value:
                    placeholders[key] = value
    
    st.markdown("---")
    
    # Validation and Navigation
    message_content = selected_suggestion if use_suggestions else custom_message
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    
    with col3:
        if st.button("Next →", type="primary", use_container_width=True):
            if not channels:
                st.error("Please select at least one communication channel")
            elif not message_content.strip():
                st.error("Please enter a message or select a suggestion")
            else:
                # Save form data
                st.session_state.form_data.update({
                    'channels': channels,
                    'tone': tone,
                    'custom_message': custom_message,
                    'use_suggestions': use_suggestions,
                    'selected_suggestion': selected_suggestion,
                    'placeholders': placeholders
                })
                
                # Generate messages using agents
                with st.spinner("🤖 Processing your request..."):
                    process_message_with_agents(message_content, channels[0])  # Use first channel
                
                st.session_state.step = 3
                st.rerun()

def step_3_final_results():
    """Step 3: Final Results with Enhanced Compliance Rules"""
    st.header("📊 Final Results")
    show_progress_bar()
    
    st.markdown("---")
    
    # Summary Section (unchanged)
    st.subheader("📋 Summary")
    summary_data = {
        "Category": st.session_state.form_data['category'],
        "Audience": st.session_state.form_data['audience'],
        "Communication Channel": ", ".join(st.session_state.form_data['channels']),
        "Tone": st.session_state.form_data['tone']
    }
    
    for key, value in summary_data.items():
        st.markdown(f"**{key}:** {value}")
    
    st.markdown("---")
    
    # Final Message Section (unchanged)
    st.subheader("💬 Here's your final message. Kindly review before sending.")
    
    final_message = st.session_state.form_data.get('final_message', '')
    if not final_message:
        if st.session_state.form_data['use_suggestions']:
            final_message = st.session_state.form_data['selected_suggestion']
        else:
            final_message = st.session_state.form_data['custom_message']
    
    # Display message
    with st.container():
        st.text_area("", final_message, height=150, disabled=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📋 Copy Message", use_container_width=True):
                st.code(final_message)
                st.success("Message ready to copy!")
    
    st.markdown("---")
    
    # **NEW: Enhanced Compliance Check with Editable Rules**
    st.subheader("🛡️ Smart Compliance Check")
    
    # Initialize compliance rules in session state
    if 'compliance_todo_rules' not in st.session_state:
        st.session_state.compliance_todo_rules = [
            "Use polite and respectful language",
            "Include accurate contact information", 
            "Add mandatory disclaimers as per policy",
            "Provide clear opt-out instructions",
            "Maintain professional tone throughout",
            "Include sender identification clearly",
            "Ensure message length is appropriate for channel",
            "Use verified statistics and claims only"
        ]
    
    if 'compliance_dont_rules' not in st.session_state:
        st.session_state.compliance_dont_rules = [
            "Don't use absolute guarantees (100%, guaranteed, etc.)",
            "Don't create false urgency (urgent, immediately, etc.)",
            "Don't use misleading or deceptive claims",
            "Don't include unverified percentage claims",
            "Don't use lottery/sweepstakes language (winner, lucky, etc.)",
            "Don't make unrealistic promises",
            "Don't use high-pressure sales tactics",
            "Don't exclude risk factors or conditions"
        ]
    
# **Enhanced Compliance Check Display**
    st.subheader("🛡️ Smart Compliance Check")

    compliance_issues = st.session_state.form_data.get('compliance_issues', [])

    if compliance_issues:
        # Show issues if found
        st.error("**❌ Issues Detected - Corrections needed before sending:**")
        for i, issue in enumerate(compliance_issues, 1):
            st.markdown(f"**{i}.** {issue}")
        
        st.markdown("---")
        
        # Show the editable rules sections (your existing code)
        # ... editable rules code here ...
        
        # Re-check compliance button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Re-check Compliance", use_container_width=True):
                with st.spinner("🤖 Re-analyzing message..."):
                    process_message_with_agents(final_message, st.session_state.form_data['channels'][0])
                st.rerun()
                
    else:
        # Message passed all compliance checks
        st.success("✅ **COMPLIANCE APPROVED!** Message meets all regulatory requirements.")
        
        # Show a celebratory message
        #st.balloons()  # Fun visual feedback
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 214, 160, 0.1) 100%); border-radius: 15px; border: 2px solid #10B981;">
                <h3 style="color: #10B981; margin-bottom: 1rem;">🎉 Ready to Send!</h3>
                <p style="color: #FFFFFF; font-size: 1.1rem;">Your message has passed all compliance checks and is ready for deployment.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Optional: Still show rules but collapsed
    with st.expander("📋 **View Current Compliance Rules**", expanded=False):
        # Show your editable rules here but collapsed by default
        pass

    
    # **NEW: Editable Compliance Rules Sections**
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ To-Do Rules for Compliance")
        st.caption("Edit these rules to customize what should be included in messages")
        
        # Convert list to text for editing
        todo_text = "\n".join(st.session_state.compliance_todo_rules)
        new_todo_text = st.text_area(
            "Edit To-Do Rules (one per line):",
            value=todo_text,
            height=200,
            key="todo_rules_editor",
            help="Each line represents a rule. Add, remove, or edit rules as needed."
        )
        
        # Update session state if text changed
        if new_todo_text != todo_text:
            st.session_state.compliance_todo_rules = [
                line.strip() for line in new_todo_text.splitlines() if line.strip()
            ]
            st.success("✅ To-Do rules updated!")
    
    with col2:
        st.subheader("❌ Don't Do Rules for Compliance")
        st.caption("Edit these rules to customize what should be avoided in messages")
        
        # Convert list to text for editing
        dont_text = "\n".join(st.session_state.compliance_dont_rules)
        new_dont_text = st.text_area(
            "Edit Don't Do Rules (one per line):",
            value=dont_text,
            height=200,
            key="dont_rules_editor",
            help="Each line represents a rule to avoid. Add, remove, or edit rules as needed."
        )
        
        # Update session state if text changed
        if new_dont_text != dont_text:
            st.session_state.compliance_dont_rules = [
                line.strip() for line in new_dont_text.splitlines() if line.strip()
            ]
            st.success("✅ Don't Do rules updated!")
    
    # **NEW: Display Current Rules Summary**
    with st.expander("📋 **Current Compliance Rules Summary**", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ To-Do Rules:**")
            for i, rule in enumerate(st.session_state.compliance_todo_rules, 1):
                st.markdown(f"{i}. {rule}")
        
        with col2:
            st.markdown("**❌ Don't Do Rules:**")
            for i, rule in enumerate(st.session_state.compliance_dont_rules, 1):
                st.markdown(f"{i}. {rule}")
    
    # **NEW: Re-check Compliance Button**
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Re-check Compliance with Updated Rules", use_container_width=True):
            with st.spinner("🤖 Re-analyzing message with updated rules..."):
                # Re-run compliance check with updated rules
                process_message_with_agents(final_message, st.session_state.form_data['channels'][0])
            st.success("✅ Compliance re-check completed!")
            st.rerun()
    
    st.markdown("---")
    
    # Action Buttons (unchanged)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    
    with col2:
        if st.button("🔄 Generate Another Message", use_container_width=True):
            st.session_state.form_data.update({
                'custom_message': '',
                'selected_suggestion': '',
                'generated_messages': [],
                'final_message': '',
                'compliance_issues': []
            })
            st.session_state.step = 2
            st.rerun()
    
    with col3:
        if st.button("🚀 Start New", type="primary", use_container_width=True):
            # Reset all data but keep the compliance rules
            st.session_state.form_data = {
                'audience': 'Existing Customers',
                'category': 'CRT Renewals',
                'channels': [],
                'tone': 'Friendly',
                'custom_message': '',
                'use_suggestions': False,
                'selected_suggestion': '',
                'placeholders': {},
                'generated_messages': [],
                'compliance_results': [],
                'final_message': '',
                'compliance_issues': []
            }
            st.session_state.step = 1
            st.rerun()


def generate_suggestions(audience, category):
    """Generate contextual suggestions based on audience and category"""
    suggestions_map = {
        ("Existing Customers", "CRT Renewals"): [
            "Hi {Name}, Hope you're doing well! This is a gentle reminder that your premium of {Premium Amount} is due on {Date}. Renewing on time ensures your 100% policy benefits continue without any interruption. You can complete your renewal in just a few clicks using our quick pay option. Thank you for being a valued customer!",
            "Dear {Name}, Your policy renewal is approaching. Please pay {Premium Amount} by {Date} to maintain continuous coverage.",
            "Hi {Name}, Don't let your policy lapse! Renew today with {Premium Amount} to keep your family protected.",
            "Hello {Name}, Your renewal of {Premium Amount} is due {Date}. Quick pay available for instant processing."
        ],
        ("New Leads", "Claims"): [
            "Welcome! We're here to help you with your insurance needs. Contact us to learn about our comprehensive coverage options.",
            "Hi {Name}, Thank you for your interest in our services. Let us show you how we can protect what matters most to you.",
            "Hello {Name}, Our team is ready to assist you with finding the perfect insurance solution.",
            "Welcome to our family! Let's discuss how we can provide you with peace of mind through our insurance products."
        ],
        ("Policyholders at Risk", "Group Claims"): [
            "Hi {Name}, We've noticed some concerns with your policy. Let's work together to resolve this quickly.",
            "Dear {Name}, Our support team is here to help you with your policy concerns. Please contact us immediately.",
            "Hello {Name}, We value your relationship with us. Let's discuss how we can assist you better.",
            "Hi {Name}, We're committed to resolving your concerns. Our dedicated team is standing by to help."
        ]
    }
    
    key = (audience, category)
    return suggestions_map.get(key, [
        f"Hi {{Name}}, We have an important update regarding your {category.lower()}. Please contact us for more details.",
        f"Dear {{Name}}, Thank you for choosing us for your {category.lower()} needs. We're here to help!",
        f"Hello {{Name}}, We hope this message finds you well. We're reaching out about your {category.lower()}.",
        f"Hi {{Name}}, Our team is available to assist you with any {category.lower()} related questions."
    ])

def process_message_with_agents(message_content, channel):
    """Process message through agents pipeline - STOPS if compliance passes"""
    try:
        # Map categories to scenarios
        scenario_map = {
            "CRT Renewals": "insurance_renewal",
            "Claims": "insurance_renewal", 
            "Group Claims": "insurance_renewal",
            "CX I-Serv": "healthcare_reminder",
            "CX IVR": "healthcare_reminder"
        }
        
        category = st.session_state.form_data['category']
        scenario = scenario_map.get(category, "insurance_renewal")
        
        # Prepare input data
        input_data = {
            'audience': st.session_state.form_data['audience'],
            'age_group': 'Above 40',  # Default for insurance
            'channel': channel,
            'tone': st.session_state.form_data['tone'],
            'placeholders': st.session_state.form_data['placeholders'],
            'num_messages': 1,  # Generate single message for final result
            'custom_message': message_content
        }
        
        # Run workflow - Start with copywriter first
        results = run_async(st.session_state.workflow_engine.execute_dynamic_workflow(
            scenario=scenario,
            input_data=input_data,
            agent_sequence=["copywriter"]  # Only run copywriter first
        ))
        
        # Process copywriter results
        generated_message = message_content  # Default to original message
        if 'copywriter' in results and results['copywriter'].get('success'):
            messages = results['copywriter']['data'].get('messages', [])
            if messages:
                generated_message = messages[0]['content']
                st.session_state.form_data['generated_messages'] = messages
        
        # Update final message
        st.session_state.form_data['final_message'] = generated_message
        
        # Now run compliance check on the generated message
        compliance_results = run_async(st.session_state.workflow_engine.execute_dynamic_workflow(
            scenario=scenario,
            input_data={**input_data, 'custom_message': generated_message},
            agent_sequence=["compliance"]  # Only compliance agent
        ))
        
        # Process compliance results
        compliance_issues = []
        if 'compliance' in compliance_results and compliance_results['compliance'].get('success'):
            compliance_data = compliance_results['compliance']['data']
            message_analyses = compliance_data.get('message_analyses', [])
            
            for analysis in message_analyses:
                violations = analysis.get('violations', [])
                for violation in violations:
                    if violation.get('severity') in ['HIGH', 'MEDIUM']:
                        compliance_issues.append(violation.get('description', 'Compliance issue detected'))
        
        # Update compliance issues
        st.session_state.form_data['compliance_issues'] = compliance_issues
        st.session_state.form_data['compliance_results'] = message_analyses if 'message_analyses' in locals() else []
        
        # **STOP PROCESSING IF NO COMPLIANCE ISSUES FOUND**
        if not compliance_issues:
            st.success("✅ **All compliance checks passed!** No further processing needed.")
            st.info("🎉 **Message is ready to send** - meets all regulatory requirements.")
            return  # Stop here - no need for further agent processing
        
        # **ONLY CONTINUE IF COMPLIANCE ISSUES EXIST**
        st.warning(f"⚠️ **Found {len(compliance_issues)} compliance issues** - additional processing may be needed.")
        
        # Optional: Could run feedback or decision agents here if compliance fails
        # But for now, we just stop at compliance check
        
    except Exception as e:
        # Fallback if processing fails
        st.session_state.form_data['final_message'] = message_content
        st.session_state.form_data['compliance_issues'] = [f"Processing error: {str(e)}"]
        st.error(f"🚨 **Processing Error:** {str(e)}")


def main():
    # Header
    st.title("📧 Gen AI Communication Tool")
    st.markdown("*AI-Powered Message Generation with Compliance Checking*")
    
    # Add some custom CSS for better styling
    st.markdown("""
        <style>
        .stRadio > label { font-weight: bold; }
        .stCheckbox > label { font-weight: normal; }
        .main-header { font-size: 2em; color: #1f77b4; }
        </style>
    """, unsafe_allow_html=True)
    
    # Route to appropriate step
    if st.session_state.step == 1:
        step_1_communication_setup()
    elif st.session_state.step == 2:
        step_2_message_details()
    elif st.session_state.step == 3:
        step_3_final_results()
    
    # Footer
    st.markdown("---")
    #st.markdown("*Built with ❤️ using Streamlit and OpenAI GPT-4*")

if __name__ == "__main__":
    main()
