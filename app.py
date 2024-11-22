import streamlit as st
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from process import AIDoctor, get_voice_input, speak_text

class StreamlitApp:
    def __init__(self):
        self.ai_doctor = AIDoctor()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'user_name' not in st.session_state:
            st.session_state.user_name = None
        if 'user_age' not in st.session_state:
            st.session_state.user_age = None
        if 'user_sex' not in st.session_state:
            st.session_state.user_sex = None
        if 'user_height' not in st.session_state:
            st.session_state.user_height = None
        if 'user_weight' not in st.session_state:
            st.session_state.user_weight = None
        if 'user_allergies' not in st.session_state:
            st.session_state.user_allergies = None

    def display_header(self):
        #Display the app header and description
        # col1, col2 = st.columns([0.1,0.9])
        # with col1:
        #     st.image("icon.png", use_column_width=True)
        # with col2:
        st.title("🧑🏻‍⚕️HealBot")
        st.markdown("""
        Hi! I'm Dr. AI, your friendly AI doctor. I can communicate in many languages. I'm here to:
        * Chat about your health concerns
        * Help understand your symptoms
        * Suggest over-the-counter remedies
        * Guide you on when to see a doctor
        
        **Note:** I'm an AI assistant here to help, but not to replace your regular doctor.
        """)

    def display_disclaimer(self):
        """Display medical disclaimer"""
        st.text("")
        st.text("")
        with st.expander("📋 Important Note", expanded=True):
            st.warning("""
            Hi there! While I'm here to help and provide information, please remember that 
            I'm an AI assistant, not a real doctor. Any advice or suggestions I provide 
            should be discussed with your healthcare provider before taking action.
            
            If you're experiencing a medical emergency, please contact emergency services 
            immediately.
            """)

    def get_user_info(self):
        """Get user information if not already provided"""
        if not st.session_state.user_name:
            with st.form("user_info_form"):
                st.markdown("### 👋 Welcome! Let's get to know each other")
                
                name = st.text_input("What should I call you?")
                
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("Age (years)", min_value=0, max_value=120)
                with col2:
                    sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
                
                col3, col4 = st.columns(2)
                with col3:
                    height = st.number_input("Height (cm)", min_value=0, max_value=300, value=None)
                with col4:
                    weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=None)
                
                allergies = st.text_area(
                    "Please list any medicine or food allergies (if none, write 'None')",
                    placeholder="Enter allergies here..."
                )
                
                submit = st.form_submit_button("Start Chat")
                
                if submit and name and age and sex and height and weight and allergies:
                    st.session_state.user_name = name
                    st.session_state.user_age = age
                    st.session_state.user_sex = sex
                    st.session_state.user_height = height
                    st.session_state.user_weight = weight
                    st.session_state.user_allergies = allergies
                    return True
                elif submit:
                    st.error("Please fill in all fields")
                return False
            return False
        return True
    
    def create_message_container(self, role: str, content: str):
        """Create a styled message container for chat messages"""
        if role == "user":
            with st.container():
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                        <div style="background-color: #034f01; padding: 0.75rem; border-radius: 15px; max-width: 80%;">
                            <p style="margin: 0; color: #ededed;">🧑🏻 {content}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            with st.container():
                st.markdown(
                    f"""
                    <div style="display: flex; margin: 1rem 0;">
                        <div style="background-color: #021617; padding: 0.75rem; border-radius: 15px; max-width: 80%; color: #00e5ff;">
                            <p style="margin: 0;">🧑🏻‍⚕️ {content}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    def display_chat_interface(self):
        """Display the enhanced chat interface using Streamlit chat input"""
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.conversation_history:
                self.create_message_container(message["role"], message["content"])

        # Input Method Selection (Text/Voice)
        method=st.sidebar.radio("Select Input Method", ["Text", "Voice"], horizontal=True, index=0)
        if method == "Text":
            user_input = st.chat_input(
                placeholder="Describe your symptoms or ask any health-related questions...",
                key="chat_input"
            )
        else:
            if st.button("Start Voice Input", type='primary'):
                st.write("Listening... Speak now!")
                user_input, error = get_voice_input()
                if error:
                    st.error(error)
                else:
                    st.write(f"You said: {user_input}")
            else:
                user_input = None
        
        if user_input:
            # Add user message to history
            st.session_state.conversation_history.append(
                {"role": "user", "content": user_input}
            )
            
            # Prepare user info for AI
            user_info = {
                "name": st.session_state.user_name,
                "age": st.session_state.user_age,
                "sex": st.session_state.user_sex,
                "height": st.session_state.user_height,
                "weight": st.session_state.user_weight,
                "allergies": st.session_state.user_allergies
            }
            
            # Get AI response
            ai_response = self.ai_doctor.get_response(
                st.session_state.conversation_history,
                user_info)
            
            # Add AI response to history
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": ai_response}
            )
            
            # Add button for speech output
            if st.button("Hear Spoken Output"):
                st.write("Speaking...")
                speak_text(ai_response)

            # Rerun to refresh the chat interface
            st.rerun()

        # Add the "Hear Spoken Output" button if there's an AI response
        if st.session_state.conversation_history and st.session_state.conversation_history[-1]["role"] == "assistant":
            ai_response = st.session_state.conversation_history[-1]["content"]
            if st.button("Hear Spoken Output"):
                st.write("Speaking...")
                speak_text(ai_response)

    def create_pdf_report(self, conversation_text: str) -> bytes:
        """Create a PDF report of the chat history"""
        class PDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'BU', 20)
                self.cell(0, 10, 'AI Doctor Consultation Report', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                self.set_y(self.get_y() + 10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Times', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, align='C')

        pdf = PDF()
        pdf.add_font('NotoSans', '', 'fonts/NotoSans-Regular.ttf')#, uni=True)
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Add patient information
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Patient Information:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', 'I', 11)
        pdf.cell(0, 10, f"Name: {st.session_state.user_name}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Age: {st.session_state.user_age} years", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Sex: {st.session_state.user_sex}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Height: {st.session_state.user_height} cm", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Weight: {st.session_state.user_weight} kg", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Allergies: {st.session_state.user_allergies}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Add conversation
        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font('NotoSans', '', 12)
        pdf.cell(0, 10, 'Consultation History:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('NotoSans', '', 11)

        pdf.set_fill_color(245, 245, 245)
        for line in conversation_text.split('\n'):
            if line.strip():
                if line.startswith('You:'):
                    pdf.set_text_color(0, 100, 0)
                else:
                    pdf.set_text_color(0, 0, 139)
                
                pdf.multi_cell(0, 10, line, fill=True)
                pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font('Times', 'BI', 10)
        pdf.multi_cell(0, 10, 'Note: This is an AI-generated consultation report and should not replace professional medical advice. Please consult with a healthcare provider for proper medical diagnosis and treatment.')

        return bytes(pdf.output())

    def add_sidebar_features(self):
            """Add sidebar features with enhanced styling"""
            with st.sidebar:
                st.header("🗒️ Patient Info:")
                
                # User information
                if st.session_state.user_name:
                    st.markdown(f"""
                        <div style='background-color: #00162b; padding: 1rem; border-radius: 10px;'>
                            <p style='margin: 0;'>👤 <strong>Patient:</strong> {st.session_state.user_name}</p>
                            <p style='margin: 0;'>📅 <strong>Age:</strong> {st.session_state.user_age} years</p>
                            <p style='margin: 0;'>⚧ <strong>Sex:</strong> {st.session_state.user_sex}</p>
                            <p style='margin: 0;'>📏 <strong>Height:</strong> {st.session_state.user_height} cm</p>
                            <p style='margin: 0;'>⚖️ <strong>Weight:</strong> {st.session_state.user_weight} kg</p>
                            <p style='margin: 0;'>⚠️ <strong>Allergies:</strong> {st.session_state.user_allergies}</p>
                            <p style='margin: 0;'>🕒 <strong>Started:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        </div>
                    """, unsafe_allow_html=True)

                # st.markdown("---")
                st.header("💬 Chat Controls")
                # Chat control buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 New Chat", type="primary", use_container_width=True):
                        st.session_state.conversation_history = []
                        st.rerun()
                with col2:
                    if st.button("👋 New Consultation", use_container_width=True):
                        st.session_state.conversation_history = []
                        st.session_state.user_name = None
                        st.rerun()

                # Export feature
                if st.session_state.conversation_history:
                    # st.markdown("---")
                    st.header("📥 Save Your Chat")
                    
                    # Format conversation for PDF
                    conversation_text = "\n".join([
                        f"{'You' if msg['role'] == 'user' else 'Dr. AI'}: {msg['content']}" 
                        for msg in st.session_state.conversation_history
                    ])
                    
                    # Generate PDF
                    pdf_bytes = self.create_pdf_report(conversation_text)
                    
                    # Create download button
                    st.download_button(
                        label="Download Consultation Report (PDF)",
                        data=pdf_bytes,
                        file_name=f"ai_doctor_consultation_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    def run(self):
        """Run the Streamlit app"""
        self.initialize_session_state()
        col1, col2 = st.columns(2)
        with col1:
            self.display_header()
        with col2:
            self.display_disclaimer()
        
        if self.get_user_info():
            self.add_sidebar_features()
            self.display_chat_interface()

def main():
    # Set page config
    st.set_page_config(
        page_title="AI Doctor Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stTextArea textarea {
            border-radius: 10px;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        
        .stButton button {
            border-radius: 20px;
        }
        
        .stMarkdown {
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Run the app
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()





# import streamlit as st
# from datetime import datetime
# from fpdf import FPDF
# from fpdf.enums import XPos, YPos
# from process import AIDoctor

# class StreamlitApp:
#     def __init__(self):
#         self.ai_doctor = AIDoctor()
        
#     def initialize_session_state(self):
#         """Initialize session state variables"""
#         if 'conversation_history' not in st.session_state:
#             st.session_state.conversation_history = []
#         if 'user_name' not in st.session_state:
#             st.session_state.user_name = None
#         if 'user_age' not in st.session_state:
#             st.session_state.user_age = None
#         if 'user_sex' not in st.session_state:
#             st.session_state.user_sex = None
#         if 'user_height' not in st.session_state:
#             st.session_state.user_height = None
#         if 'user_weight' not in st.session_state:
#             st.session_state.user_weight = None
#         if 'user_allergies' not in st.session_state:
#             st.session_state.user_allergies = None

#     def display_header(self):
#         """Display the app header and description"""
#         st.title("🏥 HealBot")
#         st.markdown("""
#         Hi! I'm Dr. AI, your friendly AI doctor. I can communicate in many languages. I'm here to:
#         * Chat about your health concerns
#         * Help understand your symptoms
#         * Suggest over-the-counter remedies
#         * Guide you on when to see a doctor
        
#         **Note:** I'm an AI assistant here to help, but not to replace your regular doctor.
#         """)

#     def display_disclaimer(self):
#         """Display medical disclaimer"""
#         st.text("")
#         st.text("")
#         with st.expander("📋 Important Note", expanded=True):
#             st.warning("""
#             Hi there! While I'm here to help and provide information, please remember that 
#             I'm an AI assistant, not a real doctor. Any advice or suggestions I provide 
#             should be discussed with your healthcare provider before taking action.
            
#             If you're experiencing a medical emergency, please contact emergency services 
#             immediately.
#             """)

#     def get_user_info(self):
#         """Get user information if not already provided"""
#         if not st.session_state.user_name:
#             with st.form("user_info_form"):
#                 st.markdown("### 👋 Welcome! Let's get to know each other")
                
#                 name = st.text_input("What should I call you?")
                
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     age = st.number_input("Age (years)", min_value=0, max_value=120)
#                 with col2:
#                     sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
                
#                 col3, col4 = st.columns(2)
#                 with col3:
#                     height = st.number_input("Height (cm)", min_value=0, max_value=300, value=None)
#                 with col4:
#                     weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=None)
                
#                 allergies = st.text_area(
#                     "Please list any medicine or food allergies (if none, write 'None')",
#                     placeholder="Enter allergies here..."
#                 )
                
#                 submit = st.form_submit_button("Start Chat")
                
#                 if submit and name and age and sex and height and weight and allergies:
#                     st.session_state.user_name = name
#                     st.session_state.user_age = age
#                     st.session_state.user_sex = sex
#                     st.session_state.user_height = height
#                     st.session_state.user_weight = weight
#                     st.session_state.user_allergies = allergies
#                     return True
#                 elif submit:
#                     st.error("Please fill in all fields")
#                 return False
#             return False
#         return True
    
#     def create_message_container(self, role: str, content: str):
#         """Create a styled message container for chat messages"""
#         if role == "user":
#             with st.container():
#                 st.markdown(
#                     f"""
#                     <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
#                         <div style="background-color: #034f01; padding: 0.75rem; border-radius: 15px; max-width: 80%;">
#                             <p style="margin: 0; color: #ededed;">🧑🏻 {content}</p>
#                         </div>
#                     </div>
#                     """,
#                     unsafe_allow_html=True
#                 )
#         else:
#             with st.container():
#                 st.markdown(
#                     f"""
#                     <div style="display: flex; margin: 1rem 0;">
#                         <div style="background-color: #021617; padding: 0.75rem; border-radius: 15px; max-width: 80%; color: #00e5ff;">
#                             <p style="margin: 0;">🧑🏻‍⚕️ {content}</p>
#                         </div>
#                     </div>
#                     """,
#                     unsafe_allow_html=True
#                 )

#     def display_chat_interface(self):
#         """Display the enhanced chat interface using Streamlit chat input"""
#         chat_container = st.container()
        
#         with chat_container:
#             for message in st.session_state.conversation_history:
#                 self.create_message_container(message["role"], message["content"])

#         # Use Streamlit's chat input instead of form
#         user_input = st.chat_input(
#             placeholder="Describe your symptoms or ask any health-related questions...",
#             key="chat_input"
#         )
        
#         if user_input:
#             # Add user message to history
#             st.session_state.conversation_history.append(
#                 {"role": "user", "content": user_input}
#             )
            
#             # Prepare user info for AI
#             user_info = {
#                 "name": st.session_state.user_name,
#                 "age": st.session_state.user_age,
#                 "sex": st.session_state.user_sex,
#                 "height": st.session_state.user_height,
#                 "weight": st.session_state.user_weight,
#                 "allergies": st.session_state.user_allergies
#             }
            
#             # Get AI response
#             ai_response = self.ai_doctor.get_response(
#                 st.session_state.conversation_history,
#                 user_info)
            
#             # Add AI response to history
#             st.session_state.conversation_history.append(
#                 {"role": "assistant", "content": ai_response}
#             )
            
#             # Rerun to refresh the chat interface
#             st.rerun()

#     def create_pdf_report(self, conversation_text: str) -> bytes:
#         """Create a PDF report of the chat history"""
#         class PDF(FPDF):
#             def header(self):
#                 self.set_font('Helvetica', 'BU', 20)
#                 self.cell(0, 10, 'AI Doctor Consultation Report', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
#                 self.set_y(self.get_y() + 10)

#             def footer(self):
#                 self.set_y(-15)
#                 self.set_font('Times', 'I', 8)
#                 self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, align='C')

#         pdf = PDF()
#         pdf.add_font('NotoSans', '', 'fonts/NotoSans-Regular.ttf')#, uni=True)
#         pdf.alias_nb_pages()
#         pdf.add_page()
        
#         # Add patient information
#         pdf.set_font('Helvetica', 'B', 12)
#         pdf.cell(0, 10, 'Patient Information:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.set_font('Helvetica', 'I', 11)
#         pdf.cell(0, 10, f"Name: {st.session_state.user_name}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.cell(0, 10, f"Age: {st.session_state.user_age} years", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.cell(0, 10, f"Sex: {st.session_state.user_sex}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.cell(0, 10, f"Height: {st.session_state.user_height} cm", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.cell(0, 10, f"Weight: {st.session_state.user_weight} kg", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.cell(0, 10, f"Allergies: {st.session_state.user_allergies}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
#         # Add conversation
#         pdf.set_y(pdf.get_y() + 10)
#         pdf.set_font('NotoSans', '', 12)
#         pdf.cell(0, 10, 'Consultation History:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         pdf.set_font('NotoSans', '', 11)

#         pdf.set_fill_color(245, 245, 245)
#         for line in conversation_text.split('\n'):
#             if line.strip():
#                 if line.startswith('You:'):
#                     pdf.set_text_color(0, 100, 0)
#                 else:
#                     pdf.set_text_color(0, 0, 139)
                
#                 pdf.multi_cell(0, 10, line, fill=True)
#                 pdf.ln(5)
        
#         pdf.set_text_color(0, 0, 0)
#         pdf.set_y(pdf.get_y() + 10)
#         pdf.set_font('Times', 'BI', 10)
#         pdf.multi_cell(0, 10, 'Note: This is an AI-generated consultation report and should not replace professional medical advice. Please consult with a healthcare provider for proper medical diagnosis and treatment.')

#         return bytes(pdf.output())

#     def add_sidebar_features(self):
#             """Add sidebar features with enhanced styling"""
#             with st.sidebar:
#                 st.header("🗒️ Patient Info:")
                
#                 # User information
#                 if st.session_state.user_name:
#                     st.markdown(f"""
#                         <div style='background-color: #00162b; padding: 1rem; border-radius: 10px;'>
#                             <p style='margin: 0;'>👤 <strong>Patient:</strong> {st.session_state.user_name}</p>
#                             <p style='margin: 0;'>📅 <strong>Age:</strong> {st.session_state.user_age} years</p>
#                             <p style='margin: 0;'>⚧ <strong>Sex:</strong> {st.session_state.user_sex}</p>
#                             <p style='margin: 0;'>📏 <strong>Height:</strong> {st.session_state.user_height} cm</p>
#                             <p style='margin: 0;'>⚖️ <strong>Weight:</strong> {st.session_state.user_weight} kg</p>
#                             <p style='margin: 0;'>⚠️ <strong>Allergies:</strong> {st.session_state.user_allergies}</p>
#                             <p style='margin: 0;'>🕒 <strong>Started:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
#                         </div>
#                     """, unsafe_allow_html=True)

#                 # st.markdown("---")
#                 st.header("💬 Chat Controls")
#                 # Chat control buttons
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     if st.button("🔄 New Chat", type="primary", use_container_width=True):
#                         st.session_state.conversation_history = []
#                         st.rerun()
#                 with col2:
#                     if st.button("👋 New Consultation", use_container_width=True):
#                         st.session_state.conversation_history = []
#                         st.session_state.user_name = None
#                         st.rerun()

#                 # Export feature
#                 if st.session_state.conversation_history:
#                     # st.markdown("---")
#                     st.header("📥 Save Your Chat")
                    
#                     # Format conversation for PDF
#                     conversation_text = "\n".join([
#                         f"{'You' if msg['role'] == 'user' else 'Dr. AI'}: {msg['content']}" 
#                         for msg in st.session_state.conversation_history
#                     ])
                    
#                     # Generate PDF
#                     pdf_bytes = self.create_pdf_report(conversation_text)
                    
#                     # Create download button
#                     st.download_button(
#                         label="Download Consultation Report (PDF)",
#                         data=pdf_bytes,
#                         file_name=f"ai_doctor_consultation_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
#                         mime="application/pdf",
#                         use_container_width=True
#                     )

#     def run(self):
#         """Run the Streamlit app"""
#         self.initialize_session_state()
#         col1, col2 = st.columns(2)
#         with col1:
#             self.display_header()
#         with col2:
#             self.display_disclaimer()
        
#         if self.get_user_info():
#             self.add_sidebar_features()
#             self.display_chat_interface()

# def main():
#     # Set page config
#     st.set_page_config(
#         page_title="AI Doctor Assistant",
#         page_icon="🏥",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
    
#     # Add custom CSS
#     st.markdown("""
#         <style>
#         .stTextArea textarea {
#             border-radius: 10px;
#         }
        
#         .main .block-container {
#             padding-top: 2rem;
#             padding-bottom: 3rem;
#             padding-left: 5rem;
#             padding-right: 5rem;
#         }
        
#         .stButton button {
#             border-radius: 20px;
#         }
        
#         .stMarkdown {
#             line-height: 1.6;
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     # Run the app
#     app = StreamlitApp()
#     app.run()

# if __name__ == "__main__":
#     main()
