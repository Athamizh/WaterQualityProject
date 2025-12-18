from datetime import datetime

from src.model import default_model
from src.samples import WaterSample


def test_model_classifies_unsafe_for_extreme_pollution_signals():
    model = default_model()

    # Extreme values so it MUST be unsafe under default model
    s = WaterSample(
        sample_id="1",
        timestamp=datetime(2025, 1, 1),
        ph=3.0,
        turbidity=500.0,
        conductivity=10000.0,
        dissolved_oxygen=0.5,
        temperature=40.0,
        salinity=80.0,
        chlorophyll=1000.0,
    )
    assert model.classify(s) == "Unsafe"


def test_risk_increases_with_higher_turbidity():
    model = default_model()
    low = WaterSample("L", None, 7.2, 1.0, 500.0, 7.0, 25.0, 5.0, 5.0)
    high = WaterSample("H", None, 7.2, 20.0, 500.0, 7.0, 25.0, 5.0, 5.0)
    assert model.risk_score(high) >= model.risk_score(low)
