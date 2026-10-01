from __future__ import annotations


def generate_public_id(prefix: str, sequence: int) -> str:
    """
    Generate a human-readable public ID, e.g. P-0001, D-0042.

    prefix  — single letter: P (patient), D (doctor), N (nurse), A (admin)
    sequence — integer from a DB sequence or COUNT
    """
    return f"{prefix}-{sequence:04d}"
