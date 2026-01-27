# BenchSight Commercial Roadmap Visuals

**Visual diagrams for market positioning, revenue projections, and feature comparison**

Last Updated: 2026-01-21
Version: 2.00

---

## Market Positioning Map

### Price vs Features Positioning

```mermaid
graph LR
    subgraph HighPrice["High Price"]
        SP[Sportlogiq<br/>$50K+/year]
        IN[InStat<br/>$10-30K/year]
        SY[Synergy<br/>$15-40K/year]
    end
    
    subgraph MediumPrice["Medium Price"]
        HU[Hudl<br/>$1.5-3K/year]
    end
    
    subgraph LowPrice["Low Price"]
        BS[BenchSight<br/>$0.5-2K/year]
        IC[Iceberg<br/>$0.5-1.5K/year]
    end
    
    subgraph BasicFeatures["Basic Features"]
        IC
        HU
    end
    
    subgraph AdvancedFeatures["Advanced Features"]
        SP
        IN
        SY
        BS
    end
    
    style BS fill:#00ff88
    style SP fill:#ff4444
    style IN fill:#ff4444
    style SY fill:#ff4444
    style HU fill:#ff8800
    style IC fill:#aa66ff
```

**Positioning:**
- **BenchSight:** Advanced features at low price (sweet spot)
- **Professional platforms:** Advanced features at high price
- **Youth platforms:** Basic features at medium price

---

## Revenue Projection Chart

### Revenue Growth Timeline

```mermaid
gantt
    title Revenue Projection (Realistic Scenario)
    dateFormat YYYY-MM-DD
    section Year 1
    Launch & Beta           :2026-03-01, 3M
    Q1 Revenue $10K         :rev1, 2026-03-01, 3M
    Q2 Revenue $20K         :rev2, 2026-06-01, 3M
    Q3 Revenue $30K         :rev3, 2026-09-01, 3M
    Q4 Revenue $40K         :rev4, 2026-12-01, 3M
    
    section Year 2
    Q1 Revenue $60K         :rev5, 2027-03-01, 3M
    Q2 Revenue $80K         :rev6, 2027-06-01, 3M
    Q3 Revenue $100K        :rev7, 2027-09-01, 3M
    Q4 Revenue $120K        :rev8, 2027-12-01, 3M
```

### Customer Growth Projection

```mermaid
graph LR
    A[Month 0<br/>0 teams] --> B[Month 6<br/>50 teams]
    B --> C[Month 12<br/>150 teams]
    C --> D[Month 18<br/>300 teams]
    D --> E[Month 24<br/>500 teams]
    
    style A fill:#ff4444
    style B fill:#ff8800
    style C fill:#00d4ff
    style D fill:#00ff88
    style E fill:#00ff88
```

### MRR Growth Projection

```mermaid
graph TD
    A[Month 0<br/>$0 MRR] --> B[Month 6<br/>$3,550 MRR]
    B --> C[Month 12<br/>$11,150 MRR]
    C --> D[Month 18<br/>$22,500 MRR]
    D --> E[Month 24<br/>$38,750 MRR]
    
    F[Break-Even<br/>$3,200/month] -.->|Month 6| B
    
    style A fill:#ff4444
    style B fill:#00ff88
    style C fill:#00d4ff
    style D fill:#00d4ff
    style E fill:#00ff88
    style F fill:#ff8800
```

---

## Feature Comparison Matrix

### Us vs Competitors

```mermaid
graph TB
    subgraph Features["Feature Comparison"]
        BS[BenchSight]
        SP[Sportlogiq]
        IN[InStat]
        SY[Synergy]
        HU[Hudl]
    end
    
    subgraph Advanced["Advanced Analytics"]
        BS -->|[YES] xG, WAR/GAR| ADV1
        SP -->|[YES] xG, WAR/GAR| ADV1
        IN -->|[PARTIAL] Limited| ADV2
        SY -->|[YES] xG, WAR/GAR| ADV1
        HU -->|[NO] Basic only| ADV3
    end
    
    subgraph Pricing["Pricing"]
        BS -->|[YES] $0.5-2K/year| PRICE1
        SP -->|[NO] $50K+/year| PRICE3
        IN -->|[NO] $10-30K/year| PRICE3
        SY -->|[NO] $15-40K/year| PRICE3
        HU -->|[PARTIAL] $1.5-3K/year| PRICE2
    end
    
    subgraph Market["Target Market"]
        BS -->|[YES] Youth/Junior| MKT1
        SP -->|[NO] Professional| MKT3
        IN -->|[NO] Professional| MKT3
        SY -->|[NO] College/Pro| MKT2
        HU -->|[YES] Youth/HS| MKT1
    end
    
    style BS fill:#00ff88
    style SP fill:#ff4444
    style IN fill:#ff4444
    style SY fill:#ff4444
    style HU fill:#ff8800
```

### Feature Parity Analysis

