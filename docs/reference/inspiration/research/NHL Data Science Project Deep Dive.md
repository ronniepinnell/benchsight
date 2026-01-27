# **Technical Audit and Strategic Implementation of Spatiotemporal Hockey Analytics: A Comprehensive Framework for Next-Generation Performance Modeling**

## **1\. Executive Technical Overview and The Paradigm Shift in Hockey Analytics**

The National Hockey League (NHL) is currently undergoing a fundamental transformation in how performance is quantified, moving from discrete event-based logging to continuous spatiotemporal tracking. Historically, analytics departments relied on the Real-Time Scoring System (RTSS), a manual entry system recording roughly 300-400 events per game. The introduction of Puck and Player Tracking (PPT), powered by SMT (SportsMEDIA Technology) and Hawk-Eye infrastructure, has expanded this dataset to approximately one million data points per game, capturing the $x, y, z$ coordinates of every player and the puck at frequencies ranging from 12 to 60 Hz.1

This report serves as a rigorous technical audit and implementation roadmap for a proprietary high-performance analytics platform. The objective is to bridge the gap between raw coordinate streams and actionable "micro-stats"—specifically defining **Rush**, **Scoring Chance**, **Play**, and **Sequence**—and to construct a robust Expected Goals (xG) model that accounts for the nuances of pre-shot movement and defensive pressure. The analysis suggests that while the current project architecture captures foundational event data, it critically lacks the *connective tissue* of sequence-based logic and the *geometric rigor* of vector-based defensive metrics required to compete with industry leaders like Sportslogiq or internal team systems.3

### **1.1 The Epistemology of Tracking Data: From Frequency to Geometry**

The core deficiency in many nascent analytics projects is the reliance on frequency counts (e.g., "How many zone entries occurred?") rather than geometric efficiency (e.g., "What was the velocity vector of the defense during the entry?"). Current research indicates that the "Corsi Era" (proxying possession via shot volume) has been superseded by the "xG Era" (shot quality), which is now yielding to the "Micro-Stat Era" (process evaluation).4

To model the game effectively, one must treat hockey not as a series of isolated events, but as a continuous fluid dynamic problem where space and time are the primary currencies. The project must therefore pivot from an **Event-Based Data Model** to a **Sequence-Based Data Model**. This distinction is non-trivial; it requires a fundamental restructuring of the ingestion pipeline to link disparate rows of data into coherent narrative chains—defined here as *Sequences*.5

### **1.2 Gap Analysis: Identified Deficiencies vs. Industry Standards**

A deep dive into the provided research materials and current state-of-the-art methodologies reveals specific gaps in the current project scope that must be addressed:

| Component | Current "Standard" Project State | Required "Expert" Implementation | Research Support |
| :---- | :---- | :---- | :---- |
| **Data Topology** | Discrete Events (Shots, Hits) | Continuous Sequences (Possession Chains) | 5 |
| **Possession** | Inferred from Event Logs | Derived from Proximity ($r \< 5ft$) & Velocity | 6 |
| **Defensive Metrics** | Box Score (Blocks, Hits) | Spatiotemporal (Gap Control, Pressure Index) | 7 |
| **Rush Definition** | Qualitative / Time-Based | Geometric & Time-Based (4s window \+ Displacement) | 9 |
| **xG Model** | Shot Location \+ Angle | Pre-Shot Movement, Royal Road, Freeze Time | 11 |
| **Calibration** | Static Training Data | Dynamic Re-calibration for SMT Sensor Drift | 11 |

The following sections detail the mathematical and architectural solutions to close these gaps.

## ---

**2\. Fundamental Data Architecture and Coordinate Systems**

The bedrock of any advanced analytics platform is its coordinate system. Inconsistencies in origin points, rink dimensions, or normalization logic will propagate errors into every downstream calculation, rendering complex metrics like "Gap Control" invalid.

### **2.1 The SMT/Hawk-Eye Coordinate Reference System**

The NHL's current tracking infrastructure utilizes a Cartesian coordinate system that must be standardized before ingestion.

* **Origin $(0,0)$:** The center ice face-off dot is the universal origin point.13  
* **X-Axis:** Represents the length of the ice, ranging from $-100$ to $+100$ feet. The goal lines are typically located at $x \= \\pm 89$ feet.  
* **Y-Axis:** Represents the width of the ice, ranging from $-42.5$ to $+42.5$ feet.14  
* **Z-Axis:** Represents elevation above the ice surface. While the puck is tracked in 3D, player centroids are typically projected onto the 2D plane for tactical analysis.

