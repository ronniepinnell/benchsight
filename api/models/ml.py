"""
ML Request/Response Models
Pydantic models for ML endpoints
"""
from pydantic import BaseModel
from typing import Optional, List


class PredictPlayerStatsRequest(BaseModel):
    player_id: str
    season_id: str
    games_remaining: Optional[int] = None


class PredictPlayerStatsResponse(BaseModel):
    player_id: str
    season_id: str
    games_remaining: int
    predicted_goals: float
    predicted_assists: float
    predicted_points: float
    predicted_war: float
    confidence: float
    model_version: str
    goals_lower_bound: float
    goals_upper_bound: float
    points_lower_bound: float
    points_upper_bound: float


class PredictGameOutcomeRequest(BaseModel):
    home_team_id: str
    away_team_id: str
    season_id: str
    game_date: Optional[str] = None


class PredictGameOutcomeResponse(BaseModel):
    home_team_id: str
    away_team_id: str
    home_win_probability: float
    away_win_probability: float
    predicted_home_goals: float
    predicted_away_goals: float
    predicted_total_goals: float
    over_under_line: float
    over_probability: float
    under_probability: float
    confidence: float
    key_factors: List[str]
    model_version: str
