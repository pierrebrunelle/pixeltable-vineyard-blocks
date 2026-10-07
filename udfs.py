"""Pixeltable UDFs for the vineyard estate (recorded by module path, e.g. `udfs.yield_band`)."""
import pixeltable as pxt

SEASON = 2026


@pxt.udf
def vine_age(planted_year: int) -> int:
    return max(0, SEASON - planted_year)


@pxt.udf
def yield_per_acre(tons: float, acres: float) -> float:
    """Tons per acre, rounded to 0.01."""
    return round(tons / acres, 2) if acres > 0 else 0.0


@pxt.udf
def yield_band(tons: float, acres: float) -> str:
    """low (< 2.5 t/ac), mid (< 4.5 t/ac) or high."""
    tpa = tons / acres if acres > 0 else 0.0
    return 'low' if tpa < 2.5 else ('mid' if tpa < 4.5 else 'high')


@pxt.udf
def ripeness(brix: float) -> str:
    return 'underripe' if brix < 21 else ('ripe' if brix <= 25.5 else 'late-harvest')


@pxt.udf
def score_label(score: int) -> str:
    """Wine-critic style 100-point label."""
    if score >= 95:
        return 'classic'
    if score >= 90:
        return 'outstanding'
    if score >= 85:
        return 'very good'
    return 'good' if score >= 80 else 'fair'
