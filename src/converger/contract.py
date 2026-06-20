import hashlib
from pathlib import Path

DESIGN_HASH = "f24992c8b729a3adc28c92ab068e1d88f2245bf852fb8272c88b183e24db6bee"


def verify_contract() -> None:
    path = Path(__file__).resolve().parents[2] / "docs" / "DESIGN.md"
    if not path.exists():
        raise FileNotFoundError("docs/DESIGN.md missing from repository")

    content = path.read_bytes()
    computed = hashlib.sha256(content).hexdigest()
    if computed != DESIGN_HASH:
        raise ValueError(
            "docs/DESIGN.md contract violated!\n"
            f"Expected: {DESIGN_HASH}\n"
            f"Got:      {computed}"
        )
