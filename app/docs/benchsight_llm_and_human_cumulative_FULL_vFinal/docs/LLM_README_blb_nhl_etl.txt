
LLM README – Benchsight BLB ↔ NHL Player Comparison ETL

What this folder contains
-------------------------
• benchsight_blb_nhl_player_comp_etl_plan.txt
    - A detailed, step-by-step ETL plan describing how to build:
        * fact_blb_player_features (+ standardized version)
        * fact_nhl_player_features (+ standardized version)
        * fact_blb_nhl_player_comps
        * vw_blb_player_comp_cards
    - It explains the feature-space, normalization, distance metrics,
      and where this comparison layer fits into the overall project.

How you (the LLM) should use it
-------------------------------
1. Read benchsight_blb_nhl_player_comp_etl_plan.txt fully.
2. When asked to implement BLB ↔ NHL comps, do NOT invent new logic;
   instead, follow the plan’s steps:
    - Use existing BLB and NHL MART stats tables from the project.
    - Derive per-player features.
    - Standardize metrics to z-scores by league/position/season.
    - Compute similarity and top-N comps.
3. When generating SQL or Python:
    - Align column names and table naming patterns with the project’s
      table catalog and stats catalog.
    - Keep the comparison layer modular, so it can be scheduled
      as a separate stage in the orchestrator.

4. When asked to modify or extend this:
    - Start by restating the relevant part of the ETL plan.
    - Then propose adjustments (e.g., new features, weights, filters).

Short-hand reference
--------------------
If a user says:
    “Use the BLB–NHL player comps ETL plan”
or
    “Follow the Benchsight player comparison ETL logic”
you should assume they are referring to this plan and base
your implementation on it.
