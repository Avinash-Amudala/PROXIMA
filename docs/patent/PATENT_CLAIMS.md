# Patent Claims

## Independent Claims

### Claim 1: Method for Proxy Metric Evaluation

A computer-implemented method for evaluating reliability of proxy metrics in online experiments, comprising:

1. **Receiving historical experiment data** comprising:
   - A plurality of randomized controlled experiments
   - For each experiment: treatment assignments, user segment attributes, short-horizon proxy measurements, and long-horizon outcome measurements

2. **Computing treatment effects** for each experiment:
   - Computing a proxy treatment effect as a difference in means between treatment and control groups for the proxy metric
   - Computing a long-horizon treatment effect as a difference in means between treatment and control groups for the long-horizon outcome metric

3. **Computing a reliability score** for each candidate proxy metric, wherein the reliability score comprises:
   - An **effect correlation component** measuring correlation between proxy treatment effects and long-horizon treatment effects across experiments
   - A **directional accuracy component** measuring proportion of experiments where proxy effect and long-horizon effect have the same sign
   - A **fragility component** measuring stability of proxy validity across user segments

4. **Detecting fragile segments** by:
   - Partitioning users into segments based on segment attributes
   - Computing segment-level treatment effects for proxy and long-horizon metrics
   - Identifying segments exhibiting sign flips where proxy effect direction contradicts long-horizon effect direction
   - Computing a flip rate for each segment

5. **Generating a ranked list** of proxy metrics ordered by reliability score

6. **Outputting warnings** for segments where flip rate exceeds a threshold

### Claim 2: System for Proxy Metric Selection

A system for selecting reliable proxy metrics for online experiments, comprising:

1. **A data ingestion module** configured to receive and store historical experiment data including treatment assignments, segment attributes, proxy measurements, and outcome measurements

2. **A treatment effect estimation module** configured to compute experiment-level and segment-level treatment effects using statistical methods

3. **A proxy scoring module** configured to:
   - Compute reliability scores for candidate proxy metrics
   - Combine multiple reliability components using weighted aggregation
   - Rank proxies by composite reliability

4. **A fragility detection module** configured to:
   - Identify user segments with proxy-outcome disagreement
   - Compute sign flip rates for each segment
   - Flag high-risk segments

5. **A decision simulation module** configured to:
   - Simulate shipping decisions based on proxy metrics
   - Compute win rates, false positive rates, false negative rates, and regret
   - Compare decision quality across proxies

6. **A user interface** configured to display:
   - Ranked proxy metrics with reliability scores
   - Fragile segments with warnings
   - Decision simulation results
   - Confidence intervals and statistical significance

### Claim 3: Composite Reliability Score

A method for computing a composite reliability score for a proxy metric, comprising:

1. **Computing effect correlation** (ρ):
   - Calculating Pearson correlation between proxy treatment effects and long-horizon treatment effects across experiments
   - Applying Fisher's z-transformation for statistical testing

2. **Computing directional accuracy** (α):
   - For each experiment, determining if sign(proxy_effect) == sign(long_horizon_effect)
   - Computing proportion of experiments with sign agreement

3. **Computing fragility rate** (φ):
   - Identifying segments with sign flips
   - Computing proportion of segment-experiment cells exhibiting flips

4. **Combining components** using weighted formula:
   ```
   Reliability = w₁ × ρ + w₂ × α + w₃ × (1 - φ)
   ```
   where w₁, w₂, w₃ are weights summing to 1

5. **Normalizing** reliability score to [0, 1] range

## Dependent Claims

### Claim 4: Segment-Conditional Proxy Selection

The method of Claim 1, further comprising:
- Receiving segment attributes for a new experiment
- Computing segment similarity between new experiment and historical experiments
- Recommending proxies with highest reliability for similar segment distributions
- Adjusting reliability scores based on segment composition

### Claim 5: Bootstrap Confidence Intervals

The method of Claim 1, wherein computing treatment effects further comprises:
- Generating bootstrap samples from experiment data
- Computing treatment effects for each bootstrap sample
- Deriving confidence intervals from bootstrap distribution
- Reporting uncertainty bounds for all effect estimates

### Claim 6: Decision Simulation with Regret

