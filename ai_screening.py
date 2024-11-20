import os
from openai import OpenAI
import json
import base64
from PIL import Image
from io import BytesIO

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def analyze_adhd_responses(responses):
    """Analyze ADHD screening responses using GPT-4"""
    try:
        prompt = (
            "Analyze these ADHD screening responses and provide an assessment. "
            "The response should include a risk level (low, medium, high) and "
            "detailed recommendations. Format the response as JSON."
        )
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a mental health screening expert. Analyze ADHD screening responses."
                },
                {
                    "role": "user", 
                    "content": f"{prompt}\n\nResponses: {json.dumps(responses)}"
                }
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Failed to analyze ADHD responses: {e}")

def analyze_skin_image(image_data):
    """Analyze skin condition from uploaded image using GPT-4 Vision"""
    try:
        # Convert PIL Image to base64
        buffered = BytesIO()
        image_data.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a dermatology screening expert. Analyze the skin condition in the image."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this skin image and provide an assessment of any visible skin conditions or concerns. Include risk level and recommendations."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Failed to analyze skin image: {e}")