Critical Normalization Requirement:  
Raw tracking feeds often report absolute coordinates relative to the arena's fixed sensors. For predictive modeling, however, all coordinates must be normalized relative to the attacking team.

* *The "Attacking Right" Standard:* All data frames should be transformed such that the team currently in possession is attacking toward the positive x-axis (right side).  
* *Transformation Logic:* If the attacking team's target net is at $x \= \-89$, the transformation $x' \= \-x$ and $y' \= \-y$ must be applied. This ensures that a shot from the "left faceoff circle" is mathematically identical regardless of the period or end of the ice.11 Failure to normalize creates "mirror" artifacts in heatmaps and confuses machine learning classifiers.

### **2.2 Temporal Synchronization and Sensor Fusion**

A major technical challenge identified in the research is the disparity in sampling rates between the puck and players.

* **Puck Frequency:** \~60 Hz (Infrared/Optical).  
* **Player Frequency:** \~12-15 Hz (Optical/Tag-based).2

Derivation of Consistent States:  
To calculate metrics like "Pass Completion Probability" or "Interception Reach," the system must perform temporal interpolation. The player coordinates ($P\_{t}$) at 12 Hz must be upsampled to match the puck's 60 Hz timestamps ($O\_{t}$) using cubic spline interpolation. This creates a synchronized "Game State Tensor" at 60 frames per second, allowing for the precise calculation of velocity vectors ($\\vec{v}$) and acceleration ($\\vec{a}$) required for pressure modeling.8

### **2.3 Handling Data Drift and "Ghosting"**

Recent analysis of the 2024-2025 data suggests significant "drift" in event definitions due to hardware changes (from infrared to fully optical SMT configurations). Specifically, shot coordinates near the crease and "short misses" are being tracked with higher sensitivity, artificially inflating Expected Goals (xG) totals if older models are not recalibrated.11 The data engineering pipeline must include a **Drift Detection Module** that monitors the distribution of shot distances week-over-week to flag anomalies in tracking calibration.

## ---

**3\. Defining the Atomic Units: Play, Sequence, and Possession**

To move beyond the box score, we must define the hierarchical ontology of a hockey game. The proposed schema is: **Game $\\rightarrow$ Period $\\rightarrow$ Shift $\\rightarrow$ Sequence $\\rightarrow$ Play.**

### **3.1 The "Sequence": A Possession-Based Construct**

The concept of the "Sequence" is the most critical missing link in the current project. A Sequence is defined as a continuous interval of time where one team maintains controlling influence over the puck.

* **Definition:** A Sequence $S$ begins at time $t\_{start}$ when a team gains possession (via Faceoff Win, Takeaway, or Puck Recovery) and ends at $t\_{end}$ when possession is lost, a goal is scored, or a stoppage occurs.5  
* Mathematical Boundary:

  $$S \= \\{ e\_i \\in E \\mid t\_{start} \\le t(e\_i) \\le t\_{end}, \\text{Possession}(e\_i) \= \\text{Team}\_A \\}$$

  where $E$ is the set of all game events.  
* **Differentiating from Shifts:** A single player shift may contain multiple sequences (e.g., offense $\\rightarrow$ turnover $\\rightarrow$ defense $\\rightarrow$ turnover $\\rightarrow$ offense). The Sequence isolates the tactical unit of the game.

Calculating Sequence Value ($V\_{seq}$):  
We assign value to a sequence based on the cumulative xG generated or the potential xG of the zone entry.

$$V\_{seq} \= \\sum\_{i=1}^{n} xG(shot\_i) \+ \\sum\_{j=1}^{m} xV(entry\_j)$$

Research indicates that a Sequence containing a "Controlled Entry" has a baseline potential value of \~0.067 xG, whereas a "Failed Dump-In" has a value of \~0.003 xG.5

### **3.2 The "Play": Classifying Risk and Intent**

Within a Sequence, individual actions ("Plays") must be classified by their risk profile to aid coaching analysis.

* **Green Plays:** Low-risk actions with no immediate pressure (e.g., a D-to-D pass in the neutral zone).  
* **Yellow Plays:** Actions that force a defensive reaction (e.g., attacking the blue line, dumping the puck to a specific corner).  
* **Red Plays:** High-risk, high-reward actions attempting to beat a defender directly (e.g., a pass through the Royal Road or a 1-on-1 deke).16

### **3.3 Defining "Possession" in the Optical Era**

