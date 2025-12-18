"""Analysis utilities: summaries, calibration, generators, saving outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

from .samples import WaterSample
from .model import WaterQualityModel


def summarize_alerts(results: List[Tuple[WaterSample, float, str]]) -> Dict[str, object]:
    """Summarize evaluation results."""
    labels = [label for _, _, label in results]
    safe_count = sum(1 for x in labels if x == "Safe")
    unsafe_count = sum(1 for x in labels if x == "Unsafe")
    worst = sorted(results, key=lambda t: t[1], reverse=True)[:5]  # lambda (Part 2)
    return {"total": len(results), "safe": safe_count, "unsafe": unsafe_count, "top5_worst": worst}


def alert_generator(results: Iterable[Tuple[WaterSample, float, str]]):
    """Generator yielding unsafe alerts (Part 2 generator)."""
    for sample, score, label in results:
        if label == "Unsafe":
            yield (sample, score)


def save_results_csv(results: List[Tuple[WaterSample, float, str]], out_path: Path) -> None:
    """Meaningful I/O: save evaluated results to CSV."""
    rows = []
    for s, score, label in results:
        ts = s.timestamp.isoformat() if s.timestamp else ""
        rows.append(
            {
                "sample_id": s.sample_id,
                "timestamp": ts,
                "ph": s.ph,
                "turbidity": s.turbidity,
                "conductivity": s.conductivity,
                "dissolved_oxygen": s.dissolved_oxygen,
                "temperature": s.temperature,
                "salinity": s.salinity,
                "chlorophyll": s.chlorophyll,
                "risk_score": score,
                "label": label,
            }
        )
    pd.DataFrame(rows).to_csv(out_path, index=False)


def build_calibrated_model(samples: List[WaterSample], base_weights: Dict[str, float] | None = None, unsafe_percentile: float = 90.0) -> WaterQualityModel:
    """Calibrate thresholds + cutoff from the dataset so you don't get all 'Safe'."""
    df = pd.DataFrame([{
        "ph": s.ph,
        "turbidity": s.turbidity,
        "conductivity": s.conductivity,
        "dissolved_oxygen": s.dissolved_oxygen,
        "temperature": s.temperature,
        "salinity": s.salinity,
        "chlorophyll": s.chlorophyll,
    } for s in samples])

    q95 = df.quantile(0.95)
    q05 = df.quantile(0.05)

    thresholds = {
        "ph_low": 6.5,
        "ph_high": 8.5,
        "turbidity_max": float(q95["turbidity"]) if float(q95["turbidity"]) > 0 else 1.0,
        "conductivity_max": float(q95["conductivity"]) if float(q95["conductivity"]) > 0 else 1.0,
        "chlorophyll_max": float(q95["chlorophyll"]) if float(q95["chlorophyll"]) > 0 else 1.0,
        "salinity_max": float(q95["salinity"]) if float(q95["salinity"]) > 0 else 1.0,
        "do_low": float(q05["dissolved_oxygen"]),
        "do_high": float(q95["dissolved_oxygen"]),
        "temp_low": float(q05["temperature"]),
        "temp_high": float(q95["temperature"]),
    }

    weights = base_weights or {
        "ph": 0.10,
        "turbidity": 0.20,
        "conductivity": 0.10,
        "chlorophyll": 0.25,
        "dissolved_oxygen": 0.20,
        "salinity": 0.10,
        "temperature": 0.05,
    }

    tmp = WaterQualityModel(thresholds=thresholds, weights=weights, unsafe_cutoff=0.0)
    scores = np.array([tmp.risk_score(s) for s in samples], dtype=float)
    cutoff = float(np.percentile(scores, unsafe_percentile))
    return WaterQualityModel(thresholds=thresholds, weights=weights, unsafe_cutoff=cutoff)
