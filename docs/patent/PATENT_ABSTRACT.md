# Patent Application: Systems and Methods for Selecting Reliable Proxy Metrics for Online Experiments under Distribution Shift

## Title
Systems and Methods for Selecting Reliable Proxy Metrics for Online Experiments under Distribution Shift

## Abstract

Online controlled experiments frequently rely on long-horizon outcome metrics whose observation requires substantial time, delaying product decisions. To accelerate decision-making, short-horizon proxy metrics are often used, but such proxies may be unreliable, particularly under distribution shift across user cohorts, devices, geographies, or experiment types.

Described herein are systems and methods that ingest historical experiment data comprising randomized treatment assignments, segment attributes, short-horizon measurements, and long-horizon outcomes, and automatically identify proxy metrics that reliably predict long-horizon treatment effects.

The disclosed system computes, for each candidate proxy metric, a **reliability score** that integrates:
1. **Agreement** between proxy-induced treatment effects and long-horizon treatment effects across experiments
2. **Stability** of proxy performance across segments and temporal slices
3. **Transportability** of proxy validity to shifted cohort distributions

Additionally, the system detects **proxy fragility** by identifying cohort-specific divergences including sign reversals where proxy effects conflict with long-horizon effects, and generates warnings indicating segments for which the proxy is not trustworthy.

The system may further recommend proxy metrics for new experiments based on similarity of segment composition and experiment conditions, and provide an interface that ranks proxies, quantifies uncertainty, and flags failure risks, thereby enabling faster and safer experiment decisions.

## Field of Invention

The present invention relates generally to online experimentation and A/B testing systems, and more particularly to automated systems for evaluating and selecting reliable proxy metrics for predicting long-term treatment effects in the presence of distribution shift and heterogeneous treatment effects.

## Background

Online platforms conduct thousands of randomized controlled experiments (A/B tests) annually to evaluate product changes. The gold standard for decision-making is to measure long-term outcomes such as 30-day user retention, lifetime value, or long-term engagement. However, these metrics require weeks or months to observe, creating significant delays in product iteration cycles.

To accelerate decisions, practitioners commonly use **proxy metrics**—short-term measurements available within hours or days (e.g., day-1 engagement, click-through rate, initial session duration). The fundamental assumption is that improvements in the proxy metric will translate to improvements in the long-term outcome.

### Problems with Current Approaches

1. **Proxy Unreliability**: Proxies often fail to predict long-term effects accurately, leading to incorrect shipping decisions
2. **Distribution Shift**: Proxy validity varies across user segments (geography, device type, user tenure), but current systems treat proxies as universally valid
3. **Simpson's Paradox**: A proxy may appear valid globally but show opposite effects in specific subpopulations
4. **Metric Gaming**: Treatments can be optimized to improve proxy metrics without benefiting (or even harming) long-term outcomes
5. **Manual Selection**: Proxy selection is typically manual, subjective, and not data-driven

### Need for Innovation

There is a need for automated systems that:
- Quantify proxy reliability using historical experiment data
- Detect segments where proxies are unreliable
- Warn practitioners about proxy fragility before making decisions
- Recommend appropriate proxies based on experiment characteristics

## Summary of Invention

The present invention provides a computer-implemented system and method for automatically evaluating and selecting reliable proxy metrics for online experiments. The system analyzes historical experiment data to:

1. **Compute Reliability Scores**: For each candidate proxy metric, compute a composite reliability score based on:
   - Correlation between proxy treatment effects and long-term treatment effects
   - Directional accuracy (sign agreement)
   - Stability across segments (low fragility)

2. **Detect Proxy Fragility**: Identify specific user segments where proxy metrics show sign flips or high variance compared to global effects

3. **Generate Warnings**: Automatically flag experiments and segments where proxy-based decisions would be unreliable

4. **Simulate Decision Outcomes**: Evaluate the expected win rate, false positive rate, and regret of using each proxy for shipping decisions

5. **Provide Recommendations**: Rank proxies and recommend the most reliable metrics for specific experiment contexts

### Key Novelty

The invention's novelty lies in:
- **Composite reliability metric** combining correlation, directional accuracy, and segment stability
- **Automated fragility detection** using segment-level sign flip analysis
- **Decision simulation framework** for quantifying proxy-based decision quality
- **Segment-conditional proxy recommendations** accounting for distribution shift

## Technical Advantages

1. **Faster Decision-Making**: Enables confident use of early metrics, reducing experiment duration
2. **Reduced Risk**: Prevents incorrect shipping decisions due to misleading proxies
3. **Automated Analysis**: Eliminates manual, subjective proxy selection
4. **Segment Awareness**: Accounts for heterogeneous treatment effects and distribution shift
5. **Quantified Uncertainty**: Provides confidence intervals and statistical significance tests

## Applications

- Online A/B testing platforms
- Product experimentation systems
- Marketing campaign optimization
- Clinical trial design
- Policy evaluation systems
- Any domain requiring early prediction of long-term outcomes

---

**Inventor**: Avinash Amudala  
**Date**: February 2026  
**Status**: Provisional Patent Application