In tracking data, "Possession" is not an explicit flag; it must be derived.

* Proximity Algorithm: A player $P$ is deemed to have possession at time $t$ if the Euclidean distance between the player centroid and the puck is less than a threshold $r$ (typically 3-5 feet) and the velocity vectors are correlated.

  $$\\text{Possession}(P, t) \\iff \\text{dist}(P\_t, \\text{Puck}\_t) \< r \\land \\cos(\\theta\_{\\vec{v}\_P, \\vec{v}\_{Puck}}) \> 0.8$$  
* **Loose Puck Recovery (LPR):** This is a critical micro-stat. An LPR event is generated when the puck state transitions from "Free" (no player within $r$) to "Possessed".6

## ---

**4\. The Taxonomy of Transition: Rush and Zone Entry Analysis**

The "Rush" is the most volatile and dangerous state in hockey. To analyze it, we must replace qualitative "eye-test" definitions with strict programmable logic.

### **4.1 The Technical Definition of a "Rush"**

There is a consensus among advanced analytics groups (Sportslogiq, Natural Stat Trick) that a Rush is defined by **time and geometry**.

* **Definition:** A Rush is a sequence where an attacking team transitions from the Neutral Zone into the Offensive Zone and generates a shot attempt within a specific time window, typically **4.0 seconds** of crossing the blue line.9  
* **The 4-Second Rule:** Empirical studies show that the correlation between "Rush Chances" and shooting percentage ($Sh\\%$) effectively vanishes if the shot occurs more than 4-6 seconds after entry. The defense has settled, and the play converts to "Zone Offense" or "Cycle".9

**Algorithm for Rush Detection:**

1. **Event Trigger:** Detect $t\_{entry}$ where the puck crosses the Offensive Blue Line (absolute $x \> 25$ or $x \< \-25$).  
2. **Context Filter:** Ensure the play originated in the Neutral or Defensive Zone (no faceoffs at the blueline).  
3. **Outcome Check:** Identify if a Shot Attempt occurs at $t\_{shot}$.  
4. Boolean Logic:

   $$\\text{IsRush} \= (t\_{shot} \- t\_{entry} \\le 4.0)$$

### **4.2 Zone Entry Classification: Controlled vs. Uncontrolled**

The *method* of entry is the single strongest predictor of offensive success.

* **Controlled Entry (Carry/Pass):** The attacking team maintains possession across the blue line.  
  * *Carry-In:* Player coordinates cross the line simultaneous to puck coordinates with proximity $\< 3ft$.  
  * *Pass-In:* Puck crosses the line and is received by a teammate within $\\delta t \< 1.0s$.  
  * *Impact:* Controlled entries generate approximately **twice the shot volume** and significantly higher xG compared to dump-ins.18  
* **Uncontrolled Entry (Dump/Tip):**  
  * *Dump-In:* Puck crosses the line with no player in proximity.  
  * *Failed Entry:* Possession is lost between the Red Line and the Blue Line.

Metric: Denied Zone Entry (The "Gap" Metric)  
This is a vital metric for evaluating defensemen. A "Denial" occurs when a defender forces a turnover or a dump-in immediately at the blue line.

$$\\text{EntryDenial\\%} \= \\frac{\\text{EntriesDenied}}{\\text{TotalAttemptsAgainst}}$$

Top-tier defensemen excel not just at retrieving dump-ins, but at preventing the Controlled Entry entirely.20

## ---

**5\. Quantifying Offensive Threat: Expected Goals (xG) 3.0**

The project currently lacks a sophisticated xG model. We must move beyond simple shot location (distance/angle) to a **Gradient Boosted Model (XGBoost)** that incorporates pre-shot movement and granular context.

### **5.1 Defining the "Scoring Chance"**

While xG is a continuous probability, "Scoring Chance" is a binary classification used for reporting.

* **Geometric Definition (War-on-Ice):** A shot taken from the "Home Plate" polygon (extending from the goal posts to the faceoff dots, capped at the top of the circles).21  
* **Probabilistic Definition:**  
  * **Scoring Chance:** Any unblocked shot with $xG \> 0.08$.  
  * **High Danger Scoring Chance (HDSC):** Any shot with $xG \\ge 0.20$.23

### **5.2 Feature Engineering for the xG Model**

To build a "Sportslogiq-level" model, we must engineer features that capture the *disruption* of the goaltender. The model calculates $P(\\text{Goal} \\mid \\text{Shot})$.

**The Input Vector ($X$):**

