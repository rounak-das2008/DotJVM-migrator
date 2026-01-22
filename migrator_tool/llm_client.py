import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import os
from typing import Optional

class LLMClient:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        # Initialize Vertex AI. If project_id is None, it infers from environment/ADC.
        vertexai.init(project=project_id, location=location)
        
    def generate(self, prompt: str, system_instruction: str = "", model_name: str = "gemini-2.5-pro") -> str:
        model = GenerativeModel(
            model_name=model_name,
            system_instruction=[system_instruction] if system_instruction else None
        )
        
        # Aggressive safety settings to prevent blocking code generation
        safety_settings = [
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
        ]

        response = model.generate_content(
            prompt,
            safety_settings=safety_settings,
        )
        
        return response.text
