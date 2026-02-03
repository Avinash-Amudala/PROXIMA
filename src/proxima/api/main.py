"""
FastAPI Backend for PROXIMA

Provides REST API endpoints for:
- Generating synthetic data
- Scoring proxy metrics
- Detecting fragility
- Decision simulation
"""

from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
from pathlib import Path

from proxima.generator.simulate import generate_synthetic_experiments
from proxima.models.baseline import (
    score_proxies,
    find_top_fragility_segments,
    EARLY_METRICS
)
from proxima.evaluation.decision_sim import compare_decision_strategies

app = FastAPI(
    title="PROXIMA API",
    description="Proxy Metric Intelligence for Online Experiments",
    version="0.1.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class GenerateDataRequest(BaseModel):
    n_users: int = Field(default=200_000, ge=1000, le=1_000_000)
    n_experiments: int = Field(default=40, ge=5, le=200)
    seed: int = Field(default=7, ge=0)


class ProxyScoreResponse(BaseModel):
    metric: str
    reliability: float
    effect_corr: float
    directional_accuracy: float
    fragility_rate: float
    n_experiments_scored: int


class FragilitySegment(BaseModel):
    region: Optional[str] = None
    device: Optional[str] = None
    tenure: Optional[str] = None
    flip_rate: float
    n_cells: int
    avg_cell_n: float


class DecisionResult(BaseModel):
    proxy_metric: str
    win_rate: float
    false_positive_rate: float
    false_negative_rate: float
    avg_regret: float
    total_shipped: int
    correct_ships: int
    incorrect_ships: int
    missed_opportunities: int


class AnalysisResponse(BaseModel):
    proxy_scores: List[ProxyScoreResponse]
    decision_results: List[DecisionResult]
    fragile_segments: List[FragilitySegment]
    data_summary: Dict[str, Any]


# Global state (in production, use proper state management)
current_data: Optional[pd.DataFrame] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "PROXIMA API",
        "version": "0.1.0",
        "status": "running",
        "data_loaded": current_data is not None
    }


@app.post("/api/generate-data")
async def generate_data(request: GenerateDataRequest):
    """Generate synthetic experiment data."""
    global current_data
    
    try:
        current_data = generate_synthetic_experiments(
            n_users=request.n_users,
            n_experiments=request.n_experiments,
            seed=request.seed
        )
        
        return {
            "status": "success",
            "message": "Data generated successfully",
            "summary": {
                "n_users": len(current_data),
                "n_experiments": int(current_data["exp_id"].nunique()),
                "n_failure_cohort": int(current_data["failure_cohort"].sum()),
                "failure_cohort_rate": float(current_data["failure_cohort"].mean()),
                "columns": list(current_data.columns)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/proxy-scores")
async def get_proxy_scores() -> List[ProxyScoreResponse]:
    """Get proxy metric reliability scores."""
    global current_data
    
    if current_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Generate data first.")
    
    try:
        details, _ = score_proxies(current_data)
        
        scores = []
        for _, row in details.iterrows():
            scores.append(ProxyScoreResponse(
                metric=row["metric"],
                reliability=float(row["reliability"]),
                effect_corr=float(row["effect_corr"]),
                directional_accuracy=float(row["directional_accuracy"]),
                fragility_rate=float(row["fragility_rate"]),
                n_experiments_scored=int(row["n_experiments_scored"])
            ))
        
        return scores
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fragility/{proxy_metric}")
async def get_fragility(proxy_metric: str, min_count: int = 500) -> List[FragilitySegment]:
    """Get fragile segments for a specific proxy metric."""
    global current_data
    
    if current_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Generate data first.")
    
    if proxy_metric not in EARLY_METRICS:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Choose from: {EARLY_METRICS}")
    
    try:
        frag_df = find_top_fragility_segments(current_data, proxy_metric, min_count=min_count)
        
        segments = []
        for _, row in frag_df.head(20).iterrows():
            segments.append(FragilitySegment(
                region=row.get("region"),
                device=row.get("device"),
                tenure=row.get("tenure"),
                flip_rate=float(row["flip_rate"]),
                n_cells=int(row["n_cells"]),
                avg_cell_n=float(row["avg_cell_n"])
            ))
        
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/decision-simulation")
async def get_decision_simulation() -> List[DecisionResult]:
    """Get decision simulation results for all proxy metrics."""
    global current_data

    if current_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Generate data first.")

    try:
        decision_df = compare_decision_strategies(current_data, EARLY_METRICS)

        results = []
        for _, row in decision_df.iterrows():
            results.append(DecisionResult(
                proxy_metric=row["proxy_metric"],
                win_rate=float(row["win_rate"]),
                false_positive_rate=float(row["false_positive_rate"]),
                false_negative_rate=float(row["false_negative_rate"]),
                avg_regret=float(row["avg_regret"]),
                total_shipped=int(row["total_shipped"]),
                correct_ships=int(row["correct_ships"]),
                incorrect_ships=int(row["incorrect_ships"]),
                missed_opportunities=int(row["missed_opportunities"])
            ))

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/full-analysis")
async def get_full_analysis() -> AnalysisResponse:
    """Get complete analysis including proxy scores, decision simulation, and fragility."""
    global current_data

    if current_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Generate data first.")

    try:
        # Proxy scores
        details, _ = score_proxies(current_data)
        proxy_scores = []
        for _, row in details.iterrows():
            proxy_scores.append(ProxyScoreResponse(
                metric=row["metric"],
                reliability=float(row["reliability"]),
                effect_corr=float(row["effect_corr"]),
                directional_accuracy=float(row["directional_accuracy"]),
                fragility_rate=float(row["fragility_rate"]),
                n_experiments_scored=int(row["n_experiments_scored"])
            ))

        # Decision simulation
        decision_df = compare_decision_strategies(current_data, EARLY_METRICS)
        decision_results = []
        for _, row in decision_df.iterrows():
            decision_results.append(DecisionResult(
                proxy_metric=row["proxy_metric"],
                win_rate=float(row["win_rate"]),
                false_positive_rate=float(row["false_positive_rate"]),
                false_negative_rate=float(row["false_negative_rate"]),
                avg_regret=float(row["avg_regret"]),
                total_shipped=int(row["total_shipped"]),
                correct_ships=int(row["correct_ships"]),
                incorrect_ships=int(row["incorrect_ships"]),
                missed_opportunities=int(row["missed_opportunities"])
            ))

        # Fragility for top metric
        top_metric = details.iloc[0]["metric"]
        frag_df = find_top_fragility_segments(current_data, top_metric, min_count=400)
        fragile_segments = []
        for _, row in frag_df.head(15).iterrows():
            fragile_segments.append(FragilitySegment(
                region=row.get("region"),
                device=row.get("device"),
                tenure=row.get("tenure"),
                flip_rate=float(row["flip_rate"]),
                n_cells=int(row["n_cells"]),
                avg_cell_n=float(row["avg_cell_n"])
            ))

        # Data summary
        data_summary = {
            "n_users": len(current_data),
            "n_experiments": int(current_data["exp_id"].nunique()),
            "n_failure_cohort": int(current_data["failure_cohort"].sum()),
            "failure_cohort_rate": float(current_data["failure_cohort"].mean()),
            "best_proxy": details.iloc[0]["metric"],
            "best_reliability": float(details.iloc[0]["reliability"]),
            "top_fragile_metric": top_metric
        }

        return AnalysisResponse(
            proxy_scores=proxy_scores,
            decision_results=decision_results,
            fragile_segments=fragile_segments,
            data_summary=data_summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