1. **Spatial Features:**  
   * **Distance ($d$):** Euclidean distance to the center of the goal line.  
   * **Angle ($\\theta$):** Angle relative to the central y-axis.  
2. **Contextual Features (Crucial for Accuracy):**  
   * **Royal Road Crossing:** A Boolean flag indicating if the pass immediately preceding the shot crossed the central y-axis (East-West movement). This forces the goalie to reset laterally and drastically increases conversion rates.11  
   * **One-Timer Flag:** Time delta between pass reception and shot release ($\< 0.5s$).  
   * **Rebound:** Shot taken within 3 seconds of a previous shot.  
   * **Rush Event:** Boolean (derived from Section 4.1).  
   * **Traffic/Screen:** Count of players within the triangular "visual cone" between the shooter and the goalie.24  
3. **Game State:**  
   * **Strength State:** 5v5, 5v4, 4v5, Empty Net.  
   * **Score Adjustment:** Adjusting for "score effects" where leading teams play conservatively (turtle), artificially inflating opponent metrics.25

Modeling Approach:  
While Logistic Regression is interpretable, XGBoost is recommended to capture non-linear interactions (e.g., a shot from distance $d$ is harmless, but a shot from distance $d$ with a screen is dangerous).26

$$xG \= \\sigma\\left(\\sum\_{k} f\_k(X)\\right)$$

where $f\_k$ are the regression trees in the boosting ensemble.

### **5.3 Addressing Model Drift**

Research 11 highlights a critical issue: changes in NHL tracking data (from 2021 to 2025\) have led to data drift. Specifically, "short misses" near the crease are sometimes tracked erroneously as shots, and shot coordinates have shifted slightly.

* **Solution:** Implement **Nested Cross-Validation** stratified by season. Use a decay parameter to weight recent seasons (e.g., 2024-25) more heavily than older data (2017-2020) to ensure the model reflects the current physical reality of the tracking sensors.

## ---

**6\. Defensive Micro-Stats: The "Dark Matter" of Hockey Analytics**

Defensive value is notoriously difficult to capture with event data because good defense often results in *no event occurring* (e.g., a perfect gap prevents a pass). We will define these metrics using spatiotemporal logic.

### **6.1 Quantifying "Gap Control"**

Gap Control is the ability of a defender to minimize the distance to the rushing attacker while matching their velocity.7

Derivation:  
For a Rush sequence with Attacker $A$ and Defender $D$:

1. Vertical Gap ($G\_v$): The Euclidean distance along the x-axis at the moment $A$ crosses the blue line.

   $$G\_v \= |x\_A \- x\_D|$$

   Target: Elite gap is 1-2 stick lengths (\~6-10 feet).28  
2. Velocity Delta ($\\Delta v$): The difference in speed vectors.

   $$\\Delta v \= |\\vec{v}\_A \- \\vec{v}\_D|$$

   Insight: A small gap with a high $\\Delta v$ (attacker much faster) is a "Blow-By" risk. The ideal state is Tight Gap \+ Matched Velocity.

### **6.2 Forecheck Pressure and The Pressure Index**

Forechecking is the application of pressure to disrupt the opponent's breakout.29 We quantify this using a physics-based **Pressure Index**.

**Algorithm:**

1. **Time-to-Intercept ($T\_{int}$):** For every defender $D\_i$ and the puck carrier $P$, calculate the time required for $D\_i$ to reach $P$ based on current position and velocity vectors.8  
2. Pressure Probability ($P\_{pressure}$): Map $T\_{int}$ to a probability using a logistic decay function. If interception is imminent ($\< 1.5s$), pressure is maximized.

   $$P\_{pressure} \= \\sum\_{i} \\left( 1 \- \\frac{1}{1 \+ e^{-k(T\_{int, i} \- T\_0)}} \\right)$$  
3. **Active vs. Passive:** Filter out defenders moving *away* from the puck. Only count $D\_i$ if the angle between their velocity vector and the vector to the puck is $\< 45^\\circ$.

### **6.3 Passing Lane Denial (The "Teardrop" Model)**

To measure how well a team clogs passing lanes, we utilize the "Teardrop" model.2

* **Lane Openness ($\\gamma$):** Construct a teardrop shape between the passer and potential receiver.  
* **Metric:** If a defender's coordinates intersect this shape, the lane is "Clogged." We calculate the **Total Lane Denial** score for defensemen by summing the passing options they eliminate per 60 minutes.

## ---

**7\. Strategic Implementation Plan and Architecture**

