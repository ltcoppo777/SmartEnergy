from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip('"')
    genai.configure(api_key=GEMINI_API_KEY)

class ConversationMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"
    history: List[ConversationMessage] = []

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    conversation_id: str

def extract_response_and_suggestions(text: str):
    try:
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_str = text[start:end].strip()
        else:
            json_str = text.strip()
        
        data = json.loads(json_str)
        response = data.get("response", text)
        suggestions = data.get("suggestions", [])
        return response, suggestions
    except (json.JSONDecodeError, ValueError):
        return text, []

@router.post("/chat")
async def chat(chat_req: ChatRequest):
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        if not chat_req.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        system_prompt = """You are an AI Energy Advisor specialized in electricity consumption optimization, energy scheduling, and smart home energy management. Help users understand electricity pricing, optimize appliance usage schedules, reduce energy costs, and maximize comfort.

Always respond with ONLY valid JSON in this exact format:
{"response": "Your helpful response here", "suggestions": ["Question 1", "Question 2", "Question 3"]}"""
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt
        )
        
        conversation_history = []
        for msg in chat_req.history:
            if msg.role == "user":
                conversation_history.append({
                    "role": "user",
                    "parts": [msg.content]
                })
            elif msg.role == "model":
                conversation_history.append({
                    "role": "model",
                    "parts": [msg.content]
                })
        
        conversation_history.append({
            "role": "user",
            "parts": [chat_req.message]
        })
        
        response = model.generate_content(
            conversation_history,
            stream=False
        )
        
        response_text = response.text
        response_content, suggestions = extract_response_and_suggestions(response_text)
        
        return ChatResponse(
            response=response_content,
            suggestions=suggestions,
            conversation_id=chat_req.conversation_id
        )
    except genai.types.BlockedPromptException:
        raise HTTPException(status_code=400, detail="Message was blocked by safety filters")
    except genai.types.StopCandidateException as e:
        raise HTTPException(status_code=400, detail=f"Generation stopped: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)} | {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Error: {error_detail}")
