# PROXIMA Quick Start Guide

Get PROXIMA up and running in 5 minutes!

---

## Prerequisites

- **Python 3.9+** installed
- **Node.js 16+** and npm installed
- **Git** installed

---

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/Avi9618/PROXIMA.git
cd PROXIMA

# Install Python dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## Step 2: Run the Command-Line Pipeline

```bash
# Run the full analysis pipeline
python src/proxima/run_mvp.py --n_users 250000 --n_experiments 50 --seed 7

# This will:
# 1. Generate synthetic experiment data
# 2. Train a long-term outcome prediction model
# 3. Score all proxy metrics
# 4. Detect fragile segments
# 5. Simulate shipping decisions
# 6. Generate publication-quality visualizations

# Outputs saved to:
# - outputs/synthetic_data.csv
# - outputs/proxy_scores.csv
# - outputs/fragility_segments.csv
# - outputs/decision_results.csv
# - outputs/figures/*.png
```

**Expected Output**:
```
=== GENERATING DATA ===
Generated 250,000 users across 50 experiments

=== TRAINING MODEL ===
Model AUC: 0.847

=== SCORING PROXIES ===
Metric              Reliability  Effect Corr  Dir Accuracy  Fragility Rate
early_watch_min     0.867        0.923        0.950         0.085
early_starts        0.821        0.884        0.925         0.112
early_ctr           0.756        0.812        0.900         0.178
rebuffer_rate       0.623        0.701        0.825         0.287

=== DETECTING FRAGILITY ===
Top fragile segment: Mobile + IN + New (flip rate: 45.2%)

=== SIMULATING DECISIONS ===
Best proxy: early_watch_min (win rate: 87.3%)

✓ All outputs saved to outputs/
```

---

## Step 3: Launch the Interactive Dashboard

### Terminal 1: Start Backend API

```bash
cd src
uvicorn proxima.api.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

### Terminal 2: Start React Frontend

```bash
cd frontend
npm run dev

# You should see:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

### Open Browser

Navigate to **http://localhost:5173**

You should see the PROXIMA dashboard with 4 tabs:
1. **Generate Data**: Create synthetic experiments
2. **Proxy Scores**: View ranked proxy metrics
3. **Fragility Analysis**: Explore fragile segments
4. **Decision Simulation**: Analyze decision quality

---

## Step 4: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/proxima --cov-report=html

# Open coverage report
# open htmlcov/index.html  # macOS
# start htmlcov/index.html  # Windows
```

**Expected Output**:
```
tests/test_generator.py::TestSigmoid::test_sigmoid_zero PASSED
tests/test_generator.py::TestSigmoid::test_sigmoid_positive PASSED
...
tests/test_evaluation.py::TestCompareDecisionStrategies::test_all_metrics_included PASSED

====== 37 passed in 12.34s ======
```

---

## Step 5: Explore Jupyter Notebooks

```bash
# Start Jupyter
jupyter notebook notebooks/

# Open 01_data_exploration.ipynb
# Run all cells to see data exploration and visualizations
```

---

## Common Issues & Solutions

### Issue 1: Module not found error

```bash
# Solution: Install package in development mode
pip install -e .
```

### Issue 2: Port 8000 already in use

```bash
# Solution: Use a different port
uvicorn proxima.api.main:app --reload --port 8001

# Update frontend API client (frontend/src/api/client.js):
# const API_BASE_URL = 'http://localhost:8001'
```

### Issue 3: Frontend build errors

```bash
# Solution: Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue 4: CORS errors in browser

```bash
# Solution: Ensure backend is running and CORS is enabled
# Check src/proxima/api/main.py has:
# app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

---

## Next Steps

### For Research

1. **Run on Real Data**: See `docs/REAL_DATASETS.md` for integration guide
2. **Generate Paper Figures**: Use notebooks to create publication-quality plots
3. **Ablation Studies**: Modify reliability score weights in `src/proxima/models/baseline.py`
4. **Baseline Comparisons**: Implement alternative proxy selection methods

### For Patent Filing

1. **Review Patent Docs**: See `docs/patent/` for abstract, claims, and diagrams
2. **Prepare Formal Drawings**: Convert ASCII diagrams to professional format
3. **File Provisional**: Submit to USPTO or relevant patent office

### For Development

1. **Add New Proxy Metrics**: Edit `EARLY_METRICS` in `src/proxima/models/baseline.py`
2. **Customize Reliability Weights**: Modify weights in `score_proxies()` function
3. **Add New Visualizations**: Extend `src/proxima/visualization/plots.py`
4. **Integrate with Real Platform**: Use REST API endpoints from `src/proxima/api/main.py`

---

## API Endpoints

Once the backend is running, you can access:

- **Generate Data**: `POST http://localhost:8000/api/generate-data`
  ```json
  {"n_users": 10000, "n_experiments": 10, "seed": 42}
  ```

- **Get Proxy Scores**: `GET http://localhost:8000/api/proxy-scores`

- **Get Fragility**: `GET http://localhost:8000/api/fragility/early_watch_min`

- **Get Decision Results**: `GET http://localhost:8000/api/decision-simulation`

- **Full Analysis**: `GET http://localhost:8000/api/full-analysis`

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)

---

## File Locations

- **Source Code**: `src/proxima/`
- **Tests**: `tests/`
- **Frontend**: `frontend/src/`
- **Outputs**: `outputs/` (created after first run)
- **Figures**: `outputs/figures/` (created after first run)
- **Documentation**: `docs/`
- **Notebooks**: `notebooks/`

---

## Getting Help

- **Documentation**: See `README.md` for comprehensive guide
- **Real Datasets**: See `docs/REAL_DATASETS.md`
- **Patent Info**: See `docs/patent/`
- **Project Summary**: See `PROJECT_SUMMARY.md`
- **Contact**: aa9429@g.rit.edu

---

## Quick Commands Reference

```bash
# Run pipeline
python src/proxima/run_mvp.py --n_users 250000 --n_experiments 50

# Start backend
cd src && uvicorn proxima.api.main:app --reload

# Start frontend
cd frontend && npm run dev

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/proxima

# Start Jupyter
jupyter notebook notebooks/

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install
```

---

**You're all set! 🚀**

Start with the command-line pipeline, then explore the dashboard, and finally dive into the notebooks for detailed analysis.