To operationalize these definitions, a robust data engineering pipeline is required.

### **7.1 Infrastructure: The "Kappa" Architecture**

Given the volume of data (60 Hz streaming), a traditional batch ETL process is insufficient for real-time analysis.

* **Ingestion:** Use a streaming architecture (e.g., Apache Kafka or AWS Kinesis) to ingest JSON feeds from the NHL Edge API.30  
* **Processing:** Use a stream processing engine (e.g., Apache Flink or Spark Structured Streaming) to perform the coordinate normalization and interpolation in real-time.  
* **Storage:** Store raw JSON in a Data Lake (S3/GCS) and processed micro-stats in a columnar database (Snowflake/BigQuery) for rapid querying.32

### **7.2 Implementation Checklist**

1. **Phase 1: Foundation.** Establish the coordinate normalization (Attacking Right) and sync the 12Hz/60Hz data streams.  
2. **Phase 2: Sequence Logic.** Write the graph logic to link events into Sequences. This is the prerequisite for all transition analysis.  
3. **Phase 3: The xG Model.** Train the XGBoost model using 2021-2025 data, incorporating the "Royal Road" and "Rush" features.  
4. **Phase 4: Defensive Metrics.** Implement the Gap Control and Pressure Index algorithms.

### **7.3 Visualization and Reporting**

The output of this system should be visualized via:

* **Rink Heatmaps:** Showing shot density and "Pressure Zones".33  
* **Flow Charts:** Visualizing the outcome of Sequences (e.g., Entry $\\rightarrow$ Pass $\\rightarrow$ Shot).  
* **Player Cards:** displaying percentile rankings for specific micro-stats like "Entry Denial %" and "Forecheck Pressures per 60".

## **8\. Conclusion**

The transition from event counting to spatiotemporal modeling represents the mature phase of hockey analytics. By implementing the strict geometric definitions of **Rush** (4-second window), **Sequence** (possession-chain), and **Gap Control** (vector analysis) outlined in this report, the project will move beyond simple observation to predictive insight. The inclusion of **Forecheck Pressure** and **Pass Denial** metrics will provide a competitive advantage in evaluating the "unseen" aspects of the game. The immediate priority is the construction of the Sequence-based data model, which serves as the scaffold for all subsequent high-fidelity analysis.

## ---

**9\. Research Appendices**

### **Appendix A: Glossary of Derived Terms & Definitions**

| Term | Technical Definition | Source |
| :---- | :---- | :---- |
| **Rush** | A shot attempt occurring within **4.0 seconds** of a controlled offensive zone entry. | 9 |
| **Controlled Entry** | Zone entry where the puck carrier maintains possession ($\\Delta t \< 0.5s$ between crossing and touch) or completes a pass across the line. | 35 |
| **Scoring Chance** | Shot attempt with **$xG \> 0.08$** OR located within the "Home Plate" polygon. | 21 |
| **High Danger Chance** | Shot attempt with **$xG \\ge 0.20$**. | 23 |
| **Sequence** | A continuous chain of possession by one team, bounded by a turnover, stoppage, or goal. | 5 |
| **Vertical Gap** | Euclidean distance $ | x\_{Attacker} \- x\_{Defender} |
| **Forecheck Pressure** | Probability of interception $\> 0.5$ calculated via velocity vectors and Time-to-Intercept ($T\_{int}$). | 8 |
| **Royal Road** | The imaginary line connecting the center ice faceoff dot to the center of the goal line. Crossing it laterally increases xG significantly. | 11 |
| **Green/Yellow/Red Play** | Classification of play risk: Green (Open), Yellow (Forced Reaction), Red (High Risk/Beaten Defender). | 16 |

### **Appendix B: Mathematical Formulations**

1\. Expected Goals (XGBoost Objective Function Approximation):  
The probability $p$ of a goal is modeled as:

$$p(y=1|x) \= \\frac{1}{1 \+ e^{-\\sum f\_k(x)}}$$

Where $f\_k$ represent the additive functions (trees) learning features such as Distance, Angle, Rebound, and Royal Road status.  
2\. Gap Distance (Euclidean):

$$Gap \= \\sqrt{(x\_{Attacker} \- x\_{Defender})^2 \+ (y\_{Attacker} \- y\_{Defender})^2}$$

Note: For vertical gap, set $y$ terms to 0\.  
3\. Forecheck Pressure Intensity (Logistic Decay):

