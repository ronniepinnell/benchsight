-- Add net_x and net_y columns to event-based fact tables
-- Run this in Supabase Dashboard SQL Editor:
-- https://supabase.com/dashboard/project/amuisqvhhiigxetsfame/sql/new
-- Then re-run: ./benchsight.sh db upload

ALTER TABLE public."fact_breakouts" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_breakouts" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_events" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_events" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_faceoffs" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_faceoffs" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_goals" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_high_danger_chances" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_high_danger_chances" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_penalties" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_penalties" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_rushes" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_rushes" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_saves" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_saves" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_scoring_chances_detailed" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_scoring_chances_detailed" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_shots" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_shots" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_turnovers_detailed" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_turnovers_detailed" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_zone_entries" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_zone_entries" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
ALTER TABLE public."fact_zone_exits" ADD COLUMN IF NOT EXISTS net_x DOUBLE PRECISION;
ALTER TABLE public."fact_zone_exits" ADD COLUMN IF NOT EXISTS net_y DOUBLE PRECISION;