The method of Claim 1, further comprising:
- Defining a shipping threshold for proxy metrics
- For each experiment, simulating a shipping decision based on proxy effect exceeding threshold
- Comparing simulated decision to oracle decision based on true long-horizon effect
- Computing regret as expected loss from proxy-based decisions
- Aggregating regret across experiments

### Claim 7: Multi-Metric Proxy Combination

The method of Claim 1, further comprising:
- Selecting multiple proxy metrics with complementary reliability profiles
- Training a machine learning model to predict long-horizon outcomes from multiple proxies
- Computing combined proxy reliability using model performance metrics
- Recommending proxy combinations with higher reliability than individual proxies

### Claim 8: Temporal Stability Analysis

The method of Claim 1, further comprising:
- Partitioning experiments by time period
- Computing proxy reliability separately for each time period
- Detecting temporal drift in proxy validity
- Generating warnings when recent reliability differs significantly from historical reliability

### Claim 9: Interactive Visualization Interface

The system of Claim 2, wherein the user interface further comprises:
- Interactive charts showing proxy-outcome correlation with confidence bands
- Heatmaps displaying fragility rates across segment combinations
- Bar charts comparing decision simulation metrics across proxies
- Drill-down capabilities for exploring segment-specific effects
- Export functionality for publication-quality figures

### Claim 10: Real-Time Proxy Monitoring

The system of Claim 2, further comprising:
- A monitoring module that continuously ingests new experiment results
- Automatic recomputation of reliability scores as new data arrives
- Alert generation when proxy reliability degrades below threshold
- Recommendation updates based on latest data

## Method Claims

### Claim 11: Fragility Detection Algorithm

A computer-implemented method for detecting proxy metric fragility, comprising:

1. For each user segment defined by segment attributes:
   - Filtering experiment data to segment members
   - Computing proxy treatment effect and long-horizon treatment effect
   - Determining if sign(proxy_effect) ≠ sign(long_horizon_effect)
   - Recording sign flip occurrence

2. Aggregating sign flips across experiments for each segment

3. Computing flip rate as: (number of flips) / (total segment-experiment cells)

4. Ranking segments by flip rate in descending order

5. Flagging segments with flip rate exceeding threshold (e.g., 30%)

6. Generating human-readable warnings describing fragile segments

### Claim 12: Treatment Effect Estimation with Welch's t-test

The method of Claim 1, wherein computing treatment effects comprises:
- Separating users into treatment and control groups
- Computing sample means and variances for each group
- Applying Welch's t-test for unequal variances
- Computing effect size as difference in means
- Computing standard error using Welch-Satterthwaite equation
- Deriving confidence interval and p-value
- Returning structured result with effect, CI, and significance

## System Architecture Claims

### Claim 13: Distributed Processing System

The system of Claim 2, further comprising:
- A distributed data processing framework for handling large-scale experiment data
- Parallel computation of treatment effects across experiments
- Caching layer for intermediate results
- Scalable storage for historical experiment data
- API layer for integration with experimentation platforms

### Claim 14: Machine Learning Model Training

The system of Claim 2, further comprising:
- A model training module that learns to predict long-horizon outcomes from proxy metrics and segment attributes
- Feature engineering from segment attributes and proxy measurements
- Cross-validation for model selection
- Model performance evaluation using AUC, precision, recall
- Model deployment for real-time predictions

## Use Case Claims

### Claim 15: Application to A/B Testing Platforms

A method for improving A/B testing platforms, comprising:
- Integrating the proxy evaluation system of Claim 2 into an experimentation platform
- Automatically analyzing completed experiments to build proxy reliability database
- Providing proxy recommendations when new experiments are created
- Displaying real-time warnings during experiment analysis
- Preventing premature shipping decisions based on unreliable proxies

---

**Total Claims**: 15 (3 independent, 12 dependent)

**Claim Coverage**:
- Core method and system architecture
- Novel reliability scoring approach
- Fragility detection algorithm
- Decision simulation framework
- Extensions for temporal analysis, multi-metric combination, real-time monitoring
- Integration with existing platforms

**Strategic Value**:
- Broad coverage of proxy metric evaluation domain
- Specific algorithmic innovations (composite scoring, fragility detection)
- System architecture claims for implementation
- Use case claims for commercial applications

