"""Defines WaterSample and timestamp parsing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .exceptions import DataValidationError


@dataclass(frozen=True, slots=True)
class WaterSample:
    """Represents a single water sample record (sensor snapshot).

    Notes
    -----
    Includes:
    - validation
    - __str__ (Part 2)
    - operator overloading (__lt__) (Part 2)
    """

    sample_id: str
    timestamp: Optional[datetime]

    ph: float
    turbidity: float
    conductivity: float
    dissolved_oxygen: float
    temperature: float
    salinity: float
    chlorophyll: float

    def validate(self) -> None:
        """Validate ranges to catch obvious sensor/data errors."""
        if not self.sample_id:
            raise DataValidationError("sample_id must be a non-empty string.")

        if not (0.0 <= float(self.ph) <= 14.0):
            raise DataValidationError(f"Invalid pH={self.ph}. Expected within [0, 14].")

        for name, val in [
            ("turbidity", self.turbidity),
            ("conductivity", self.conductivity),
            ("dissolved_oxygen", self.dissolved_oxygen),
            ("salinity", self.salinity),
            ("chlorophyll", self.chlorophyll),
        ]:
            if float(val) < 0.0:
                raise DataValidationError(f"Invalid {name}={val}. Expected >= 0.")

        if not (-5.0 <= float(self.temperature) <= 45.0):
            raise DataValidationError(f"Invalid temperature={self.temperature}. Expected within [-5, 45].")

    def __str__(self) -> str:
        ts = self.timestamp.isoformat() if self.timestamp else "NA"
        return (
            f"WaterSample(id={self.sample_id}, ts={ts}, ph={self.ph:.2f}, turb={self.turbidity:.2f}, "
            f"cond={self.conductivity:.2f}, DO={self.dissolved_oxygen:.2f}, temp={self.temperature:.2f}, "
            f"sal={self.salinity:.2f}, chl={self.chlorophyll:.2f})"
        )

    def __lt__(self, other: "WaterSample") -> bool:
        """Operator overloading: allow sorting by timestamp then id."""
        if not isinstance(other, WaterSample):
            return NotImplemented
        if self.timestamp and other.timestamp:
            return (self.timestamp, self.sample_id) < (other.timestamp, other.sample_id)
        return self.sample_id < other.sample_id


def parse_timestamp(value: object) -> Optional[datetime]:
    """Parse timestamps from common formats (built-in datetime)."""
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in {"na", "nan", "none"}:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None
