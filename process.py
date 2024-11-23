import groq
from typing import Dict, List
import os
import streamlit as st
# from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import io
import wave

# Load environment variables from .env file
# load_dotenv()

def speak_text(text: str):
    """Convert text to speech and play it."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Adjust speech rate
        engine.setProperty('volume', 1.0)  # Adjust volume (0.0 to 1.0)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speech synthesis: {e}")

def process_audio_input(audio_bytes):
    """Process audio bytes from Streamlit's microphone input"""
    try:
        # Convert audio bytes to wav format for speech recognition
        audio_segment = io.BytesIO(audio_bytes)
        
        # Initialize recognizer
        r = sr.Recognizer()
        
        # Convert to AudioFile
        with sr.AudioFile(audio_segment) as source:
            audio_data = r.record(source)
            
        # Perform speech recognition
        text = r.recognize_google(audio_data)
        return text
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

# def get_voice_input():
#     r = sr.Recognizer()
#     with sr.Microphone(device_index=pa.get_default_input_device()) as source:
#         audio = r.listen(source)
#     try:
#         text = r.recognize_google(audio)
#         return text, None
#     except sr.UnknownValueError:
#         return None, "Sorry, I couldn't understand that. Please try again."
#     except sr.RequestError:
#         return None, "Sorry, there was an error processing your request. Please try again later."

class AIDoctor:
    def __init__(self):
        # Check if API key is available
        api_key = st.secrets['GROQ_API_KEY']
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please make sure it's set in your .env file"
            )
        
        # Initialize Groq client
        self.client = groq.Groq(api_key=api_key)
        

        # Enhanced system prompt for more conversational interactions
        self.system_prompt = """You are a friendly and empathetic AI Medical Assistant named Dr. AI. Your communication style should be:
                1. Warm and conversational, like a caring doctor
                2. Clear and easy to understand, avoiding complex medical jargon
                3. Patient and thorough in your explanations
                4. Empathetic to the patient's concerns
                5. Able to communicate clearly in multiple Indian languages

                You will receive the patient's complete profile including:
                - Name (use it occasionally to make the conversation personal)
                - Age (consider age-specific health concerns and medication dosages)
                - Sex (consider sex-specific health conditions and symptoms)
                - Height and Weight (use to assess BMI and related health factors)
                - Allergies (ALWAYS check against these when suggesting medications)

                Your role is to:
                1. Start with a friendly greeting and ask about their symptoms
                2. Consider the patient's complete profile when assessing their concerns
                3. Ask relevant follow-up questions in a conversational way
                4. Calculate and consider BMI when relevant to the consultation
                5. Provide preliminary assessments in clear, simple language
                6. Offer practical health advice and lifestyle recommendations
                7. ALWAYS cross-reference any medication suggestions with their listed allergies

                When suggesting medications:
                - Focus on common, easily available over-the-counter options
                - FIRST check against the patient's listed allergies
                - Explain potential allergies and interactions in simple terms
                - Always remind about reading medication labels
                - Adjust dosage recommendations based on age and weight when relevant
                - Provide alternative options when available

                Remember to:
                - Use the patient's name in responses occasionally
                - Show understanding and empathy for their symptoms
                - Reference their age and other relevant health factors when giving advice
                - Consider sex-specific health concerns when relevant
                - Maintain continuity by referencing previous parts of the conversation
                - Ask one clear follow-up question at a time
                - End your responses with encouragement or support
                - Be extra cautious with medication recommendations for:
                * Children and elderly patients
                * Patients with multiple allergies
                * Patients with extreme BMI values

                Important: Always include a friendly reminder that you are an AI assistant and not a 
                replacement for professional medical advice. For any serious concerns, warmly recommend 
                consulting with a healthcare provider."""

    def get_response(self, conversation_history: List[Dict[str, str]], user_info: Dict[str, str]) -> str:
        try:
            # Prepare the messages for the API call
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add user's information to the context
            user_context = {
                "role": "system", 
                "content": f"""The patient's information:
                - Name: {user_info['name']}
                - Age: {user_info['age']} years
                - Sex: {user_info['sex']}
                - Height: {user_info['height']} cm
                - Weight: {user_info['weight']} kg
                - Allergies: {user_info['allergies']}
                
                Please consider this information when providing medical advice and watch for any allergy concerns."""
            }
            messages.append(user_context)
            
            # Add the entire conversation history
            messages.extend(conversation_history)
            
            # Make the API call to Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.2-11b-vision-preview",
                temperature=0.7,
                max_tokens=1024,
                top_p=0.95,
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"