| Feature Category | BenchSight | Sportlogiq | InStat | Synergy | Hudl | Gap |
|-----------------|------------|-----------|--------|---------|------|-----|
| **Core Analytics** | [YES] | [YES] | [YES] | [YES] | [YES] | None |
| **Advanced Metrics** | [YES] | [YES] | [PARTIAL] | [YES] | [NO] | Advantage |
| **ML/CV Automation** | [PLANNED] | [YES] | [PARTIAL] | [YES] | [NO] | **Gap** |
| **Video Storage** | [PLANNED] | [YES] | [YES] | [YES] | [YES] | **Gap** |
| **Mobile Apps** | [PLANNED] | [YES] | [YES] | [YES] | [YES] | **Gap** |
| **Ease of Use** | [YES] | [NO] | [NO] | [NO] | [YES] | Advantage |
| **Pricing** | [YES] | [NO] | [NO] | [NO] | [PARTIAL] | Advantage |
| **Youth Focus** | [YES] | [NO] | [NO] | [NO] | [YES] | Advantage |

**Key Insights:**
- **Advantages:** Advanced analytics, pricing, ease of use, youth focus
- **Gaps:** ML/CV automation, video storage, mobile apps (acceptable for MVP)

---

## Competitive Positioning

### Value Proposition Map

```mermaid
quadrantChart
    title Competitive Positioning
    x-axis Low Price --> High Price
    y-axis Basic Features --> Advanced Features
    quadrant-1 Premium
    quadrant-2 Value Leader
    quadrant-3 Budget
    quadrant-4 Overpriced
    BenchSight: [0.3, 0.9]
    Sportlogiq: [0.95, 0.95]
    InStat: [0.7, 0.8]
    Synergy: [0.8, 0.9]
    Hudl: [0.5, 0.3]
    Iceberg: [0.2, 0.2]
```

**Positioning:**
- **BenchSight:** Value Leader (advanced features, low price)
- **Professional platforms:** Premium (advanced features, high price)
- **Hudl:** Budget (basic features, medium price)
- **Iceberg:** Budget (basic features, low price)

---

## Revenue Model Visualization

### Revenue Streams

```mermaid
graph TD
    A[Revenue Streams] --> B[Subscription Revenue]
    A --> C[Add-On Revenue]
    A --> D[Enterprise Revenue]
    
    B --> B1[Free Tier<br/>$0/month<br/>Acquisition]
    B --> B2[Team Tier<br/>$50/month<br/>Primary]
    B --> B3[Pro Tier<br/>$150/month<br/>Growth]
    B --> B4[Enterprise<br/>Custom<br/>Scale]
    
    C --> C1[Additional Teams<br/>$25/team/month]
    C --> C2[Video Storage<br/>$10/100GB/month]
    C --> C3[API Access<br/>$50/month]
    C --> C4[Custom Reports<br/>$100 one-time]
    
    D --> D1[League Deals<br/>$500-2000/month]
    D --> D2[White-Label<br/>Custom pricing]
    D --> D3[On-Premise<br/>Custom pricing]
    
    style B fill:#00ff88
    style C fill:#00d4ff
    style D fill:#aa66ff
```

### Customer Lifetime Value Flow

```mermaid
graph LR
    A[Customer Acquisition<br/>CAC: $140] --> B[Month 1-3<br/>$75/month<br/>$225 total]
    B --> C[Month 4-12<br/>$75/month<br/>$675 total]
    C --> D[Month 13-24<br/>$75/month<br/>$900 total]
    D --> E[LTV: $1,800<br/>Margin: $1,440]
    
    E --> F[LTV:CAC Ratio<br/>10.3:1]
    
    style A fill:#ff4444
    style B fill:#ff8800
    style C fill:#00d4ff
    style D fill:#00ff88
    style E fill:#00ff88
    style F fill:#00ff88
```

---

## Go-to-Market Timeline

### Marketing & Sales Funnel

```mermaid
graph TD
    A[Market Awareness] --> B[Lead Generation]
    B --> C[Qualification]
    C --> D[Demo/Trial]
    D --> E[Proposal]
    E --> F[Close]
    F --> G[Onboarding]
    G --> H[Activation]
    H --> I[Expansion]
    I --> J[Retention]
    
    A -->|Content Marketing| A1[Blog, Social Media]
    A -->|Paid Ads| A2[Google, Facebook]
    A -->|Partnerships| A3[Leagues, Orgs]
    
    B -->|5% conversion| B1[1000 visitors → 50 leads]
    C -->|60% qualified| C1[50 leads → 30 qualified]
    D -->|40% trial| D1[30 qualified → 12 trials]
    E -->|50% proposal| E1[12 trials → 6 proposals]
    F -->|40% close| F1[6 proposals → 2.4 customers]
    
    style A fill:#00d4ff
    style B fill:#00d4ff
    style C fill:#00d4ff
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#00ff88
    style G fill:#00ff88
    style H fill:#00ff88
    style I fill:#00ff88
    style J fill:#00ff88
```

### Customer Acquisition Channels

