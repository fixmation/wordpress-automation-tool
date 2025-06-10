import os
import google.generativeai as genai

def apply_sqlite_migrations(engine, model, migrations_path):
    """Apply SQLite migrations to the database"""
    # Ensure the migrations directory exists
    real_path = os.path.join(os.path.dirname(__file__), migrations_path)
    if not os.path.exists(real_path):
        print(f"Migrations directory {real_path} does not exist")
        return

    migrations_path = real_path  # Use the adjusted path

def upload_file_to_storage(file, storage_path):
    # Placeholder function
    pass

def url_for_uploaded_file(file_id):
    """
    Generate a URL for the uploaded file using its file_id.
    """
    return f"/uploads/{file_id}"

def list_available_models():
    """
    List available models for Gemini API
    """
    try:
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            return {"error": "Please add your Gemini API key in the Secrets tab with the name 'GEMINI_API_KEY'"}

        genai.configure(api_key=GEMINI_API_KEY)

        # Get list of available models
        models = genai.list_models()
        available_models = [model.name for model in models if "generateContent" in model.supported_generation_methods]
        return {"available_models": available_models}
    except Exception as e:
        return {"error": str(e)}

def llm(message, temperature=0.7):
    """
    Use Google Gemini to generate AI responses
    """
    try:
        # Configure Gemini API
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            return {"response": "Please add your Gemini API key in the Secrets tab with the name 'GEMINI_API_KEY'"}

        genai.configure(api_key=GEMINI_API_KEY)

        # Use the correct model configuration
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]

        generation_config = {
            "temperature": temperature,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # First try to get available models
        try:
            models_info = list_available_models()
            available_models = models_info.get("available_models", [])

            # Select a model that's available, prioritizing gemini-1.5-flash
            model_name = None
            for model_candidate in ["gemini-1.5-flash", "gemini-1.5-pro", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]:
                if model_candidate in available_models:
                    model_name = model_candidate
                    break

            # If no recognized model is available, use the first available model
            if not model_name and available_models:
                model_name = available_models[0]

            # If still no model, fall back to gemini-1.5-flash but it may fail
            if not model_name:
                model_name = "gemini-1.5-flash"

            # Initialize the model with the selected name
            model = genai.GenerativeModel(model_name,
                                        safety_settings=safety_settings,
                                        generation_config=generation_config)
        except Exception as model_error:
            # If listing models fails, try with the default model
            model = genai.GenerativeModel("gemini-pro",
                                        safety_settings=safety_settings,
                                        generation_config=generation_config)

        # Add instruction to make replies conversational, include links, and avoid repetitive phrases
        enhanced_message = message + """

Your responses should be:
1. Conversational and human-like - Use a friendly, casual tone with natural language patterns and contractions
2. Free from repetitive greetings - DO NOT begin responses with "Hey there!" or any similar repetitive greeting pattern
3. Include relevant links from the application when appropriate:
   - For pricing information: /generate_content
   - For tutorials: /tutorials
   - For documentation: /documentation
   - For WordPress installation: /wordpress_installation
   - For case studies: /case_studies
   - For contact page: /contact
   - For blog content: /blog
   - For optimization tips: /optimization

Format any links as Markdown: [link text](URL)
Vary your opening words and sentence structure. Begin with diverse starters like 'Absolutely', 'Certainly', 'I'd be happy to help', 'Great question', etc.
"""

        # Generate response with better error handling
        response = model.generate_content(enhanced_message)
        if response and hasattr(response, 'text'):
            # Process response to ensure URLs are properly formatted
            response_text = response.text

            # Ensure all app links use proper format
            response_text = response_text.replace("[insert link to pricing page]", "[our pricing page](/generate_content)")

            return {"response": response_text}
        else:
            return {"response": "Unable to generate a response. Please try again."}

    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return {"response": "The API quota has been exceeded. Please check your Google Cloud billing settings."}
        elif "permission" in error_msg.lower() or "403" in error_msg:
            return {"response": "Access denied. Please make sure you have enabled the Gemini API in your Google Cloud project."}
        elif "invalid" in error_msg.lower():
            return {"response": "Invalid API key. Please check if your API key is correct in the Secrets tab."}
        else:
            return {"response": f"Connection error: {error_msg}. Please ensure the Gemini API is enabled in your Google Cloud project."}