# Technical Diagrams for Patent Application

## Diagram 1: System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PROXIMA SYSTEM                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────┐         ┌──────────────────┐                   │
│  │  Experiment    │────────▶│  Data Ingestion  │                   │
│  │  Platform      │         │     Module       │                   │
│  │  (External)    │         └────────┬─────────┘                   │
│  └────────────────┘                  │                              │
│                                      ▼                              │
│                          ┌───────────────────────┐                 │
│                          │  Historical Experiment │                 │
│                          │  Data Store            │                 │
│                          │  - Treatment assignments│                 │
│                          │  - Segment attributes  │                 │
│                          │  - Proxy measurements  │                 │
│                          │  - Long-term outcomes  │                 │
│                          └───────────┬───────────┘                 │
│                                      │                              │
│         ┌────────────────────────────┼────────────────────────┐    │
│         │                            │                        │    │
│         ▼                            ▼                        ▼    │
│  ┌─────────────┐          ┌──────────────────┐    ┌──────────────┐│
│  │  Treatment  │          │  Proxy Scoring   │    │  Fragility   ││
│  │  Effect     │          │  Module          │    │  Detection   ││
│  │  Estimation │          │  - Correlation   │    │  Module      ││
│  │  Module     │          │  - Directional   │    │  - Sign flips││
│  │             │          │  - Fragility     │    │  - Segment   ││
│  └──────┬──────┘          │  - Composite     │    │    analysis  ││
│         │                 └────────┬─────────┘    └──────┬───────┘│
│         │                          │                     │        │
│         └──────────────────────────┼─────────────────────┘        │
│                                    ▼                               │
│                        ┌───────────────────────┐                  │
│                        │  Decision Simulation  │                  │
│                        │  Module               │                  │
│                        │  - Win rate           │                  │
│                        │  - False pos/neg      │                  │
│                        │  - Regret analysis    │                  │
│                        └───────────┬───────────┘                  │
│                                    │                               │
│                                    ▼                               │
│                        ┌───────────────────────┐                  │
│                        │  Recommendation       │                  │
│                        │  Engine               │                  │
│                        │  - Proxy ranking      │                  │
│                        │  - Segment warnings   │                  │
│                        │  - Confidence bounds  │                  │
│                        └───────────┬───────────┘                  │
│                                    │                               │
│                                    ▼                               │
│                        ┌───────────────────────┐                  │
│                        │  User Interface       │                  │
│                        │  - Dashboard          │                  │
│                        │  - Visualizations     │                  │
│                        │  - API endpoints      │                  │
│                        └───────────────────────┘                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Diagram 2: Reliability Score Computation Flow

```
Input: Historical Experiment Data
│
├─▶ For each Proxy Metric:
│   │
│   ├─▶ [1] Compute Effect Correlation (ρ)
│   │   │
│   │   ├─▶ Extract proxy treatment effects across experiments
│   │   ├─▶ Extract long-term treatment effects across experiments
│   │   ├─▶ Compute Pearson correlation
│   │   └─▶ Apply Fisher's z-transformation
│   │
│   ├─▶ [2] Compute Directional Accuracy (α)
│   │   │
│   │   ├─▶ For each experiment:
│   │   │   ├─▶ Check if sign(proxy_effect) == sign(long_effect)
│   │   │   └─▶ Record agreement (1) or disagreement (0)
│   │   └─▶ Compute proportion of agreements
│   │
│   ├─▶ [3] Compute Fragility Rate (φ)
│   │   │
│   │   ├─▶ For each segment:
│   │   │   ├─▶ Compute segment-level proxy effect
│   │   │   ├─▶ Compute segment-level long-term effect
│   │   │   └─▶ Detect sign flip
│   │   └─▶ Compute flip_rate = (flips) / (total_cells)
│   │
│   └─▶ [4] Combine into Composite Score
│       │
│       └─▶ Reliability = 0.6×ρ + 0.2×α + 0.2×(1-φ)
│
└─▶ Output: Ranked list of proxies with reliability scores
```

## Diagram 3: Fragility Detection Algorithm

