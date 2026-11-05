"""Resolve originals in either a scratch cache or the preserved private library."""
from pathlib import Path

def resolve_source(cache, relative):
    cache=Path(cache)
    candidates=[cache/relative,cache/'collections'/relative]
    prefix='opening-scenes-2026-11-05/'
    if relative.startswith(prefix):
        candidates.append(cache/'collections/research'/relative[len(prefix):])
    horizon_prefix='opening-horizons-2026-11-05/'
    if relative.startswith(horizon_prefix):
        candidates.append(cache/'collections/horizons'/relative[len(horizon_prefix):])
    expansion_prefix='opening-expansion-2026-11-06/'
    if relative.startswith(expansion_prefix):
        candidates.append(cache/'collections/expansion-2026-11-06'/relative[len(expansion_prefix):])
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f'Original not found in source cache: {relative}')
