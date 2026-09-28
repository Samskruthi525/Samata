"""Storage sizing (design doc §14.2). Illustrative: measure a pilot batch first."""
MIB_PER_GIB = 1024


def master_gib(pages: int, mean_mib_per_page: float = 25.0) -> float:
    return pages * mean_mib_per_page / MIB_PER_GIB


def logical_copies_gib(pages: int, copies: int = 3, mean_mib_per_page: float = 25.0) -> float:
    """Replicated logical bytes - NOT vendor billing or a backup design."""
    return master_gib(pages, mean_mib_per_page) * copies


def av_gib(hours: float, mbit_per_s: float) -> float:
    return hours * 3600 * mbit_per_s / 8 / MIB_PER_GIB
