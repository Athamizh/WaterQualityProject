import pandas as pd
import pytest

from src.loader import DatasetLoader
from src.exceptions import DataValidationError


def test_loader_missing_required_columns_raises():
    # Intentionally missing required columns (should raise)
    df = pd.DataFrame(
        {
            "Record number": [1],
            "Timestamp": ["2025-01-01 00:00:00"],
            "pH": [7.0],
        }
    )
    loader = DatasetLoader(csv_path="dummy.csv")
    with pytest.raises(DataValidationError):
        loader.build_samples(df)