```
Input: Experiment Data, Proxy Metric, Segment Attributes
│
├─▶ Define Segments
│   └─▶ Segments = {region, device, tenure, ...}
│
├─▶ For each Segment S:
│   │
│   ├─▶ For each Experiment E:
│   │   │
│   │   ├─▶ Filter data: D_seg = Data[segment == S & exp == E]
│   │   │
│   │   ├─▶ Compute proxy effect:
│   │   │   δ_proxy = mean(D_seg[treatment=1].proxy) - mean(D_seg[treatment=0].proxy)
│   │   │
│   │   ├─▶ Compute long-term effect:
│   │   │   δ_long = mean(D_seg[treatment=1].outcome) - mean(D_seg[treatment=0].outcome)
│   │   │
│   │   ├─▶ Check for sign flip:
│   │   │   flip = (sign(δ_proxy) ≠ sign(δ_long)) AND (|δ_long| > threshold)
│   │   │
│   │   └─▶ Record flip occurrence
│   │
│   └─▶ Compute flip_rate_S = (# flips in S) / (# experiments with S)
│
├─▶ Rank segments by flip_rate (descending)
│
└─▶ Output: List of fragile segments with flip rates
```

## Diagram 4: Decision Simulation Process

```
Input: Experiment Data, Proxy Metric, Shipping Threshold
│
├─▶ For each Experiment E:
│   │
│   ├─▶ Compute proxy treatment effect: δ_proxy
│   ├─▶ Compute long-term treatment effect: δ_long (ground truth)
│   │
│   ├─▶ Simulate Proxy-Based Decision:
│   │   │
│   │   └─▶ Decision_proxy = SHIP if δ_proxy > threshold else NO_SHIP
│   │
│   ├─▶ Oracle Decision (using true long-term effect):
│   │   │
│   │   └─▶ Decision_oracle = SHIP if δ_long > 0 else NO_SHIP
│   │
│   ├─▶ Classify Outcome:
│   │   │
│   │   ├─▶ True Positive:  Decision_proxy = SHIP AND δ_long > 0
│   │   ├─▶ False Positive: Decision_proxy = SHIP AND δ_long ≤ 0
│   │   ├─▶ True Negative:  Decision_proxy = NO_SHIP AND δ_long ≤ 0
│   │   └─▶ False Negative: Decision_proxy = NO_SHIP AND δ_long > 0
│   │
│   └─▶ Compute Regret:
│       │
│       └─▶ Regret_E = |δ_long| if decision was wrong, else 0
│
├─▶ Aggregate Metrics:
│   │
│   ├─▶ Win Rate = (TP + TN) / Total
│   ├─▶ False Positive Rate = FP / (FP + TN)
│   ├─▶ False Negative Rate = FN / (FN + TP)
│   └─▶ Average Regret = mean(Regret_E)
│
└─▶ Output: Decision quality metrics for proxy
```

## Diagram 5: Data Flow for New Experiment

```
New Experiment Created
│
├─▶ Extract Experiment Metadata
│   ├─▶ Segment distribution (% Mobile, % NA, % New users, ...)
│   ├─▶ Experiment type (UI change, algorithm, pricing, ...)
│   └─▶ Expected duration
│
├─▶ Query Historical Database
│   └─▶ Find similar past experiments based on segment similarity
│
├─▶ Retrieve Proxy Reliability Scores
│   └─▶ Filter by segment-conditional reliability
│
├─▶ Generate Recommendations
│   │
│   ├─▶ Rank proxies by reliability for this segment distribution
│   ├─▶ Identify fragile segments for top proxies
│   └─▶ Compute expected decision quality
│
├─▶ Display to User
│   │
│   ├─▶ Recommended proxy: "early_watch_min" (reliability: 0.87)
│   ├─▶ Warning: "Fragile for Mobile+IN+New users (flip rate: 45%)"
│   └─▶ Alternative: "early_starts" (reliability: 0.82, more stable)
│
└─▶ User Makes Decision
    └─▶ Select proxy and proceed with experiment
```

---

## Figure Descriptions for Patent Filing

**Figure 1**: System architecture showing data ingestion, processing modules, and user interface

**Figure 2**: Flowchart of reliability score computation combining correlation, directional accuracy, and fragility

**Figure 3**: Algorithm for detecting fragile segments through sign flip analysis

**Figure 4**: Decision simulation process comparing proxy-based decisions to oracle decisions

**Figure 5**: Data flow for providing proxy recommendations for new experiments

These diagrams illustrate the key technical innovations and can be converted to formal patent drawings.

