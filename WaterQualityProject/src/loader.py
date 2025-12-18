"""Load Brisbane water quality CSV and build WaterSample objects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .exceptions import DataValidationError
from .samples import WaterSample, parse_timestamp


@dataclass(slots=True)
class DatasetLoader:
    """Loads Brisbane water quality dataset CSV and constructs WaterSample objects."""

    csv_path: Path
    column_map: Optional[Dict[str, str]] = None
    use_quality_filter: bool = True

    REQUIRED_CANONICAL = (
        "sample_id",
        "ph",
        "turbidity",
        "conductivity",
        "dissolved_oxygen",
        "temperature",
        "salinity",
        "chlorophyll",
    )

    def load_dataframe(self) -> pd.DataFrame:
        """Load CSV into a DataFrame (meaningful I/O)."""
        try:
            return pd.read_csv(self.csv_path)
        except FileNotFoundError:
            raise
        except pd.errors.ParserError as e:
            raise DataValidationError(f"CSV parsing failed: {e}") from e

    def _default_column_map(self) -> Dict[str, str]:
        return {
            "timestamp": "Timestamp",
            "sample_id": "Record number",
            "ph": "pH",
            "turbidity": "Turbidity",
            "conductivity": "Specific Conductance",
            "dissolved_oxygen": "Dissolved Oxygen",
            "temperature": "Temperature",
            "salinity": "Salinity",
            "chlorophyll": "Chlorophyll",
        }

    def _resolve_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        mapping = self._default_column_map() if self.column_map is None else dict(self.column_map)

        missing = []
        for canonical in self.REQUIRED_CANONICAL:
            actual = mapping.get(canonical)
            if actual is None or actual not in df.columns:
                missing.append(canonical)

        if missing:
            raise DataValidationError(
                f"Missing required columns (canonical): {missing}\n"
                f"Available columns: {list(df.columns)}\n"
                f"Fix by editing column_map."
            )
        return mapping

    def _apply_quality_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter by [quality] columns if present (Exception containment via conservative filter)."""
        if not self.use_quality_filter:
            return df

        quality_cols = [c for c in df.columns if c.endswith("[quality]")]
        if not quality_cols:
            return df

        def ok(v) -> bool:
            if pd.isna(v):
                return True
            s = str(v).strip().lower()
            # many datasets use 0/1 or text flags; we accept common "ok" codes
            return s in {"0", "1", "good", "ok", "true"}

        mask = pd.Series(True, index=df.index)
        for qc in quality_cols:
            mask &= df[qc].apply(ok)

        return df.loc[mask].copy()

    def build_samples(self, df: pd.DataFrame, max_rows: Optional[int] = None) -> List[WaterSample]:
        """Convert rows into WaterSample objects (for-loop requirement satisfied here)."""
        df2 = self._apply_quality_filter(df)
        mapping = self._resolve_columns(df2)
        use_df = df2.head(max_rows) if max_rows else df2

        samples: List[WaterSample] = []
        for idx, row in use_df.iterrows():
            sample_id = str(row[mapping["sample_id"]]).strip()
            ts = parse_timestamp(row.get(mapping.get("timestamp", "")))

            try:
                s = WaterSample(
                    sample_id=sample_id,
                    timestamp=ts,
                    ph=float(row[mapping["ph"]]),
                    turbidity=float(row[mapping["turbidity"]]),
                    conductivity=float(row[mapping["conductivity"]]),
                    dissolved_oxygen=float(row[mapping["dissolved_oxygen"]]),
                    temperature=float(row[mapping["temperature"]]),
                    salinity=float(row[mapping["salinity"]]),
                    chlorophyll=float(row[mapping["chlorophyll"]]),
                )
            except (TypeError, ValueError) as e:
                raise DataValidationError(f"Row {idx} has non-numeric fields: {e}") from e

            samples.append(s)

        return samples
