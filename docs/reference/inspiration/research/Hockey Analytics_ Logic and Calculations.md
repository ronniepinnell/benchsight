## ---

**1\. Sequence & Possession Logic**

To move from event counting to sequence modeling, you must implement a "State Machine" logic in your ETL process.

### **The Hierarchy of Action**

* **Play (Atomic):** A single event ($Event\_n$) with $(x, y, t)$.  
* **Sequence (Group):** A chain of plays $\\{Event\_1, Event\_2, ... Event\_n\\}$ where the Possession\_Owner remains constant.  
* **Rush (Sub-Type):** A Sequence that includes a Zone\_Entry and a Shot\_Attempt within 5 seconds.

### **State Transition Definitions**

* **Possession Gain:** Triggered by Takeaway, Recovery, or Won Faceoff.  
* **Possession Loss:** Triggered by Giveaway, Missed Shot (that results in a recovery by the opponent), or Whistle.  
* **The "5-Second Rule" (Rush Logic):**  
  $$Is\\\_Rush \= (Time\_{Shot} \- Time\_{Zone\\\_Entry}) \\leq 5.0s$$

  If the time exceeds 5 seconds, the transition attack is "broken," and the play becomes a "Cycle" or "Set Play."

## ---

**2\. Advanced Performance Calculations**

These are the core formulas for your analytics engine.

### **A. Royal Road Expected Goals (RR-xG)**

Standard xG models are purely spatial. For a "Sportlogiq-grade" model, you need a **Pre-Shot Movement Multiplier**.

* **Logic:** If a pass crosses the vertical midline of the Offensive Zone within **2 seconds** of the shot.  
* **Formula:**  
  $$xG\_{Total} \= xG\_{Baseline} \\times \\text{Multiplier}(2.5)$$  
* **Why:** Forcing the goalie to move laterally across the "Royal Road" decreases their save percentage by over **20%**.

### **B. Transition Efficiency (TE)**

This evaluates how well your team moves from defense to offense.

* **Calculation:**  
  $$TE \= \\frac{\\text{Successful Zone Entries}}{\\text{Total Possession Gains in Defensive Zone}}$$  
* **Description:** High-performing teams minimize "dump-and-chase" in favor of controlled entries.

### **C. Defensive Impact (Strips/Takeaways)**

Your colleague started with a weight of **0.12 xgf\_impact** for a Strip. We should formalize the **Possession Value Added (PVA)**:

* **PVA Calculation:**  
  $$PVA \= xG\_{Sequence\\\_After\\\_Action} \- xG\_{Expected\\\_Against\\\_If\\\_Lost}$$

## 

# ---

**Hockey Analytics: Commercial-Grade Performance Engine**

## **1\. Core Tactical Hierarchy**

To move beyond basic box-score stats, the data must be organized into a state-based hierarchy.

* **Play (Atomic Unit):** A single action (Pass, Shot, Hit) with a $(x, y)$ coordinate, timestamp $t$, and player ID.  
* **Sequence (The Possession):** A continuous chain of controlled plays by one team.  
  * **Start:** Triggered by a "Gain" event (e.g., Takeaway, Recovery, Won Faceoff).  
  * **End:** Triggered by a "Loss" event (e.g., Giveaway, Goal, Period End, or Whistle).  
* **Rush (Transition):** A sequence that moves the puck into the Offensive Zone with speed, resulting in a shot within a **5-second** window of entry.  
* **Cycle (Sustained O-Zone):** An offensive sequence where the team maintains possession in the O-Zone for longer than 5 seconds without a "Rush" transition.  
* **Scoring Change:** A distinct shift in the game's Expected Goals ($xG$) probability, often caused by a high-danger event like a "Royal Road" pass.

## ---

**2\. Advanced Performance Formulas**

These calculations represent the high-level modeling used by Sportlogiq and NHL front offices.

### **Expected Goals ($xG$) with Pre-Shot Movement**

