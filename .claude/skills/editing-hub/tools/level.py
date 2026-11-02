"""Speaking level shared by the cutter and the checker.

Active-speech level: start from the 75th percentile of 10 ms frame loudness, then
settle on the median of the frames that are not dead (within 11 dB of the level).
"""
import numpy as np


def speaking_level(db, dead_db=11.0):
    lvl = float(np.percentile(db, 75))
    for _ in range(10):
        lvl = float(np.median(db[db >= lvl - dead_db]))
    return lvl


def preemph(x):
    """Tilt toward high frequencies so s, f, t and sh count as voice."""
    y = np.empty_like(x)
    y[0] = x[0]
    y[1:] = x[1:] - 0.97 * x[:-1]
    return y


def live_mask(db, pe, dead_db=11.0, lvl=None, lvl_pe=None):
    """Live = within dead_db of speaking level on either the plain or the tilted measure."""
    lvl = speaking_level(db, dead_db) if lvl is None else lvl
    lvl_pe = speaking_level(pe, dead_db) if lvl_pe is None else lvl_pe
    return (db >= lvl - dead_db) | (pe >= lvl_pe - dead_db), lvl, lvl_pe