$$I\_{pressure} \= \\sum\_{d \\in Defenders} \\left( 1 \- \\frac{1}{1 \+ e^{-k(TimeIntercept\_d \- T\_{reaction})}} \\right)$$

Where $T\_{reaction}$ is the estimated reaction time (\~0.2s).  
4\. Sequence Value:

$$V\_{seq} \= \\sum\_{e \\in Sequence} xG\_e \+ (1 \- P\_{turnover}) \\times V\_{zone}$$

### **Appendix C: Implementation References & Libraries**

* **Python Libraries:** pandas (data manipulation), xgboost (modeling), sportypy (rink plotting), scikit-learn (logistic regression), scipy.interpolate (spline interpolation).  
* **R Packages:** nhlscraper 10, hockey-scraper.13  
* **Key Data Sources:** NHL Edge API (SMT), MoneyPuck (Calibration benchmarks) 23, Evolving Hockey (WAR/RAPM methodologies).38

### **Appendix D: Advanced Considerations & Future Outlook**

* **Pose Estimation:** Future iterations should leverage the $z$-coordinate and limb tracking (if available via Hawk-Eye) to determine *stick position* rather than just body centroid. This allows for "Stick-on-Puck" gap measurement, which is far more accurate than "Body-on-Body".1  
* **Fatigue Proxies:** Incorporate "Total Distance Traveled" and "Burst Count" ($\>20$ mph) in the current shift to weight xG models. A tired goalie or defenseman reacts slower, increasing goal probability.11  
* **Ghosting:** Use "Ghosting" techniques (simulating optimal defender positioning) to calculate "Defensive Runs Saved" by comparing actual positioning to the optimal theoretical position.41

#### **Works cited**

