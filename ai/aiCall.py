# ai_call.py
import json
import requests

def ai_call(state: str, prompt: str, model: str = "gemma3") -> str:
    full_prompt = f"{prompt.strip()}\n\nState:\n{state.strip()}\n\nAI:"
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': full_prompt,
                'stream': False
            }
        )
        response.raise_for_status()
        data = response.json()
        # print(f"AI call successful: {data}")
        return data.get('response', 'No response from AI.').strip()
    
    except requests.exceptions.RequestException as e:
        print(f"AI call failed: {e}")
        return "Error: Failed to get response from AI."

