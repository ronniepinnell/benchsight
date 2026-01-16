"""
ML Prediction Endpoints
Real-time ML model inference for interactive predictions
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from ..services.ml_service import ml_service
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/ml", tags=["ml"])


# ============================================================================
# Request/Response Models
# ============================================================================

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


class FindSimilarPlayersRequest(BaseModel):
    player_id: str
    season_id: str
    limit: Optional[int] = 10
    min_similarity: Optional[float] = 70.0


class SimilarPlayer(BaseModel):
    player_id: str
    player_name: str
    similarity_score: float
    similar_stats: List[str]
    different_stats: List[str]


class FindSimilarPlayersResponse(BaseModel):
    player_id: str
    player_name: str
    similar_players: List[SimilarPlayer]
    model_version: str


class PredictLineChemistryRequest(BaseModel):
    player1_id: str
    player2_id: str
    player3_id: Optional[str] = None
    team_id: str
    season_id: str


class PredictLineChemistryResponse(BaseModel):
    chemistry_score: float
    offensive_chemistry: float
    defensive_chemistry: float
    transition_chemistry: float
    expected_goals_together: float
    expected_cf_pct_together: float
    optimal_strength: str
    optimal_game_state: str
    confidence: float
    model_version: str


class PredictNextGoalScorerRequest(BaseModel):
    game_id: int
    current_period: int
    time_remaining_seconds: int


class GoalScorerCandidate(BaseModel):
    player_id: str
    player_name: str
    probability: float
    team: str


class PredictNextGoalScorerResponse(BaseModel):
    game_id: int
    top_candidates: List[GoalScorerCandidate]
    expected_time_until_goal: float
    model_version: str


class PredictRealTimeWinProbabilityRequest(BaseModel):
    game_id: int
    current_score_home: int
    current_score_away: int
    current_period: int
    time_remaining_seconds: int
    power_play_status: Optional[str] = None


class PredictRealTimeWinProbabilityResponse(BaseModel):
    game_id: int
    home_win_probability: float
    away_win_probability: float
    next_goal_home_probability: float
    next_goal_away_probability: float
    momentum_score: float
    momentum_team: str
    comeback_probability: float
    model_version: str


# ============================================================================
# Player Prediction Endpoints
# ============================================================================

@router.post("/predict/player-stats", response_model=PredictPlayerStatsResponse)
async def predict_player_stats(request: PredictPlayerStatsRequest):
    """
    Predict player stats for remainder of season.
    
    Uses trained ML models to predict goals, assists, points, WAR, etc.
    """
    try:
        predictions = ml_service.predict_player_stats(
            player_id=request.player_id,
            season_id=request.season_id,
            games_remaining=request.games_remaining
        )
        return predictions
    except Exception as e:
        logger.error(f"Error predicting player stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/player-next-game", response_model=PredictPlayerStatsResponse)
async def predict_player_next_game(
    player_id: str = Query(..., description="Player ID"),
    opponent_team_id: Optional[str] = Query(None, description="Opponent team ID"),
    home_away: Optional[str] = Query(None, description="'Home' or 'Away'")
):
    """
    Predict player performance in next game.
    
    Returns predicted goals, assists, points, WAR for upcoming game.
    """
    try:
        predictions = ml_service.predict_player_next_game(
            player_id=player_id,
            opponent_team_id=opponent_team_id,
            home_away=home_away
        )
        return predictions
    except Exception as e:
        logger.error(f"Error predicting next game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Game Prediction Endpoints
# ============================================================================

@router.post("/predict/game-outcome", response_model=PredictGameOutcomeResponse)
async def predict_game_outcome(request: PredictGameOutcomeRequest):
    """
    Predict game winner and score.
    
    Returns win probabilities, predicted score, over/under, key factors.
    """
    try:
        prediction = ml_service.predict_game_outcome(
            home_team_id=request.home_team_id,
            away_team_id=request.away_team_id,
            season_id=request.season_id,
            game_date=request.game_date
        )
        return prediction
    except Exception as e:
        logger.error(f"Error predicting game outcome: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/real-time-win-probability", response_model=PredictRealTimeWinProbabilityResponse)
async def predict_real_time_win_probability(request: PredictRealTimeWinProbabilityRequest):
    """
    Predict win probability during live game.
    
    Updates win probability based on current game state.
    """
    try:
        prediction = ml_service.predict_real_time_win_probability(
            game_id=request.game_id,
            current_score_home=request.current_score_home,
            current_score_away=request.current_score_away,
            current_period=request.current_period,
            time_remaining_seconds=request.time_remaining_seconds,
            power_play_status=request.power_play_status
        )
        return prediction
    except Exception as e:
        logger.error(f"Error predicting real-time win probability: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/next-goal-scorer", response_model=PredictNextGoalScorerResponse)
async def predict_next_goal_scorer(request: PredictNextGoalScorerRequest):
    """
    Predict who will score the next goal.
    
    Returns top candidates with probabilities.
    """
    try:
        prediction = ml_service.predict_next_goal_scorer(
            game_id=request.game_id,
            current_period=request.current_period,
            time_remaining_seconds=request.time_remaining_seconds
        )
        return prediction
    except Exception as e:
        logger.error(f"Error predicting next goal scorer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Player Comparison Endpoints
# ============================================================================

@router.post("/find/similar-players", response_model=FindSimilarPlayersResponse)
async def find_similar_players(request: FindSimilarPlayersRequest):
    """
    Find players with similar play styles.
    
    Uses ML clustering/embeddings to find similar players.
    """
    try:
        similar_players = ml_service.find_similar_players(
            player_id=request.player_id,
            season_id=request.season_id,
            limit=request.limit,
            min_similarity=request.min_similarity
        )
        return similar_players
    except Exception as e:
        logger.error(f"Error finding similar players: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/player-value")
async def compare_player_value(
    player1_id: str = Query(..., description="First player ID"),
    player2_id: str = Query(..., description="Second player ID"),
    season_id: str = Query(..., description="Season ID")
):
    """
    Compare player value across metrics.
    
    Returns value scores, trade value, contract value.
    """
    try:
        comparison = ml_service.compare_player_value(
            player1_id=player1_id,
            player2_id=player2_id,
            season_id=season_id
        )
        return comparison
    except Exception as e:
        logger.error(f"Error comparing player value: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Line Chemistry Endpoints
# ============================================================================

@router.post("/predict/line-chemistry", response_model=PredictLineChemistryResponse)
async def predict_line_chemistry(request: PredictLineChemistryRequest):
    """
    Predict how well players work together on a line.
    
    Returns chemistry scores, expected performance, optimal deployment.
    """
    try:
        chemistry = ml_service.predict_line_chemistry(
            player1_id=request.player1_id,
            player2_id=request.player2_id,
            player3_id=request.player3_id,
            team_id=request.team_id,
            season_id=request.season_id
        )
        return chemistry
    except Exception as e:
        logger.error(f"Error predicting line chemistry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/lineup")
async def optimize_lineup(
    team_id: str = Query(..., description="Team ID"),
    season_id: str = Query(..., description="Season ID"),
    opponent_team_id: Optional[str] = Query(None, description="Opponent team ID"),
    game_state: Optional[str] = Query(None, description="'Leading', 'Trailing', 'Tied'")
):
    """
    Generate optimal line combinations.
    
    Returns best forward lines, defense pairs, PP units, PK units.
    """
    try:
        optimal_lineup = ml_service.optimize_lineup(
            team_id=team_id,
            season_id=season_id,
            opponent_team_id=opponent_team_id,
            game_state=game_state
        )
        return optimal_lineup
    except Exception as e:
        logger.error(f"Error optimizing lineup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Goalie Prediction Endpoints
# ============================================================================

@router.post("/predict/goalie-stats")
async def predict_goalie_stats(
    goalie_id: str = Query(..., description="Goalie player ID"),
    season_id: str = Query(..., description="Season ID"),
    opponent_team_id: Optional[str] = Query(None, description="Opponent team ID")
):
    """
    Predict goalie performance for next game/season.
    
    Returns predicted save %, GAA, shutout probability.
    """
    try:
        predictions = ml_service.predict_goalie_stats(
            goalie_id=goalie_id,
            season_id=season_id,
            opponent_team_id=opponent_team_id
        )
        return predictions
    except Exception as e:
        logger.error(f"Error predicting goalie stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Team Prediction Endpoints
# ============================================================================

@router.get("/predict/playoff-probability")
async def predict_playoff_probability(
    team_id: str = Query(..., description="Team ID"),
    season_id: str = Query(..., description="Season ID")
):
    """
    Predict playoff probability and seed.
    
    Returns playoff probability, seed probabilities, championship odds.
    """
    try:
        predictions = ml_service.predict_playoff_probability(
            team_id=team_id,
            season_id=season_id
        )
        return predictions
    except Exception as e:
        logger.error(f"Error predicting playoff probability: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Advanced Analytics Endpoints
# ============================================================================

@router.get("/detect/breakout-players")
async def detect_breakout_players(
    season_id: str = Query(..., description="Season ID"),
    min_probability: Optional[float] = Query(50.0, description="Minimum breakout probability"),
    limit: Optional[int] = Query(20, description="Number of results")
):
    """
    Detect players likely to break out.
    
    Returns players with high breakout probability.
    """
    try:
        breakout_players = ml_service.detect_breakout_players(
            season_id=season_id,
            min_probability=min_probability,
            limit=limit
        )
        return breakout_players
    except Exception as e:
        logger.error(f"Error detecting breakout players: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assess/injury-risk")
async def assess_injury_risk(
    player_id: str = Query(..., description="Player ID"),
    season_id: str = Query(..., description="Season ID")
):
    """
    Assess player injury risk.
    
    Returns injury risk score, risk factors, recommendations.
    """
    try:
        risk_assessment = ml_service.assess_injury_risk(
            player_id=player_id,
            season_id=season_id
        )
        return risk_assessment
    except Exception as e:
        logger.error(f"Error assessing injury risk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ml_health():
    """
    Health check for ML service.
    
    Returns model status, versions, availability.
    """
    try:
        health = ml_service.get_health()
        return health
    except Exception as e:
        logger.error(f"Error checking ML health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
