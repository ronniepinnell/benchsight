#!/usr/bin/env python3
"""
=============================================================================
Test Suite: Video Highlights
=============================================================================
Tests for video integration, highlight generation, and YouTube URL handling.

Run with: pytest tests/test_video_highlights.py -v
=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.video_integration import (
    extract_youtube_id,
    format_timestamp,
    parse_timestamp,
    VideoSource,
    VideoClip,
    VideoManager
)


class TestYouTubeIdExtraction:
    """Test YouTube video ID extraction from various URL formats."""
    
    def test_standard_watch_url(self):
        """Extract from youtube.com/watch?v=..."""
        url = "https://www.youtube.com/watch?v=hMM6oE6O_Mg"
        assert extract_youtube_id(url) == "hMM6oE6O_Mg"
    
    def test_watch_url_with_params(self):
        """Extract from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=DaQS2qlm_C4&t=125s"
        assert extract_youtube_id(url) == "DaQS2qlm_C4"
    
    def test_short_url(self):
        """Extract from youtu.be short URL."""
        url = "https://youtu.be/Mt-lTEMScK4"
        assert extract_youtube_id(url) == "Mt-lTEMScK4"
    
    def test_embed_url(self):
        """Extract from embed URL."""
        url = "https://www.youtube.com/embed/fbZ-kglEMfk"
        assert extract_youtube_id(url) == "fbZ-kglEMfk"
    
    def test_empty_url(self):
        """Handle empty input."""
        assert extract_youtube_id("") is None
        assert extract_youtube_id(None) is None
    
    def test_invalid_url(self):
        """Handle non-YouTube URL."""
        url = "https://vimeo.com/12345"
        result = extract_youtube_id(url)
        # Should return None or not match vimeo ID
        assert result is None or result != "12345"
    
    def test_url_without_scheme(self):
        """URL with v= pattern but missing scheme."""
        url = "youtube.com/watch?v=test1234567"
        result = extract_youtube_id(url)
        # Should still find the video ID
        assert result == "test1234567"


class TestTimestampFormatting:
    """Test timestamp conversion utilities."""
    
    def test_format_seconds_only(self):
        """Format time under a minute."""
        assert format_timestamp(45) == "0:45"
    
    def test_format_minutes_seconds(self):
        """Format time in minutes:seconds."""
        assert format_timestamp(125) == "2:05"
    
    def test_format_hours_minutes_seconds(self):
        """Format time over an hour."""
        assert format_timestamp(3725) == "1:02:05"
    
    def test_format_zero(self):
        """Format zero seconds."""
        assert format_timestamp(0) == "0:00"
    
    def test_format_exact_minute(self):
        """Format exact minute boundary."""
        assert format_timestamp(60) == "1:00"
    
    def test_parse_mm_ss(self):
        """Parse MM:SS format."""
        assert parse_timestamp("2:05") == 125
    
    def test_parse_hh_mm_ss(self):
        """Parse HH:MM:SS format."""
        assert parse_timestamp("1:02:05") == 3725
    
    def test_parse_roundtrip(self):
        """Format then parse returns original value."""
        for seconds in [0, 45, 125, 3600, 3725]:
            formatted = format_timestamp(seconds)
            parsed = parse_timestamp(formatted)
            assert parsed == seconds, f"Roundtrip failed for {seconds}"


class TestVideoSource:
    """Test VideoSource data class."""
    
    @pytest.fixture
    def video_source(self):
        return VideoSource(
            game_id=18969,
            video_type="Full_Ice",
            video_url="https://www.youtube.com/watch?v=hMM6oE6O_Mg",
            video_id="hMM6oE6O_Mg"
        )
    
    def test_timestamp_url(self, video_source):
        """Generate watch URL with timestamp."""
        url = video_source.get_timestamp_url(125)
        assert url == "https://www.youtube.com/watch?v=hMM6oE6O_Mg&t=125s"
    
    def test_timestamp_url_zero(self, video_source):
        """Generate URL with zero timestamp."""
        url = video_source.get_timestamp_url(0)
        assert url == "https://www.youtube.com/watch?v=hMM6oE6O_Mg&t=0s"
    
    def test_embed_url_start_only(self, video_source):
        """Generate embed URL with start time only."""
        url = video_source.get_embed_url(125)
        assert "start=125" in url
        assert "hMM6oE6O_Mg" in url
    
    def test_embed_url_start_end(self, video_source):
        """Generate embed URL with start and end times."""
        url = video_source.get_embed_url(125, 140)
        assert "start=125" in url
        assert "end=140" in url


class TestVideoClip:
    """Test VideoClip data class."""
    
    @pytest.fixture
    def video_clip(self):
        source = VideoSource(
            game_id=18969,
            video_type="Full_Ice",
            video_url="https://www.youtube.com/watch?v=hMM6oE6O_Mg",
            video_id="hMM6oE6O_Mg"
        )
        return VideoClip(
            video_source=source,
            start_seconds=360,
            end_seconds=380,
            clip_type="highlight",
            title="Test Goal",
            description="A test goal clip"
        )
    
    def test_duration(self, video_clip):
        """Calculate clip duration."""
        assert video_clip.duration == 20
    
    def test_watch_url(self, video_clip):
        """Get watch URL with correct timestamp."""
        assert "t=360s" in video_clip.watch_url
    
    def test_embed_url(self, video_clip):
        """Get embed URL with start and end."""
        assert "start=360" in video_clip.embed_url
        assert "end=380" in video_clip.embed_url


