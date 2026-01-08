import hashlib
from pathlib import Path

# SHA256 hash of docs/DESIGN.md as of 2026-01-08 (locked contract)
# We will compute the real hash after final stabilization
DESIGN_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # placeholder — update soon


def verify_contract() -> None:
    """Fail fast if DESIGN.md changed without version bump."""
    design_path = Path(__file__).parent.parent / "docs" / "DESIGN.md"
    if not design_path.exists():
        raise RuntimeError("docs/DESIGN.md missing — contract cannot be verified")

    actual = hashlib.sha256(design_path.read_bytes()).hexdigest()
    if actual != DESIGN_HASH:
        raise RuntimeError(
            "DESIGN.md changed without updating DESIGN_HASH.\n"
            "This violates the locked contract.\n"
            "Requires major version bump and unanimous review."
        )
