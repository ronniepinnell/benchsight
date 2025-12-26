-- =============================================================================
-- HOCKEY ANALYTICS - DATABASE SCHEMA CREATION
-- =============================================================================
-- File: sql/ddl/01_create_schemas.sql
--
-- PURPOSE:
--   Create the database schemas for staging and data mart.
--
-- SCHEMAS:
--   staging:     Raw data loaded from files
--   hockey_mart: Transformed, analysis-ready data
--
-- RUN: psql -d hockey_analytics -f sql/ddl/01_create_schemas.sql
-- =============================================================================

-- Create staging schema for raw data
CREATE SCHEMA IF NOT EXISTS staging;

COMMENT ON SCHEMA staging IS 'Raw data loaded from Excel files before transformation';

-- Create data mart schema for transformed data
CREATE SCHEMA IF NOT EXISTS hockey_mart;

COMMENT ON SCHEMA hockey_mart IS 'Transformed, analysis-ready data for Power BI and ML';

-- Grant permissions (adjust as needed)
-- GRANT ALL ON SCHEMA staging TO hockey_user;
-- GRANT ALL ON SCHEMA hockey_mart TO hockey_user;
