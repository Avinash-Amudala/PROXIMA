# PROXIMA Artifact Appendix

This document provides complete instructions for reproducing the results in the PROXIMA paper.

## System Requirements

### Hardware
- **Minimum**: 8 GB RAM, 4 CPU cores
- **Recommended**: 16 GB RAM, 8+ CPU cores
- **Storage**: 2 GB free disk space (10 GB if using real datasets)

### Software
- **Operating System**: Windows 10/11, macOS 12+, or Ubuntu 20.04+
- **Python**: 3.9, 3.10, or 3.11 (tested on 3.11)
- **Node.js**: 18+ (for dashboard only)
- **Git**: 2.30+

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Avinash-Amudala/PROXIMA.git
cd PROXIMA
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies (Optional, for Dashboard)

```bash
cd frontend
npm install
cd ..
```

## Reproduction Steps

### Quick Reproduction (Synthetic Data)

Run the complete reproduction script:

```bash
python scripts/reproduce_all.py --seed 42
```

**Expected runtime**: 2-5 minutes on a modern laptop.

### Expected Outputs

After running `reproduce_all.py`, you should see:

```
outputs/paper_figures/
├── figure1_proxy_reliability.png    # Figure 1 from paper
├── figure2_decision_simulation.png  # Figure 2 from paper
├── summary_table.csv                # All numerical results
└── reproduction_metadata.json       # Reproduction metadata
```

### Expected Numerical Results

The following results should match the paper (within ±0.01 due to floating point):

| Metric | Reliability | Correlation | Dir. Accuracy | Win Rate |
|--------|-------------|-------------|---------------|----------|
| early_starts | 0.80 | 0.42 | 1.00 | 1.00 |
| early_ctr | 0.80 | 0.42 | 1.00 | 1.00 |
| early_watch | 0.65 | -0.16 | 1.00 | 1.00 |
| rebuffer_rate | 0.35 | 0.16 | 0.00 | 0.00 |

## Real Dataset Reproduction

To reproduce results on real datasets (Criteo, KuaiRec):

### Step 1: Download Datasets

See `docs/REAL_DATASETS.md` for download links and instructions.

- **Criteo Uplift**: https://ailab.criteo.com/criteo-uplift-prediction-dataset/
- **KuaiRec**: https://kuairec.com/

### Step 2: Place Datasets

```
Data/
├── criteo-uplift-v2.1.csv.gz    # Criteo dataset
└── KuaiRec/                      # KuaiRec folder
    ├── small_matrix.csv
    └── user_features.csv
```

### Step 3: Run Integration Scripts

```bash
python scripts/integrate_criteo.py
python scripts/integrate_kuairec.py
```

**Expected runtime**: 10-30 minutes depending on hardware.

## Dashboard Demo

To run the interactive dashboard:

### Terminal 1: Start Backend API

```bash
cd src
uvicorn proxima.api.main:app --reload --port 8000
```

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'proxima'`:

```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%cd%\src          # Windows
```

### Memory Errors

For large datasets, reduce batch size:

```bash
python scripts/reproduce_all.py --n_users 100000
```

### Node.js Errors

Ensure Node.js 18+ is installed:

```bash
node --version  # Should be v18.x.x or higher
```

## Contact

For questions about reproduction:
- **Author**: Avinash Amudala
- **Email**: aa9429@g.rit.edu
- **GitHub Issues**: https://github.com/Avinash-Amudala/PROXIMA/issues

## License

This artifact is released under the MIT License.

