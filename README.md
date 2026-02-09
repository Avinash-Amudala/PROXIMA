# PROXIMA: Proxy Metric Intelligence

**Automatically learn which early metrics are reliable proxies for long-term impact in A/B testing**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎥 Dashboard Demo

![PROXIMA Dashboard Demo](docs/Proxima-intro.gif)

## 🎯 Overview

PROXIMA (Proxy Metric Intelligence) is a research system that addresses a critical challenge in online experimentation: **How do we know if early metrics are reliable proxies for long-term outcomes?**

In A/B testing, we often want to measure long-term metrics (e.g., 30-day retention, lifetime value) but need to make decisions quickly. PROXIMA automatically:

1. **Scores proxy reliability** using historical experiment data
2. **Detects proxy fragility** across user segments (geography, device, tenure)
3. **Simulates decision quality** to quantify the risk of using each proxy
4. **Warns about failure modes** like Simpson's paradox and metric gaming

### Key Innovation

PROXIMA introduces a **composite reliability score** that combines:
- **Effect correlation** (60%): How well proxy effects correlate with long-term effects
- **Directional accuracy** (20%): How often proxy and long-term effects agree on direction
- **Anti-fragility** (20%): How stable the proxy is across user segments

This enables **segment-aware proxy selection** that accounts for distribution shift.

---

## 📊 System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph Input["📥 Input Data"]
        A[Historical A/B Tests]
        B[User Segments]
        C[Proxy Metrics]
        D[Long-term Metrics]
    end

    subgraph Core["🔬 PROXIMA Core Engine"]
        E[Data Generator]
        F[Treatment Effect Estimator]
        G[Proxy Scorer]
        H[Fragility Detector]
        I[Decision Simulator]
    end

    subgraph Output["📤 Outputs"]
        J[Reliability Scores]
        K[Fragility Reports]
        L[Decision Quality Metrics]
        M[Visualizations]
    end

    subgraph Interface["🖥️ User Interfaces"]
        N[REST API]
        O[React Dashboard]
        P[CLI Tools]
    end

    A --> E
    B --> E
    C --> E
    D --> E

    E --> F
    F --> G
    F --> H
    G --> I
    H --> I

    G --> J
    H --> K
    I --> L
    J --> M
    K --> M
    L --> M

    J --> N
    K --> N
    L --> N
    M --> N

    N --> O
    N --> P

    style Input fill:#e1f5ff
    style Core fill:#fff4e1
    style Output fill:#e8f5e9
    style Interface fill:#f3e5f5
```

### Data Flow Pipeline

```mermaid
flowchart LR
    subgraph Stage1["Stage 1: Data Preparation"]
        A1[Raw Experiment Data] --> A2[Feature Engineering]
        A2 --> A3[Segment Definition]
        A3 --> A4[Train/Test Split]
    end

    subgraph Stage2["Stage 2: Effect Estimation"]
        B1[Treatment Effect<br/>Proxy Metrics]
        B2[Treatment Effect<br/>Long-term Metrics]
        B3[Segment-level Effects]
    end

    subgraph Stage3["Stage 3: Proxy Scoring"]
        C1[Correlation Analysis]
        C2[Directional Accuracy]
        C3[Fragility Detection]
        C4[Composite Score]
    end

    subgraph Stage4["Stage 4: Validation"]
        D1[Decision Simulation]
        D2[Win Rate Analysis]
        D3[Regret Calculation]
        D4[Statistical Tests]
    end

    A4 --> B1
    A4 --> B2
    A4 --> B3

    B1 --> C1
    B2 --> C1
    B1 --> C2
    B2 --> C2
    B3 --> C3

    C1 --> C4
    C2 --> C4
    C3 --> C4

    C4 --> D1
    D1 --> D2
    D1 --> D3
    D2 --> D4

    style Stage1 fill:#e3f2fd
    style Stage2 fill:#fff3e0
    style Stage3 fill:#f1f8e9
    style Stage4 fill:#fce4ec
```

### Algorithm Flow

```mermaid
flowchart TD
    Start([Start: Historical Experiments]) --> LoadData[Load Experiment Data]

    LoadData --> ForEachExp{For Each<br/>Experiment}

    ForEachExp -->|Yes| EstimateProxy[Estimate Proxy<br/>Treatment Effect]
    EstimateProxy --> EstimateLong[Estimate Long-term<br/>Treatment Effect]

    EstimateLong --> ForEachSeg{For Each<br/>Segment}

    ForEachSeg -->|Yes| SegEffect[Compute Segment<br/>Treatment Effects]
    SegEffect --> CheckFlip{Sign Flip?}

    CheckFlip -->|Yes| RecordFragile[Record Fragile<br/>Segment]
    CheckFlip -->|No| NextSeg[Next Segment]
    RecordFragile --> NextSeg

    NextSeg --> ForEachSeg
    ForEachSeg -->|No| NextExp[Next Experiment]

    NextExp --> ForEachExp

    ForEachExp -->|No| ComputeCorr["Compute Correlation<br/>rho = corr(proxy, long)"]

    ComputeCorr --> ComputeDA[Compute Directional<br/>Accuracy]
    ComputeDA --> ComputeFR[Compute Fragility<br/>Rate]

    ComputeFR --> CompositeScore["Composite Score:<br/>R = 0.6*rho + 0.2*DA + 0.2*(1 - FR)"]

    CompositeScore --> SimDecisions[Simulate Decisions]
    SimDecisions --> WinRate[Calculate Win Rate]
    WinRate --> Output([Output: Reliability<br/>Scores & Reports])

    style Start fill:#4caf50,color:#fff
    style Output fill:#2196f3,color:#fff
    style CompositeScore fill:#ff9800,color:#fff
    style CheckFlip fill:#f44336,color:#fff