```mermaid
pie title Customer Acquisition by Channel (Year 1)
    "Content Marketing" : 30
    "Referrals" : 25
    "Paid Ads" : 20
    "Partnerships" : 15
    "Direct Sales" : 10
```

---

## Pricing Tiers Comparison

### Feature Matrix by Tier

```mermaid
graph TB
    subgraph Free["Free Tier - $0/month"]
        F1[1 Team]
        F2[Basic Stats]
        F3[5 Games/Month]
        F4[Limited Support]
    end
    
    subgraph Team["Team Tier - $50/month"]
        T1[1 Team]
        T2[All Stats]
        T3[Unlimited Games]
        T4[Advanced Metrics]
        T5[Export]
        T6[Email Support]
    end
    
    subgraph Pro["Pro Tier - $150/month"]
        P1[5 Teams]
        P2[All Team Features]
        P3[Custom Reports]
        P4[API Access]
        P5[Priority Support]
        P6[10 Users]
    end
    
    subgraph Enterprise["Enterprise - Custom"]
        E1[Unlimited Teams]
        E2[All Pro Features]
        E3[White-Label]
        E4[Dedicated Support]
        E5[Custom Integrations]
        E6[SLA]
    end
    
    Free --> Team
    Team --> Pro
    Pro --> Enterprise
    
    style Free fill:#ff4444
    style Team fill:#ff8800
    style Pro fill:#00d4ff
    style Enterprise fill:#00ff88
```

---

## Break-Even Analysis

### Revenue vs Costs Timeline

```mermaid
gantt
    title Break-Even Analysis (Realistic Scenario)
    dateFormat YYYY-MM-DD
    section Revenue
    MRR Growth          :2026-03-01, 12M
    section Costs
    Infrastructure      :crit, cost1, 2026-03-01, 12M
    Marketing           :crit, cost2, 2026-03-01, 12M
    Support             :cost3, 2026-03-01, 12M
    section Break-Even
    Break-Even Point    :milestone, be, 2026-08-01, 0d
    section Profitability
    Profitable          :2026-08-01, 5M
```

### Monthly Revenue vs Costs

```mermaid
graph LR
    subgraph Month1["Month 1"]
        R1[Revenue: $500]
        C1[Costs: $3,200]
        L1[Loss: $2,700]
    end
    
    subgraph Month6["Month 6"]
        R6[Revenue: $3,550]
        C6[Costs: $3,200]
        P6[Profit: $350]
    end
    
    subgraph Month12["Month 12"]
        R12[Revenue: $11,150]
        C12[Costs: $3,200]
        P12[Profit: $7,950]
    end
    
    Month1 --> Month6
    Month6 --> Month12
    
    style R1 fill:#ff4444
    style C1 fill:#ff4444
    style L1 fill:#ff4444
    style R6 fill:#00ff88
    style C6 fill:#ff8800
    style P6 fill:#00ff88
    style R12 fill:#00ff88
    style C12 fill:#ff8800
    style P12 fill:#00ff88
```

---

## Market Opportunity

### Total Addressable Market (TAM)

```mermaid
graph TD
    A[Total Addressable Market] --> B[Youth Hockey Teams<br/>~50,000 teams in US]
    A --> C[Junior Hockey Teams<br/>~5,000 teams in US]
    A --> D[College Club Teams<br/>~2,000 teams in US]
    
    B --> B1[Target: 1% = 500 teams<br/>Revenue: $25K-50K/month]
    C --> C1[Target: 5% = 250 teams<br/>Revenue: $12.5K-37.5K/month]
    D --> D1[Target: 10% = 200 teams<br/>Revenue: $10K-30K/month]
    
    B1 --> E[Total Target Market<br/>950 teams<br/>$47.5K-117.5K/month]
    C1 --> E
    D1 --> E
    
    style A fill:#00d4ff
    style B fill:#00ff88
    style C fill:#00ff88
    style D fill:#00ff88
    style E fill:#00ff88
```

### Market Penetration Strategy

```mermaid
graph LR
    A[Year 1<br/>0.1% Penetration<br/>50 teams] --> B[Year 2<br/>0.3% Penetration<br/>150 teams]
    B --> C[Year 3<br/>0.6% Penetration<br/>300 teams]
    C --> D[Year 5<br/>1.5% Penetration<br/>750 teams]
    
    A --> A1[Focus: Early Adopters]
    B --> B1[Focus: Growth Markets]
    C --> C1[Focus: Scale]
    D --> D1[Focus: Market Leader]
    
    style A fill:#ff8800
    style B fill:#00d4ff
    style C fill:#00ff88
    style D fill:#00ff88
```

---

## Related Documentation

- [COMPETITOR_ANALYSIS.md](COMPETITOR_ANALYSIS.md) - Detailed competitor analysis
- [MONETIZATION_STRATEGY.md](MONETIZATION_STRATEGY.md) - Complete monetization strategy
- [GAP_ANALYSIS.md](GAP_ANALYSIS.md) - Gap analysis and priorities

---

*Last Updated: 2026-01-15*
