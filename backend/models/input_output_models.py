from typing import List, Dict
from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    user_id: str
    deficiencies: Dict[str, str]

class FoodSuggestion(BaseModel):
    foods: List[str]
    recipes: List[Dict[str, str]]  # title, ingredients, url

class FullRecommendationResponse(BaseModel):
    user_id: str
    recommendations: Dict[str, FoodSuggestion]