```

### Decision Simulation Process

```mermaid
sequenceDiagram
    participant Exp as Experiment
    participant Proxy as Proxy Metric
    participant Oracle as Long-term Metric
    participant Sim as Decision Simulator
    participant Report as Report Generator

    Exp->>Proxy: Measure early effect
    Exp->>Oracle: Measure long-term effect

    Proxy->>Sim: Proxy effect = +0.05
    Note over Sim: Decision: Ship if > 0
    Sim->>Sim: Proxy says: SHIP ✓

    Oracle->>Sim: True effect = +0.03
    Note over Sim: Oracle says: SHIP ✓

    Sim->>Sim: Compare decisions
    alt Decisions Match
        Sim->>Report: Win! (Correct decision)
    else Decisions Differ
        Sim->>Report: Loss! (Wrong decision)
    end

    Report->>Report: Aggregate across experiments
    Report->>Report: Calculate win rate
    Report-->>Exp: Final reliability score
```

### Fragility Detection Mechanism

```mermaid
graph TD
    subgraph Global["Global Level"]
        A[Overall Treatment Effect<br/>Proxy: +0.10<br/>Long-term: +0.08]
    end

    subgraph Segments["Segment Level Analysis"]
        B1[Segment 1: New Users<br/>Proxy: +0.15<br/>Long-term: +0.12<br/>✓ Same sign]

        B2[Segment 2: Power Users<br/>Proxy: +0.08<br/>Long-term: +0.10<br/>✓ Same sign]

        B3[Segment 3: Mobile Users<br/>Proxy: +0.05<br/>Long-term: -0.03<br/>⚠️ SIGN FLIP!]

        B4[Segment 4: Desktop Users<br/>Proxy: +0.12<br/>Long-term: +0.15<br/>✓ Same sign]
    end

    subgraph Detection["Fragility Detection"]
        C[Count Sign Flips: 1/4 = 25%]
        D[Fragility Rate = 0.25]
        E{Fragility > 0.1?}
    end

    subgraph Action["Action"]
        F[⚠️ WARNING:<br/>Proxy unreliable<br/>for Mobile Users]
        G[✓ Proxy reliable<br/>overall]
    end

    A --> B1
    A --> B2
    A --> B3
    A --> B4

    B1 --> C
    B2 --> C
    B3 --> C
    B4 --> C

    C --> D
    D --> E

    E -->|Yes| F
    E -->|No| G

    style A fill:#4caf50,color:#fff
    style B3 fill:#f44336,color:#fff
    style F fill:#ff9800,color:#fff
    style G fill:#4caf50,color:#fff
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Avi9618/PROXIMA.git
cd PROXIMA

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Run the MVP Pipeline

```bash
# Generate data, train model, score proxies, detect fragility, simulate decisions
python src/proxima/run_mvp.py --n_users 250000 --n_experiments 50 --seed 7

# Outputs saved to outputs/ directory
# Figures saved to outputs/figures/
```

### Launch the Dashboard

```bash
# Terminal 1: Start backend API
cd src
uvicorn proxima.api.main:app --reload --port 8000

# Terminal 2: Start React frontend
cd frontend
npm run dev

# Open browser to http://localhost:5173
```

---

## 📊 Features

### 1. Synthetic Data Generator
- Generates realistic A/B experiment data with intentional failure modes
- Includes segment attributes (region, device, tenure)
- Creates "failure cohort" where proxies mislead (Mobile + India + New users)
- Configurable sample size and number of experiments

### 2. Proxy Reliability Scoring
- Computes composite reliability score for each proxy metric
- Ranks proxies by reliability
- Provides confidence intervals and statistical significance tests
- Identifies which proxies are most trustworthy

### 3. Fragility Detection
- Detects segments where proxy shows **sign flips** (opposite direction from true effect)
- Computes flip rate for each segment
- Flags high-risk segments (e.g., >30% flip rate)
- Helps avoid Simpson's paradox

### 4. Decision Simulation
- Simulates shipping decisions based on each proxy
- Compares to "Oracle" (using true long-term metric)
- Reports win rate, false positive/negative rates, and regret
- Quantifies the cost of using proxies vs. waiting for long-term data