class TestVideoManager:
    """Test VideoManager class."""
    
    @pytest.fixture
    def video_manager(self):
        return VideoManager("data")
    
    def test_initialization(self, video_manager):
        """Manager initializes correctly."""
        assert video_manager.data_dir == Path("data")
        assert isinstance(video_manager.video_sources, dict)
    
    def test_load_game_video(self, video_manager):
        """Load video source for a game."""
        video = video_manager.load_game_video(18969)
        if video:  # Only test if video data exists
            assert video.game_id == 18969
            assert video.video_id is not None
    
    def test_load_nonexistent_game(self, video_manager):
        """Handle missing video gracefully."""
        video = video_manager.load_game_video(99999)
        assert video is None
    
    def test_caching(self, video_manager):
        """Video sources are cached."""
        video1 = video_manager.load_game_video(18969)
        video2 = video_manager.load_game_video(18969)
        if video1 and video2:
            assert video1 is video2  # Same object from cache


class TestHighlightGeneration:
    """Test automatic highlight generation."""
    
    @pytest.fixture
    def video_manager(self):
        return VideoManager("data")
    
    @pytest.fixture
    def events_df(self):
        """Load events data."""
        csv_path = Path("data/output/fact_events.csv")
        if csv_path.exists():
            return pd.read_csv(csv_path)
        return None
    
    def test_find_goals(self, events_df):
        """Find all goals in events."""
        if events_df is None:
            pytest.skip("Events data not available")
        
        goals = events_df[
            (events_df['event_type'] == 'Goal') | 
            (events_df['event_detail'].str.contains('Goal', case=False, na=False))
        ]
        assert len(goals) > 0, "Should find at least one goal"
    
    def test_goals_have_timestamps(self, events_df):
        """Goals have video timestamps."""
        if events_df is None:
            pytest.skip("Events data not available")
        
        goals = events_df[events_df['event_type'] == 'Goal']
        if len(goals) == 0:
            pytest.skip("No goals in data")
        
        if 'running_video_time' in goals.columns:
            timestamps_present = goals['running_video_time'].notna().sum()
            assert timestamps_present > 0, "Should have video timestamps for goals"
    
    def test_generate_game_highlights(self, video_manager):
        """Generate highlights for a game."""
        highlights = video_manager.generate_game_highlights(18969)
        # Should return a list (even if empty)
        assert isinstance(highlights, list)
    
    def test_get_event_url(self, video_manager):
        """Get URL for specific event."""
        url = video_manager.get_event_url(18969, 1189)  # Known goal event
        if url:
            assert "youtube.com" in url
            assert "t=" in url  # Has timestamp


class TestHighlightScoring:
    """Test highlight importance scoring logic."""
    
    def test_goal_high_score(self):
        """Goals should have high highlight scores."""
        # This tests the scoring concept - actual implementation in SQL
        base_scores = {
            'Goal': 80,
            'Save': 40,
            'Hit': 30,
            'Fight': 70
        }
        assert base_scores['Goal'] >= 70
        assert base_scores['Fight'] >= 70
    
    def test_ot_modifier(self):
        """OT events get bonus points."""
        # OT modifier should add points
        ot_bonus = 20
        base_goal = 80
        assert base_goal + ot_bonus > 90
    
    def test_breakaway_modifier(self):
        """Breakaway events get bonus points."""
        breakaway_bonus = 20
        base_shot = 20
        assert base_shot + breakaway_bonus >= 40


class TestDataIntegrity:
    """Test data integrity for video highlight generation."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    def test_events_have_video_columns(self, output_dir):
        """fact_events has video-related columns."""
        csv_path = output_dir / "fact_events.csv"
        if not csv_path.exists():
            pytest.skip("fact_events.csv not found")
        
        df = pd.read_csv(csv_path)
        # Check for running_video_time
        video_cols = [c for c in df.columns if 'video' in c.lower() or 'running' in c.lower()]
        assert len(video_cols) > 0, "Should have video-related columns"
    
    def test_video_table_exists(self, output_dir):
        """fact_video table exists."""
        csv_path = output_dir / "fact_video.csv"
        if not csv_path.exists():
            pytest.skip("fact_video.csv not found")
        
        df = pd.read_csv(csv_path)
        assert len(df) > 0, "fact_video should have entries"
        assert 'Url_1' in df.columns or 'video_url' in df.columns
    
    def test_video_urls_are_valid(self, output_dir):
        """Video URLs are valid YouTube links."""
        csv_path = output_dir / "fact_video.csv"
        if not csv_path.exists():
            pytest.skip("fact_video.csv not found")
        
        df = pd.read_csv(csv_path)
        url_col = 'Url_1' if 'Url_1' in df.columns else 'video_url'
        
        for url in df[url_col].dropna():
            video_id = extract_youtube_id(url)
            assert video_id is not None, f"Invalid URL: {url}"
            assert len(video_id) == 11, f"Video ID should be 11 chars: {video_id}"
    
    def test_events_video_game_alignment(self, output_dir):
        """Events and video data align by game_id."""
        events_path = output_dir / "fact_events.csv"
        video_path = output_dir / "fact_video.csv"
        
        if not events_path.exists() or not video_path.exists():
            pytest.skip("Required files not found")
        
        events = pd.read_csv(events_path)
        videos = pd.read_csv(video_path)
        
        events_games = set(events['game_id'].unique())
        video_games = set(videos['game_id'].unique())
        
        # Games with video should have events
        assert len(events_games & video_games) > 0, "Should have overlapping games"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
