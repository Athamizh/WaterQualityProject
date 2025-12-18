"""Risk scoring and classification for Brisbane water quality dataset."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .exceptions import DataValidationError
from .samples import WaterSample


@dataclass(slots=True)
class WaterQualityModel:
    """Transparent risk scoring model (0..1), classifies Safe/Unsafe.

    Composition relationship:
    - WaterQualityModel processes many WaterSample objects (created by DatasetLoader).
    """

    thresholds: Dict[str, float]
    weights: Dict[str, float]
    unsafe_cutoff: float = 0.60

    def __post_init__(self) -> None:
        needed = {
            "ph_low", "ph_high",
            "turbidity_max",
            "conductivity_max",
            "chlorophyll_max",
            "do_low", "do_high",
            "salinity_max",
            "temp_low", "temp_high",
        }
        missing = needed - set(self.thresholds.keys())
        if missing:
            raise DataValidationError(f"Missing thresholds keys: {sorted(missing)}")

        weight_keys = {
            "ph", "turbidity", "conductivity", "chlorophyll",
            "dissolved_oxygen", "salinity", "temperature",
        }
        missing_w = weight_keys - set(self.weights.keys())
        if missing_w:
            raise DataValidationError(f"Missing weights keys: {sorted(missing_w)}")

    # Weighted average of feature badness values.
    # Final score normalized to [0,1] to make cutoff comparable across samples.

    def feature_badness(self, s: WaterSample) -> Dict[str, float]:
        """Compute per-feature badness in [0,1]."""
        s.validate()
        T = self.thresholds

        # pH badness: 0 inside [ph_low, ph_high], increases outside
        if T["ph_low"] <= s.ph <= T["ph_high"]:
            ph_bad = 0.0
        else:
            dist = (T["ph_low"] - s.ph) if s.ph < T["ph_low"] else (s.ph - T["ph_high"])
            ph_bad = min(1.0, dist / 2.0)

        turb_bad = min(1.0, s.turbidity / T["turbidity_max"]) if T["turbidity_max"] > 0 else 0.0
        cond_bad = min(1.0, s.conductivity / T["conductivity_max"]) if T["conductivity_max"] > 0 else 0.0
        chl_bad = min(1.0, s.chlorophyll / T["chlorophyll_max"]) if T["chlorophyll_max"] > 0 else 0.0
        sal_bad = min(1.0, s.salinity / T["salinity_max"]) if T["salinity_max"] > 0 else 0.0

        # DO badness: 0 inside [do_low, do_high], increases outside
        if T["do_low"] <= s.dissolved_oxygen <= T["do_high"]:
            do_bad = 0.0
        else:
            dist = (T["do_low"] - s.dissolved_oxygen) if s.dissolved_oxygen < T["do_low"] else (s.dissolved_oxygen - T["do_high"])
            do_bad = min(1.0, dist / 2.0)

        # Temperature badness: 0 inside [temp_low, temp_high]
        if T["temp_low"] <= s.temperature <= T["temp_high"]:
            temp_bad = 0.0
        else:
            dist = (T["temp_low"] - s.temperature) if s.temperature < T["temp_low"] else (s.temperature - T["temp_high"])
            temp_bad = min(1.0, dist / 5.0)

        return {
            "ph": ph_bad,
            "turbidity": turb_bad,
            "conductivity": cond_bad,
            "chlorophyll": chl_bad,
            "dissolved_oxygen": do_bad,
            "salinity": sal_bad,
            "temperature": temp_bad,
        }

    def risk_score(self, s: WaterSample) -> float:
        """Weighted risk score in [0,1]."""
        bad = self.feature_badness(s)
        total_w = sum(float(self.weights[k]) for k in bad.keys())
        if total_w <= 0:
            raise DataValidationError("Weights must sum to a positive value.")
        score = sum(float(self.weights[k]) * bad[k] for k in bad.keys()) / total_w
        return float(max(0.0, min(1.0, score)))

    def classify(self, s: WaterSample) -> str:
        """Return Safe/Unsafe (if statement requirement)."""
        score = self.risk_score(s)
        return "Unsafe" if score >= self.unsafe_cutoff else "Safe"

    def evaluate(self, samples: Iterable[WaterSample]) -> List[Tuple[WaterSample, float, str]]:
        """Evaluate many samples. Uses enumerate() (Part 2 special function)."""
        results: List[Tuple[WaterSample, float, str]] = []
        for i, s in enumerate(samples):
            try:
                score = self.risk_score(s)
                label = "Unsafe" if score >= self.unsafe_cutoff else "Safe"
                results.append((s, score, label))
            except DataValidationError:
                # exception containment: skip invalid samples
                continue
        return results

    def __str__(self) -> str:
        return f"WaterQualityModel(cutoff={self.unsafe_cutoff})"


def default_model() -> WaterQualityModel:
    """Default model config (generic starter)."""
    thresholds = {
        "ph_low": 6.5,
        "ph_high": 8.5,
        "turbidity_max": 10.0,
        "conductivity_max": 3000.0,
        "chlorophyll_max": 50.0,
        "do_low": 4.0,
        "do_high": 12.0,
        "salinity_max": 40.0,
        "temp_low": 10.0,
        "temp_high": 30.0,
    }
    weights = {
        "ph": 0.10,
        "turbidity": 0.20,
        "conductivity": 0.10,
        "chlorophyll": 0.25,
        "dissolved_oxygen": 0.20,
        "salinity": 0.10,
        "temperature": 0.05,
    }
    return WaterQualityModel(thresholds=thresholds, weights=weights, unsafe_cutoff=0.60)

