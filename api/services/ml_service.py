"""
ML Service
Handles ML model loading, inference, and predictions
"""
import os
import joblib
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class MLService:
    """Service for ML model inference and predictions."""
    
    def __init__(self):
        """Initialize ML service and load models."""
        self.model_dir = Path(__file__).parent.parent / "models"
        self.model_dir.mkdir(exist_ok=True)
        
        # Model versions
        self.model_version = os.getenv("ML_MODEL_VERSION", "1.0.0")
        
        # Load models (lazy loading - models loaded on first use)
        self._models = {}
        self._load_models()
    
    def _load_models(self):
        """Load all ML models."""
        try:
            # Player prediction models
            if (self.model_dir / "player_goals_model.pkl").exists():
                self._models["player_goals"] = joblib.load(self.model_dir / "player_goals_model.pkl")
            if (self.model_dir / "player_assists_model.pkl").exists():
                self._models["player_assists"] = joblib.load(self.model_dir / "player_assists_model.pkl")
            if (self.model_dir / "player_points_model.pkl").exists():
                self._models["player_points"] = joblib.load(self.model_dir / "player_points_model.pkl")
            if (self.model_dir / "player_war_model.pkl").exists():
                self._models["player_war"] = joblib.load(self.model_dir / "player_war_model.pkl")
            
            # Game outcome models
            if (self.model_dir / "game_outcome_model.pkl").exists():
                self._models["game_outcome"] = joblib.load(self.model_dir / "game_outcome_model.pkl")
            if (self.model_dir / "game_score_model.pkl").exists():
                self._models["game_score"] = joblib.load(self.model_dir / "game_score_model.pkl")
            
            # Similarity models
            if (self.model_dir / "player_similarity_model.pkl").exists():
                self._models["player_similarity"] = joblib.load(self.model_dir / "player_similarity_model.pkl")
            
            # Line chemistry models
            if (self.model_dir / "line_chemistry_model.pkl").exists():
                self._models["line_chemistry"] = joblib.load(self.model_dir / "line_chemistry_model.pkl")
            
            logger.info(f"Loaded {len(self._models)} ML models")
        except Exception as e:
            logger.warning(f"Error loading ML models: {e}. Some predictions may not be available.")
    
    def get_health(self) -> Dict[str, Any]:
        """Get ML service health status."""
        return {
            "status": "healthy" if len(self._models) > 0 else "degraded",
            "models_loaded": len(self._models),
            "model_version": self.model_version,
            "available_models": list(self._models.keys())
        }
    
    def predict_player_stats(
        self, 
        player_id: str, 
        season_id: str, 
        games_remaining: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Predict player stats for remainder of season.
        
        Args:
            player_id: Player ID
            season_id: Season ID
            games_remaining: Number of games remaining (if None, calculated)
        
        Returns:
            Dictionary with predictions
        """
        # TODO: Fetch player features from database
        # For now, return placeholder structure
        features = self._get_player_features(player_id, season_id)
        
        # Make predictions
        predicted_goals = self._predict_with_model("player_goals", features, default=20.0)
        predicted_assists = self._predict_with_model("player_assists", features, default=30.0)
        predicted_points = predicted_goals + predicted_assists
        predicted_war = self._predict_with_model("player_war", features, default=2.0)
        
        # Calculate confidence intervals (simplified)
        goals_lower = predicted_goals * 0.85
        goals_upper = predicted_goals * 1.15
        points_lower = predicted_points * 0.85
        points_upper = predicted_points * 1.15
        
        return {
            "player_id": player_id,
            "season_id": season_id,
            "games_remaining": games_remaining or 20,
            "predicted_goals": float(predicted_goals),
            "predicted_assists": float(predicted_assists),
            "predicted_points": float(predicted_points),
            "predicted_war": float(predicted_war),
            "confidence": 0.75,
            "model_version": self.model_version,
            "goals_lower_bound": float(goals_lower),
            "goals_upper_bound": float(goals_upper),
            "points_lower_bound": float(points_lower),
            "points_upper_bound": float(points_upper)
        }
    
    def predict_player_next_game(
        self,
        player_id: str,
        opponent_team_id: Optional[str] = None,
        home_away: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict player performance in next game."""
        # TODO: Implement next game prediction
        features = self._get_player_features(player_id, None)
        
        # Simplified prediction
        predicted_goals = self._predict_with_model("player_goals", features, default=0.3) / 20  # Per game
        predicted_assists = self._predict_with_model("player_assists", features, default=0.4) / 20
        predicted_points = predicted_goals + predicted_assists
        
        return {
            "player_id": player_id,
            "season_id": "current",
            "games_remaining": 1,
            "predicted_goals": float(predicted_goals),
            "predicted_assists": float(predicted_assists),
            "predicted_points": float(predicted_points),
            "predicted_war": float(predicted_points * 0.1),
            "confidence": 0.65,
            "model_version": self.model_version,
            "goals_lower_bound": float(predicted_goals * 0.5),
            "goals_upper_bound": float(predicted_goals * 1.5),
            "points_lower_bound": float(predicted_points * 0.5),
            "points_upper_bound": float(predicted_points * 1.5)
        }
    
    def predict_game_outcome(
        self,
        home_team_id: str,
        away_team_id: str,
        season_id: str,
        game_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict game winner and score."""
        # TODO: Fetch team features from database
        features = self._get_team_features(home_team_id, away_team_id, season_id)
        
        # Predict outcome
        home_win_prob = self._predict_with_model("game_outcome", features, default=0.55)
        away_win_prob = 1.0 - home_win_prob
        
        # Predict score
        predicted_home_goals = self._predict_with_model("game_score", features, default=3.2)
        predicted_away_goals = self._predict_with_model("game_score", features, default=2.8)
        predicted_total = predicted_home_goals + predicted_away_goals
        
        # Over/under
        over_under_line = 5.5
        over_prob = 0.5 if predicted_total > over_under_line else 0.3
        under_prob = 1.0 - over_prob
        
        return {
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_win_probability": float(home_win_prob),
            "away_win_probability": float(away_win_prob),
            "predicted_home_goals": float(predicted_home_goals),
            "predicted_away_goals": float(predicted_away_goals),
            "predicted_total_goals": float(predicted_total),
            "over_under_line": float(over_under_line),
            "over_probability": float(over_prob),
            "under_probability": float(under_prob),
            "confidence": 0.70,
            "key_factors": [
                "Home ice advantage",
                "Recent form",
                "Head-to-head record"
            ],
            "model_version": self.model_version
        }
    
    def predict_real_time_win_probability(
        self,
        game_id: int,
        current_score_home: int,
        current_score_away: int,
        current_period: int,
        time_remaining_seconds: int,
        power_play_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict win probability during live game."""
        # Calculate base probability from score
        score_diff = current_score_home - current_score_away
        time_remaining_minutes = time_remaining_seconds / 60
        
        # Simplified model: adjust based on score and time
        if score_diff > 0:
            home_win_prob = 0.5 + (score_diff * 0.15) + (time_remaining_minutes / 60 * 0.1)
        elif score_diff < 0:
            home_win_prob = 0.5 + (score_diff * 0.15) - (time_remaining_minutes / 60 * 0.1)
        else:
            home_win_prob = 0.5
        
        home_win_prob = max(0.05, min(0.95, home_win_prob))
        away_win_prob = 1.0 - home_win_prob
        
        # Next goal probability (simplified)
        next_goal_home_prob = 0.5 if score_diff == 0 else (0.6 if score_diff > 0 else 0.4)
        next_goal_away_prob = 1.0 - next_goal_home_prob
        
        # Momentum (simplified)
        momentum_score = score_diff * 10
        momentum_team = "Home" if score_diff > 0 else "Away"
        
        # Comeback probability
        comeback_prob = 0.3 if abs(score_diff) <= 2 and time_remaining_minutes > 10 else 0.1
        
        return {
            "game_id": game_id,
            "home_win_probability": float(home_win_prob),
            "away_win_probability": float(away_win_prob),
            "next_goal_home_probability": float(next_goal_home_prob),
            "next_goal_away_probability": float(next_goal_away_prob),
            "momentum_score": float(momentum_score),
            "momentum_team": momentum_team,
            "comeback_probability": float(comeback_prob),
            "model_version": self.model_version
        }
    
    def predict_next_goal_scorer(
        self,
        game_id: int,
        current_period: int,
        time_remaining_seconds: int
    ) -> Dict[str, Any]:
        """Predict who will score the next goal."""
        # TODO: Fetch players on ice and their stats
        # For now, return placeholder
        candidates = [
            {"player_id": "P100001", "player_name": "Player 1", "probability": 0.15, "team": "Home"},
            {"player_id": "P100002", "player_name": "Player 2", "probability": 0.12, "team": "Home"},
            {"player_id": "P100003", "player_name": "Player 3", "probability": 0.10, "team": "Away"},
        ]
        
        return {
            "game_id": game_id,
            "top_candidates": candidates,
            "expected_time_until_goal": 180.0,  # 3 minutes
            "model_version": self.model_version
        }
    
    def find_similar_players(
        self,
        player_id: str,
        season_id: str,
        limit: int = 10,
        min_similarity: float = 70.0
    ) -> Dict[str, Any]:
        """Find players with similar play styles."""
        # TODO: Use similarity model or embeddings
        # For now, return placeholder
        similar_players = [
            {
                "player_id": "P100010",
                "player_name": "Similar Player 1",
                "similarity_score": 85.5,
                "similar_stats": ["goals", "shooting_pct", "cf_pct"],
                "different_stats": ["assists", "passing"]
            },
            {
                "player_id": "P100011",
                "player_name": "Similar Player 2",
                "similarity_score": 78.2,
                "similar_stats": ["war", "gar", "points"],
                "different_stats": ["goals", "physical_play"]
            }
        ]
        
        return {
            "player_id": player_id,
            "player_name": "Player Name",  # TODO: Fetch from DB
            "similar_players": similar_players[:limit],
            "model_version": self.model_version
        }
    
    def compare_player_value(
        self,
        player1_id: str,
        player2_id: str,
        season_id: str
    ) -> Dict[str, Any]:
        """Compare player value across metrics."""
        # TODO: Implement value comparison
        return {
            "player1_id": player1_id,
            "player2_id": player2_id,
            "player1_value_score": 75.5,
            "player2_value_score": 72.3,
            "value_difference": 3.2,
            "key_differences": ["WAR", "Age", "Contract"],
            "model_version": self.model_version
        }
    
    def predict_line_chemistry(
        self,
        player1_id: str,
        player2_id: str,
        player3_id: Optional[str],
        team_id: str,
        season_id: str
    ) -> Dict[str, Any]:
        """Predict line chemistry."""
        # TODO: Use chemistry model
        chemistry_score = 75.0  # Placeholder
        
        return {
            "chemistry_score": chemistry_score,
            "offensive_chemistry": 80.0,
            "defensive_chemistry": 70.0,
            "transition_chemistry": 75.0,
            "expected_goals_together": 2.5,
            "expected_cf_pct_together": 55.0,
            "optimal_strength": "5v5",
            "optimal_game_state": "All",
            "confidence": 0.70,
            "model_version": self.model_version
        }
    
    def optimize_lineup(
        self,
        team_id: str,
        season_id: str,
        opponent_team_id: Optional[str] = None,
        game_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate optimal line combinations."""
        # TODO: Implement lineup optimization
        return {
            "team_id": team_id,
            "optimal_forward_lines": [
                {"player1": "P100001", "player2": "P100002", "player3": "P100003"},
                {"player1": "P100004", "player2": "P100005", "player3": "P100006"},
            ],
            "optimal_defense_pairs": [
                {"player1": "P100007", "player2": "P100008"},
            ],
            "optimal_pp_units": [],
            "optimal_pk_units": [],
            "expected_performance": 85.0,
            "model_version": self.model_version
        }
    
    def predict_goalie_stats(
        self,
        goalie_id: str,
        season_id: str,
        opponent_team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict goalie performance."""
        # TODO: Implement goalie prediction
        return {
            "goalie_id": goalie_id,
            "predicted_save_pct": 0.920,
            "predicted_gaa": 2.50,
            "predicted_shutout_probability": 0.15,
            "predicted_quality_start_probability": 0.65,
            "model_version": self.model_version
        }
    
    def predict_playoff_probability(
        self,
        team_id: str,
        season_id: str
    ) -> Dict[str, Any]:
        """Predict playoff probability."""
        # TODO: Implement playoff prediction
        return {
            "team_id": team_id,
            "playoff_probability": 0.75,
            "seed_probabilities": {
                "1": 0.10,
                "2": 0.20,
                "3": 0.25,
                "4": 0.20
            },
            "championship_probability": 0.15,
            "model_version": self.model_version
        }
    
    def detect_breakout_players(
        self,
        season_id: str,
        min_probability: float = 50.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Detect players likely to break out."""
        # TODO: Implement breakout detection
        return [
            {
                "player_id": "P100020",
                "player_name": "Breakout Candidate",
                "breakout_probability": 75.5,
                "expected_improvement_pct": 25.0,
                "breakout_timeline_weeks": 4
            }
        ]
    
    def assess_injury_risk(
        self,
        player_id: str,
        season_id: str
    ) -> Dict[str, Any]:
        """Assess player injury risk."""
        # TODO: Implement injury risk assessment
        return {
            "player_id": player_id,
            "injury_risk_score": 35.0,
            "risk_category": "Medium",
            "most_likely_injury_type": "Lower body",
            "recommended_rest_days": 1,
            "model_version": self.model_version
        }
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def _predict_with_model(self, model_name: str, features: np.ndarray, default: float = 0.0) -> float:
        """Predict using a model, with fallback to default."""
        if model_name in self._models:
            try:
                prediction = self._models[model_name].predict(features.reshape(1, -1))[0]
                return float(prediction)
            except Exception as e:
                logger.warning(f"Error using model {model_name}: {e}")
                return default
        else:
            logger.debug(f"Model {model_name} not loaded, using default")
            return default
    
    def _get_player_features(self, player_id: str, season_id: Optional[str]) -> np.ndarray:
        """Get player features for prediction."""
        # TODO: Fetch from database and engineer features
        # For now, return placeholder features
        return np.array([0.5] * 20)  # 20 features placeholder
    
    def _get_team_features(self, home_team_id: str, away_team_id: str, season_id: str) -> np.ndarray:
        """Get team features for prediction."""
        # TODO: Fetch from database and engineer features
        # For now, return placeholder features
        return np.array([0.5] * 15)  # 15 features placeholder


# Singleton instance
ml_service = MLService()
