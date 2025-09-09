import os
import openai
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
from dotenv import load_dotenv
import asyncio

load_dotenv()

class LLMResponse(BaseModel):
    content: str
    usage: Dict[str, int]
    model_used: str
    timestamp: str
    success: bool = True
    error: Optional[str] = None

class EnhancedLLMClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
    async def generate_completion(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: str = "text"
    ) -> LLMResponse:
        """Enhanced completion with error handling and flexibility"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add JSON format instruction if needed
            if response_format == "json":
                messages.append({
                    "role": "system", 
                    "content": "Respond with valid JSON only. No additional text or formatting."
                })
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            import pandas as pd
            return LLMResponse(
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model_used=self.model,
                timestamp=str(pd.Timestamp.now()),
                success=True
            )
            
        except Exception as e:
            import pandas as pd
            return LLMResponse(
                content="",
                usage={"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0},
                model_used=self.model,
                timestamp=str(pd.Timestamp.now()),
                success=False,
                error=str(e)
            )
    
    def generate_completion_sync(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: str = "text"
    ) -> LLMResponse:
        """Synchronous version"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            if response_format == "json":
                messages.append({
                    "role": "system", 
                    "content": "Respond with valid JSON only. No additional text or formatting."
                })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            import pandas as pd
            return LLMResponse(
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model_used=self.model,
                timestamp=str(pd.Timestamp.now()),
                success=True
            )
            
        except Exception as e:
            import pandas as pd
            return LLMResponse(
                content="",
                usage={"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0},
                model_used=self.model,
                timestamp=str(pd.Timestamp.now()),
                success=False,
                error=str(e)
            )