1. The Tech Stack: How the NHL is becoming a game of data on ice \- SportsPro, accessed January 21, 2026, [https://www.sportspro.com/features/broadcast-ott/nhl-technology-strategy-data-cloud-ai-digital-aws-apple-sap-sony/](https://www.sportspro.com/features/broadcast-ott/nhl-technology-strategy-data-cloud-ai-digital-aws-apple-sap-sony/)  
2. Identifying Completed Pass Types and Improving Passing Lane ..., accessed January 21, 2026, [https://cs.uwaterloo.ca/\~brecht/papers/passing-linhac-2022.pdf](https://cs.uwaterloo.ca/~brecht/papers/passing-linhac-2022.pdf)  
3. Sportlogiq: Home, accessed January 21, 2026, [https://www.sportlogiq.com/](https://www.sportlogiq.com/)  
4. Application and Development of the Expected Goals for Hockey Player Evaluation, accessed January 21, 2026, [https://www.researchgate.net/publication/384315388\_Application\_and\_Development\_of\_the\_Expected\_Goals\_for\_Hockey\_Player\_Evaluation](https://www.researchgate.net/publication/384315388_Application_and_Development_of_the_Expected_Goals_for_Hockey_Player_Evaluation)  
5. Introducing Offensive Sequences and The Hockey Decision Tree ..., accessed January 21, 2026, [https://hockey-graphs.com/2020/03/26/introducing-offensive-sequences-and-the-hockey-decision-tree/](https://hockey-graphs.com/2020/03/26/introducing-offensive-sequences-and-the-hockey-decision-tree/)  
6. 12+ Best NHL Front Office Software Solutions for 2026 | Emerline, accessed January 21, 2026, [https://emerline.com/blog/nhl-front-office-tech-stack](https://emerline.com/blog/nhl-front-office-tech-stack)  
7. Gap Control \- Human Kinetics, accessed January 21, 2026, [https://us.humankinetics.com/blogs/excerpt/gap-control](https://us.humankinetics.com/blogs/excerpt/gap-control)  
8. Sports Analysis with Computer Vision: Pressing Intensity \- Labellerr, accessed January 21, 2026, [https://www.labellerr.com/blog/sports-analysis-with-computer-vision-pressing-intensity/](https://www.labellerr.com/blog/sports-analysis-with-computer-vision-pressing-intensity/)  
9. Do scoring chances and rush chances drive team shooting percentage? \- Blue Seat Blogs, accessed January 21, 2026, [https://blueseatblogs.com/2015/11/16/do-scoring-chances-and-rush-chances-drive-team-shooting-percentage/](https://blueseatblogs.com/2015/11/16/do-scoring-chances-and-rush-chances-drive-team-shooting-percentage/)  
10. RentoSaijo/NHLxG: Expected-goals (xG) model for the NHL \- GitHub, accessed January 21, 2026, [https://github.com/RentoSaijo/NHLxG](https://github.com/RentoSaijo/NHLxG)  
11. Expected Goals \- Methodology | HockeyStats.com, accessed January 21, 2026, [https://hockeystats.com/methodology/expected-goals](https://hockeystats.com/methodology/expected-goals)  
12. Expected Goals Model with Pre-Shot Movement, Part 1: The Model | Hockey Graphs, accessed January 21, 2026, [https://hockey-graphs.com/2019/08/12/expected-goals-model-with-pre-shot-movement-part-1-the-model/](https://hockey-graphs.com/2019/08/12/expected-goals-model-with-pre-shot-movement-part-1-the-model/)  
13. NHL-Shot-Maps \- Kaggle, accessed January 21, 2026, [https://www.kaggle.com/code/elorabrenneman/nhl-shot-maps](https://www.kaggle.com/code/elorabrenneman/nhl-shot-maps)  
14. Analyzing Passing Metrics in Ice Hockey using Puck and Player Tracking Data \- Cheriton School of Computer Science, accessed January 21, 2026, [https://cs.uwaterloo.ca/\~brecht/papers/linhac-2023.pdf](https://cs.uwaterloo.ca/~brecht/papers/linhac-2023.pdf)  
15. Passing and Pressure Metrics in Ice Hockey \- Cheriton School of Computer Science, accessed January 21, 2026, [https://cs.uwaterloo.ca/\~brecht/papers/hockey-aisa-2021.pdf](https://cs.uwaterloo.ca/~brecht/papers/hockey-aisa-2021.pdf)  
16. LINHAC: Visualizing Sportlogiq's Play-By-Play Data \- Hockey-Statistics, accessed January 21, 2026, [https://hockey-statistics.com/2024/05/30/linhac-visualizing-sportlogiqs-play-by-play-data/](https://hockey-statistics.com/2024/05/30/linhac-visualizing-sportlogiqs-play-by-play-data/)  
17. Why the Oilers are struggling in transition, and how they can improve, accessed January 21, 2026, [https://oilersnation.com/news/why-the-oilers-are-struggling-in-transition-and-how-they-can-improve](https://oilersnation.com/news/why-the-oilers-are-struggling-in-transition-and-how-they-can-improve)  
18. Stats I Track \- The Energy Line, accessed January 21, 2026, [https://theenergyline.wordpress.com/stats-i-track/](https://theenergyline.wordpress.com/stats-i-track/)  
19. Measuring the Importance of Individual Player Zone Entry Creation | Hockey Graphs, accessed January 21, 2026, [https://hockey-graphs.com/2017/08/10/measuring-the-importance-of-individual-player-zone-entry-creation/](https://hockey-graphs.com/2017/08/10/measuring-the-importance-of-individual-player-zone-entry-creation/)  
20. Player Cards/FAQ \- All Three Zones, accessed January 21, 2026, [https://www.allthreezones.com/player-cardsfaq.html](https://www.allthreezones.com/player-cardsfaq.html)  
21. A brief guide to hockey's advanced statistics, accessed January 21, 2026, [https://www.secondcityhockey.com/advanced-hockey-statistics-explainer-faqs-walkthroughs/](https://www.secondcityhockey.com/advanced-hockey-statistics-explainer-faqs-walkthroughs/)  
22. General Terms \- Evolving-Hockey, accessed January 21, 2026, [https://evolving-hockey.com/glossary/general-terms/](https://evolving-hockey.com/glossary/general-terms/)  
23. Glossary \- MoneyPuck.com, accessed January 21, 2026, [https://moneypuck.com/glossary.htm](https://moneypuck.com/glossary.htm)  
24. Puck Possession and Net Traffic Metrics in Ice Hockey \- Cheriton School of Computer Science, accessed January 21, 2026, [https://cs.uwaterloo.ca/\~brecht/theses/Pitassi-MMath.pdf](https://cs.uwaterloo.ca/~brecht/theses/Pitassi-MMath.pdf)  
25. Score Adjustments \- Evolving-Hockey, accessed January 21, 2026, [https://evolving-hockey.com/glossary/score-adjustments/](https://evolving-hockey.com/glossary/score-adjustments/)  
26. Expected by Whom? A Skill-Adjusted Expected Goals Model for NHL Shooters and Goaltenders \- arXiv, accessed January 21, 2026, [https://arxiv.org/html/2511.07703v2](https://arxiv.org/html/2511.07703v2)  
27. Mastering Gap Control: The Secret to Elite Defensive Play \- Black Hockey Sticks, accessed January 21, 2026, [https://allblackhockeysticks.com/mastering-gap-control-the-secret-to-elite-defensive-play/](https://allblackhockeysticks.com/mastering-gap-control-the-secret-to-elite-defensive-play/)  
28. Tearse: Understanding gap control \- Minnesota Hockey Magazine, accessed January 21, 2026, [https://minnesotahockeymag.com/tearse-understanding-gap-control/](https://minnesotahockeymag.com/tearse-understanding-gap-control/)  
29. Understanding Forechecking in Hockey: A Key to Defensive Domination \- Wilkes-Barre/Scranton Penguins, accessed January 21, 2026, [https://www.wbspenguins.com/blog/understanding-forechecking-in-hockey/](https://www.wbspenguins.com/blog/understanding-forechecking-in-hockey/)  
30. Data Pipeline Architecture: Key Patterns and Best Practices \- Striim, accessed January 21, 2026, [https://www.striim.com/blog/data-pipeline-architecture-key-patterns-and-best-practices/](https://www.striim.com/blog/data-pipeline-architecture-key-patterns-and-best-practices/)  
31. Live Game Tracking \- Sportradar's APIs, accessed January 21, 2026, [https://developer.sportradar.com/ice-hockey/docs/nhl-ig-live-game-retrieval](https://developer.sportradar.com/ice-hockey/docs/nhl-ig-live-game-retrieval)  
32. A Comprehensive Guide to Data Pipeline Architecture for Data Analysts | Integrate.io, accessed January 21, 2026, [https://www.integrate.io/blog/guide-to-data-pipeline-architecture/](https://www.integrate.io/blog/guide-to-data-pipeline-architecture/)  
33. iCE Features \- Sportlogiq, accessed January 21, 2026, [https://www.sportlogiq.com/ice-features/](https://www.sportlogiq.com/ice-features/)  
34. Why Rush Scoring Chances Are Important \- YouTube, accessed January 21, 2026, [https://www.youtube.com/watch?v=jzXzSICU\_tI](https://www.youtube.com/watch?v=jzXzSICU_tI)  
35. accessed January 21, 2026, [https://sid813.substack.com/p/oilers-microstat-tracking-glossary\#:\~:text=Zone%20Entries,-To%20win%20hockey\&text=Zone%20entry%20attempts%20can%20be,%2Dins)%20and%20pass%20entries.](https://sid813.substack.com/p/oilers-microstat-tracking-glossary#:~:text=Zone%20Entries,-To%20win%20hockey&text=Zone%20entry%20attempts%20can%20be,%2Dins\)%20and%20pass%20entries.)  
36. Where not to lose the puck \- IDA.LiU.SE, accessed January 21, 2026, [https://www.ida.liu.se/research/sportsanalytics/LINHAC/LINHAC22/papers/linhac22-final58.pdf](https://www.ida.liu.se/research/sportsanalytics/LINHAC/LINHAC22/papers/linhac22-final58.pdf)  
37. Primer: Advanced analytics in hockey made simple \- DK Pittsburgh Sports, accessed January 21, 2026, [https://www.dkpittsburghsports.com/2020/10/05/hockey-advanced-analytics-stats-corsi-definition-tlh](https://www.dkpittsburghsports.com/2020/10/05/hockey-advanced-analytics-stats-corsi-definition-tlh)  
38. Evolving Hockey Overview, accessed January 21, 2026, [https://evolving-hockey.com/evolving-hockey-overview/](https://evolving-hockey.com/evolving-hockey-overview/)  
39. CAROLINA HURRICANES \- CANES PR, accessed January 21, 2026, [https://canespr.com/wp-content/uploads/2024/05/clips050524.pdf](https://canespr.com/wp-content/uploads/2024/05/clips050524.pdf)  
40. NHL EDGE stats: Biggest storylines of 2025, accessed January 21, 2026, [https://www.nhl.com/news/nhl-edge-stats-trends-and-storylines-for-2025](https://www.nhl.com/news/nhl-edge-stats-trends-and-storylines-for-2025)  
41. Passing and Pressure Metrics in Ice Hockey \- ResearchGate, accessed January 21, 2026, [https://www.researchgate.net/publication/352465415\_Passing\_and\_Pressure\_Metrics\_in\_Ice\_Hockey](https://www.researchgate.net/publication/352465415_Passing_and_Pressure_Metrics_in_Ice_Hockey)