Most models are purely spatial. A performance-grade model must account for goalie movement.

$$xG \\approx \\sigma(\\beta\_0 \+ \\beta\_1 \\cdot \\text{Dist} \+ \\beta\_2 \\cdot \\text{Angle} \+ \\beta\_3 \\cdot \\text{Movement\\\_Multiplier})$$

* **The Royal Road:** If the puck crosses the vertical midline of the ice within **2 seconds** of the shot, apply a **2.5x multiplier** to the baseline $xG$. This accounts for the goalie's lateral tracking difficulty.

### **Possession Value Added (PVA)**

This measures the specific impact of "micro-stats" like Strips or Zone Exits.

$$PVA \= xG\_{\\text{post-event}} \- xG\_{\\text{pre-event}}$$

* **Neutral Zone Strip:** If a strip (weighted at **0.12**) leads to a **Rush**, the PVA captures the massive jump in scoring probability from a defensive state to a high-danger transition state.

### **Expected Primary Assists ($xA$)**

$$xA \= \\sum xG(\\text{Shots generated from passes})$$

* This credits playmakers for the quality of the chance they created, regardless of whether the shooter finishes the play.

## ---

**3\. Data Structure & ETL Logic**

To implement this, your data warehouse (BigQuery/Snowflake) should map events into a fact\_sequences table.

| Data Layer | Mapping Logic |
| :---- | :---- |
| **Sequence ID** | Use a window function: PARTITION BY team\_id ORDER BY timestamp. |
| **Rush Flag** | IF (shot\_time \- entry\_time) \< 5s THEN TRUE ELSE FALSE. |
| **Lane Break** | IF (pass\_y\_start \* pass\_y\_end) \< 0 THEN TRUE (Crosses Royal Road). |
| **Defensive Impact** | Roll up all Takeaways and Strips within a sequence to assign a total PVA\_Score to the defender. |

## ---

**4\. Research Manifest (links.md)**