### 5. Interactive Dashboard
- React-based UI with modern design
- Generate synthetic data with custom parameters
- View ranked proxy scores with reliability breakdown
- Explore fragile segments with color-coded severity
- Analyze decision simulation results with charts

### 6. Publication-Quality Visualizations
- Correlation plots with regression lines and confidence bands
- Reliability comparison bar charts
- Fragility heatmaps across segments
- Decision simulation result grids
- All plots at 300 DPI for paper submission

---

## 📁 Project Structure

```
PROXIMA/
├── src/proxima/
│   ├── generator/
│   │   └── simulate.py          # Synthetic data generation
│   ├── models/
│   │   └── baseline.py          # Proxy scoring & fragility detection
│   ├── evaluation/
│   │   ├── metrics.py           # Statistical evaluation
│   │   └── decision_sim.py      # Decision simulation
│   ├── visualization/
│   │   └── plots.py             # Publication-quality plots
│   ├── api/
│   │   └── main.py              # FastAPI backend
│   └── run_mvp.py               # Main pipeline runner
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── api/                 # API client
│   │   └── App.jsx              # Main app
│   └── package.json
├── tests/
│   ├── test_generator.py        # Data generation tests
│   ├── test_baseline.py         # Model tests
│   └── test_evaluation.py       # Evaluation tests
├── notebooks/
│   └── 01_data_exploration.ipynb
├── docs/
│   ├── patent/                  # Patent documentation
│   └── REAL_DATASETS.md         # Dataset integration guide
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🔬 Research Use Cases

### For Academic Papers

1. **Novel Contribution**: First system to automatically detect proxy fragility under distribution shift
2. **Evaluation**: Compare PROXIMA's proxy selection to manual/heuristic baselines
3. **Ablation Studies**: Test different weight combinations in reliability score
4. **Real Data Validation**: Apply to public A/B testing datasets (see `docs/REAL_DATASETS.md`)

### For Industry Applications

1. **Faster Experimentation**: Confidently use early metrics, reducing experiment duration by 50-80%
2. **Risk Mitigation**: Avoid shipping bad changes due to misleading proxies
3. **Segment-Specific Decisions**: Use different proxies for different user cohorts
4. **Automated Monitoring**: Continuously track proxy reliability as new experiments complete

---

## 📈 Example Results

```
=== PROXY RELIABILITY SCORES ===
Metric              Reliability  Effect Corr  Dir Accuracy  Fragility Rate
early_watch_min     0.867        0.923        0.950         0.085
early_starts        0.821        0.884        0.925         0.112
early_ctr           0.756        0.812        0.900         0.178
rebuffer_rate       0.623        0.701        0.825         0.287

=== FRAGILE SEGMENTS (early_watch_min) ===
Segment: Mobile + IN + New
  Flip Rate: 45.2%
  Experiments: 23
  Avg Cell Size: 1,247 users
  ⚠️  CRITICAL: Proxy shows opposite direction from true effect

=== DECISION SIMULATION ===
Proxy: early_watch_min
  Win Rate: 87.3%
  False Positive Rate: 8.1%
  False Negative Rate: 4.6%
  Average Regret: 0.0234
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/proxima --cov-report=html

# Run specific test file
pytest tests/test_baseline.py -v
```

---

## 📚 Documentation

- **[Real Dataset Integration](docs/REAL_DATASETS.md)**: Guide for using public A/B testing datasets
- **[Patent Documentation](docs/patent/)**: Technical diagrams, claims, and detailed descriptions
- **[API Reference](docs/API_REFERENCE.md)**: FastAPI endpoint documentation (coming soon)
- **[Architecture](docs/ARCHITECTURE.md)**: System design and technical details (coming soon)

---

## 📄 Paper

**System and Method for Reliability Scoring of Proxy Metrics in Experiments**
Avinash Amudala (2026)

📌 DOI: [https://doi.org/10.5281/zenodo.18566674](https://doi.org/10.5281/zenodo.18566674)

---

## 🎓 Citation

If you use PROXIMA in your research, please cite:

```bibtex
@software{proxima2026,
  author = {Amudala, Avinash},
  title = {PROXIMA: Proxy Metric Intelligence for Online Experiments},
  year = {2026},
  url = {https://github.com/Avinash-Amudala/PROXIMA}
}
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

**Avinash Amudala**
Email: aa9429@g.rit.edu
GitHub: [@Avinash-Amudala](https://github.com/Avinash-Amudala)

---

## 🙏 Acknowledgments

- Inspired by research on proxy metrics in online experimentation
- Built with modern ML/stats tools: scikit-learn, scipy, statsmodels
- Dashboard powered by React, Vite, and TailwindCSS
- Visualizations using matplotlib, seaborn, and Recharts

---

**Status**: Research prototype ready for paper submission and patent filing 🚀