# import groq
# import streamlit as st
# from typing import Dict, List
# import os
# # from dotenv import load_dotenv

# # Load environment variables from .env file
# # load_dotenv()

# class AIDoctor:
#     def __init__(self):
#         # Check if API key is available
#         api_key = st.secrets["GROQ_API_KEY"]
#         if not api_key:
#             raise ValueError(
#                 "GROQ_API_KEY not found. Please make sure it's set in your .env file"
#             )
        
#         # Initialize Groq client
#         self.client = groq.Groq(api_key=api_key)
        

#         # Enhanced system prompt for more conversational interactions
#         self.system_prompt = """You are a friendly and empathetic AI Medical Assistant named Dr. AI. Your communication style should be:
#                 1. Warm and conversational, like a caring doctor
#                 2. Clear and easy to understand, avoiding complex medical jargon
#                 3. Patient and thorough in your explanations
#                 4. Empathetic to the patient's concerns
#                 5. Able to communicate clearly in multiple Indian languages

#                 You will receive the patient's complete profile including:
#                 - Name (use it occasionally to make the conversation personal)
#                 - Age (consider age-specific health concerns and medication dosages)
#                 - Sex (consider sex-specific health conditions and symptoms)
#                 - Height and Weight (use to assess BMI and related health factors)
#                 - Allergies (ALWAYS check against these when suggesting medications)

#                 Your role is to:
#                 1. Start with a friendly greeting and ask about their symptoms
#                 2. Consider the patient's complete profile when assessing their concerns
#                 3. Ask relevant follow-up questions in a conversational way
#                 4. Calculate and consider BMI when relevant to the consultation
#                 5. Provide preliminary assessments in clear, simple language
#                 6. Offer practical health advice and lifestyle recommendations
#                 7. ALWAYS cross-reference any medication suggestions with their listed allergies

#                 When suggesting medications:
#                 - Focus on common, easily available over-the-counter options
#                 - FIRST check against the patient's listed allergies
#                 - Explain potential allergies and interactions in simple terms
#                 - Always remind about reading medication labels
#                 - Adjust dosage recommendations based on age and weight when relevant
#                 - Provide alternative options when available

#                 Remember to:
#                 - Use the patient's name in responses occasionally
#                 - Show understanding and empathy for their symptoms
#                 - Reference their age and other relevant health factors when giving advice
#                 - Consider sex-specific health concerns when relevant
#                 - Maintain continuity by referencing previous parts of the conversation
#                 - Ask one clear follow-up question at a time
#                 - End your responses with encouragement or support
#                 - Be extra cautious with medication recommendations for:
#                 * Children and elderly patients
#                 * Patients with multiple allergies
#                 * Patients with extreme BMI values

#                 Important: Always include a friendly reminder that you are an AI assistant and not a 
#                 replacement for professional medical advice. For any serious concerns, warmly recommend 
#                 consulting with a healthcare provider."""

#     def get_response(self, conversation_history: List[Dict[str, str]], user_info: Dict[str, str]) -> str:
#         try:
#             # Prepare the messages for the API call
#             messages = [{"role": "system", "content": self.system_prompt}]
            
#             # Add user's information to the context
#             user_context = {
#                 "role": "system", 
#                 "content": f"""The patient's information:
#                 - Name: {user_info['name']}
#                 - Age: {user_info['age']} years
#                 - Sex: {user_info['sex']}
#                 - Height: {user_info['height']} cm
#                 - Weight: {user_info['weight']} kg
#                 - Allergies: {user_info['allergies']}
                
#                 Please consider this information when providing medical advice and watch for any allergy concerns."""
#             }
#             messages.append(user_context)
            
#             # Add the entire conversation history
#             messages.extend(conversation_history)
            
#             # Make the API call to Groq
#             chat_completion = self.client.chat.completions.create(
#                 messages=messages,
#                 model="llama-3.2-11b-vision-preview",
#                 temperature=0.7,
#                 max_tokens=1024,
#                 top_p=0.95,
#             )
            
#             return chat_completion.choices[0].message.content
        
#         except Exception as e:
#             return f"Error: {str(e)}"