* [**The Royal Road \- Valiquette**](https://www.google.com/search?q=https://vimeo.com/112616147)**:** Foundational video research on how cross-slot movement breaks defensive structures.  
* [**Evolving Hockey xG Documentation**](https://evolving-hockey.com/)**:** Deep dive into the coefficients and logic used for public-facing NHL models.  
* [**Hockey-Graphs: Sequence Slicing**](https://hockey-graphs.com/)**:** Technical articles on programmatically defining possessions in play-by-play data.  
* [**Sportlogiq Performance Blogs**](https://www.google.com/search?q=https://sportlogiq.com/blog/)**:** Insights into professional-grade tracking of "Line of Sight" and "Lane Breaking" passes.

As a performance data scientist with a background in the high-level environments of Sportlogiq and the NHL, I recognize that your colleague has already laid a sophisticated foundation with weighted micro-stats (e.g., the 0.12 xgf\_impact for a Strip) and game-state logic (strategy\_mode in dim\_situation.csv).

To elevate this to a "Sportlogiq-grade" commercial engine, we need to move from discrete event counting to **sequential flow modeling**. Here is the deep-dive research plan and the definitions required to bridge the gap between "standard stats" and "performance analytics."

## ---

**1\. Deep-Dive Research & Execution Plan**

### **Phase I: The "State-Space" Audit (What we have vs. What we need)**

* **Audit Existing Dims:** Review dim\_takeaway\_type and dim\_situation. We have the *outcome* weights (Strips/Recoveries) and the *context* (Strategy Mode).  
* **Identify Gaps:** We are likely missing **Spatial Metadata** (X,Y coordinates for every event) and **Temporal Context** (the time elapsed between events in a sequence). Without these, we cannot calculate "Rush" or "Passing Lane" metrics.  
* **The "Play-to-Sequence" Mapping:** We must convert the flat dim\_takeaway table into a relational sequence table where every event is linked to a possession\_id.

### **Phase II: The Logic & Calculation Engine**

* **Derive Logic:** Build the "Pre-Shot Movement" logic. A shot's value isn't just its location; it’s the **Sequence** that preceded it (e.g., a Royal Road pass increases xG by \~2.5x).  
* **Metric Replication:** Implement formulas for **Expected Goals (xG)**, **Expected Goals Contribution (xGC)**, and **Possession Value (PV)**.

## ---

**2\. Defining the Core "Hockey Logic"**

In high-level performance systems, these terms are not interchangeable; they are hierarchical.

| Term | Definition | Logic / Formula |
| :---- | :---- | :---- |
| **Play** | The smallest unit of data. A discrete action with a timestamp and a player ID. | $Play \= \\{Event\\\_Type, Player, Coord(x,y), Time\\}$ |
| **Sequence** | A continuous chain of possession. It starts when a team gains control (Recovery/Takeaway) and ends when they lose it or play stops. | $\\sum\_{t\_{start}}^{t\_{end}} Plays$ where $Possession\\\_Owner \= Constant$ |
| **Rush** | A transition event where the offensive team crosses the blue line with speed and generates a shot attempt within a specific time window (usually \<5s). | $Event(ZoneEntry) \\rightarrow Shot(t \< 5.0s)$ |
| **Scoring Chance** | Any unblocked shot attempt originating from the "Home Plate" area (Slot/Inner Slot) or a shot preceded by a "High Danger" event (Pass across midline/Rebound). | $Shot \\in Area(Slot) \\lor Event(Rebound/Rush)$ |

## ---

**3\. High-Level Performance Calculations**

To append your colleague's work, we need to define the formulas for the analytics dashboard.

### **A. Expected Goals (xG)**

We don't just use location. The "Sportlogiq" way includes:

$$xG \= f(Distance, Angle, Shot\\\_Type, Pre\\\_Shot\\\_Movement, Rush\\\_Flag, Rebound\\\_Flag)$$

* **Pre-Shot Movement:** Did the puck cross the "Royal Road" (the line splitting the ice lengthwise) within 2 seconds of the shot?  
* **Rush Flag:** Is the shot part of a defined "Rush" sequence?

### **B. Possession Value (PV) / Impact**

Your colleague started this with xgf\_impact. We should expand this to every event in a sequence.

* **Calculation:** For every Play in a Sequence, calculate the delta in xG for that possession.  
* **Example:** A **Strip (0.12)** in the Neutral Zone is more valuable than a **Recovery (0.03)** because it typically creates a **Rush** opportunity.

## ---

**4\. Appending the Reference Folder**

I will supplement the benchsight\_master\_doc.rtf with a new sequence\_logic\_manifest.md that includes:

* **Possession State Machine:** Logic to define when a sequence begins (e.g., 50/50 puck win vs. direct turnover).  
* **The "Royal Road" Mapping:** Logic to flag passes that cross the middle of the ice in the Offensive Zone.  
* **Pressure Metrics:** Calculating the distance of the nearest defender to the puck carrier during a "Play."

Would you like me to start writing the SQL or Python logic to group your existing event data into these "Sequences" and "Rushes"?

---

Introduction to Hockey Analytics  
This video provides a foundational overview of how rush scoring chances and advanced transition metrics are defined and tracked in professional hockey, which is central to building your project's performance models.  
To build a commercial-grade engine comparable to Sportlogiq or the NHL’s proprietary systems, we must move beyond counting events and start modeling **state transitions**.

Below is the technical logic, definitions, and formulas required to transform your raw event data into a performance-tracking system. I have structured this to be appended directly to your project documentation.

## ---

**1\. Tactical Definitions & "The State Machine"**

In high-level analytics, a hockey game is a series of **Possessions** consisting of **Sequences**, which are made up of individual **Plays**.

### **The Possession Sequence**

* **Definition:** A continuous chain of controlled actions by one team.  
* **Start Logic:** Triggered by a "Gain Possession" event (Takeaway, Recovery, Won Faceoff, or Controlled Entry).  
* **End Logic:** Triggered by a "Loss of Possession" (Giveaway, Missed Shot, Frozen Puck, or Period End).  
* **Calculation:** Possession\_Duration \= Time(End\_Event) \- Time(Start\_Event).

### **The "Rush" (Transition Attack)**

* **Definition:** A specific type of sequence where the team moves the puck from the Defensive or Neutral Zone into the Offensive Zone with speed, leading to a shot.  
* **Logic:**  
  * Event(Zone\_Entry) where Entry\_Type \= 'Controlled'.  
  * Event(Shot\_Attempt) occurs within **5 seconds** of the entry.  
  * The defending team must not have "set" their defensive structure (often measured by the number of defenders between the puck and the net).

### **Scoring Chance (High Danger)**

* **Definition:** Any shot attempt that has a statistically high probability of resulting in a goal based on location and pre-shot movement.  
* **Logic:** If (Shot\_Location \= 'Inner Slot') OR (Shot\_Preceded\_By \= 'Royal Road Pass') OR (Shot\_Preceded\_By \= 'Rebound') THEN 'High Danger'.

## ---

**2\. Advanced Performance Calculations**

These formulas define the "Value" added by a player beyond simple goals and assists.

### **A. Expected Goals (xG) \- The Multi-Variable Model**

Unlike basic models, a "Sportlogiq-style" model uses a gradient-boosted tree (XGBoost) or logistic regression on the following:

$$xG \\approx \\sigma(\\beta\_0 \+ \\beta\_1 \\cdot Dist \+ \\beta\_2 \\cdot Angle \+ \\beta\_3 \\cdot PreShotMovement \+ \\beta\_4 \\cdot RushFlag)$$

* **Pre-Shot Movement (The Royal Road):** If the puck crosses the imaginary line splitting the ice lengthwise in the offensive zone, the $xG$ multiplier is typically **2.0x to 2.5x**.  
* **Shot Type:** Slap shots from the point have lower $xG$ than snap shots from the slot, even if the distance is similar, due to "time to react" for the goalie.

### **B. Possession Value Added (PVA)**

This measures how much a specific action (like the "Strips" your colleague noted) increases the team's chance of scoring during that sequence.

* **Formula:** $PVA \= xG\_{after\\\_event} \- xG\_{before\\\_event}$  
* **Logic:** If a player performs a **Strip** in the Neutral Zone, they have transitioned the "State" from *Defensive* to *Transition*. The PVA is the difference in the team's probability of scoring from that new state.

### **C. Expected Primary Assists (xA)**

* **Formula:** The $xG$ value of the shot resulting from a pass.  
* **Description:** This rewards playmakers regardless of whether the shooter actually scores.

## ---

**3\. Data Structure Logic (For ETL)**

To replicate these, your data warehouse needs a fact\_sequences table that rolls up your fact\_events.

| Column | Logic / Transformation |
| :---- | :---- |
| sequence\_id | UUID generated for every new possession gain. |
| is\_rush | Boolean: TRUE if Entry\_to\_Shot\_Time \< 5.0s. |
| is\_royal\_road | Boolean: TRUE if Pass\_X\_Start \* Pass\_X\_End \< 0 (Crosses midline). |
| sequence\_xg | SUM(event\_xg) for all shots within that sequence. |

## ---

**4\. Appending links.md**

Add these references to your project to ground your formulas in industry standards:

* [**The Royal Road \- Steve Valiquette**](https://www.google.com/search?q=Steve+Valiquette+Royal+Road+Analytics)**:** The foundational theory on why cross-slot passes are the most dangerous plays in hockey.  
* [**Passing Lane Analytics (Sportlogiq)**](https://www.google.com/search?q=https://sportlogiq.com/blog/)**:** Research on "Line of Sight" and "Lane Breaking" passes.  
* [**Evolving Hockey \- xG Model Documentation**](https://evolving-hockey.com/)**:** Deep dive into the coefficients used for standard NHL xG models.  
* [**Hockey Graphs \- Expected Primary Assists**](https://hockey-graphs.com/)**:** Technical breakdown of xA and shot 

## ---

**1\. Defining the Performance Hierarchy**

To model hockey effectively, you must group raw events into logical buckets.

### **The "Play" (Level 1: Atomic)**

* **Definition:** A single discrete action (Pass, Shot, Hit, Block) performed by one player at a specific $(x, y)$ coordinate and timestamp $t$.  
* **Logic:** Every row in your fact\_events table is a Play.

### **The "Sequence" (Level 2: Chain of Events)**

* **Definition:** A continuous chain of controlled events by one team. A sequence ends when the other team gains "Control" (not just a touch) or play stops.  
* **Start Trigger:** Takeaway, Recovery, Won Faceoff, or Controlled Entry.  
* **End Trigger:** Giveaway, Frozen Puck, Goal, or Change of Possession.  
* **Calculation:** Sequence\_ID is a window function partitioning by Team\_ID and ordered by $t$, resetting whenever a "Loss of Possession" event occurs.

### **The "Rush" (Level 3: Transition Attack)**

* **Definition:** An offensive sequence originating in the Defensive or Neutral zone that crosses the blue line with speed and results in a shot attempt before the defense can "set."  
* **Data Logic:**  
  * Event(Zone\_Entry) where Entry\_Type \= 'Controlled' (Carry or Pass).  
  * Time\_Delta(Shot\_Attempt \- Zone\_Entry) \< 5.0 seconds.  
  * If Time\_Delta \> 5.0s, it is classified as a **"Cycle"** play rather than a Rush.

## ---

**2\. Advanced Performance Calculations**

### **Expected Goals (xG)**

In high-level models, we use a logistic regression or XGBoost model where:

$$xG \= f(\\text{Distance, Angle, Shot\\\_Type, Pre\\\_Shot\\\_Movement, Rush\\\_Flag, Rebound\\\_Flag})$$

* **Logic for Pre-Shot Movement:** This is the most critical commercial-grade feature. If the puck crosses the "Royal Road" (the vertical midline of the ice) within 2 seconds of the shot, the $xG$ value is often multiplied by **2.5x** because the goalie must track across the center line, opening holes.

### **Expected Primary Assists (xA)**

* **Definition:** The $xG$ value of a shot, credited to the player who made the last completed pass (the "Shot Assist").  
* **Logic:** xA \= xG(Target\_Shot) if Pass\_Completed \= TRUE. This measures a playmaker's ability to create high-quality chances, independent of whether their teammate actually scores.

### **Possession Value Added (PVA)**

This is how Sportlogiq evaluates a "Strip" or a "Zone Exit."

* **Formula:** $PVA \= xG\_{\\text{post-event}} \- xG\_{\\text{pre-event}}$  
* **Description:** It measures how much an action increased the team's probability of scoring in that sequence. A "Neutral Zone Strip" has high PVA because it creates a **Rush** opportunity where the opposition is out of position.

## ---

**3\. Updated links.md References**

Add these to your project for the research depth requested:

* [**Offensive Sequences & The Decision Tree**](https://hockey-graphs.com/2020/03/26/introducing-offensive-sequences-and-the-hockey-decision-tree/)**:** This is the gold standard for defining how to "slice" a hockey game into sequences.  
* [**Expected Primary Assists Framework**](https://github.com/danmorse314/Expected-Primary-Assists)**:** Technical breakdown of how to weight passes based on their probability of becoming a goal.  
* [**Identifying Team Playing Styles (Clustering)**](https://hockey-graphs.com/2017/05/15/identifying-team-playing-styles-with-clustering/)**:** How to use "Rush" vs "Probing" (Cycle) data to define a team's tactical identity.  
* [**CSA Hockey Glossary**](https://www.csahockey.com/glossary)**:** High-level definitions for "Odd Man Rushes" and "Quality Shot Counts" used by pro scouts.

## 