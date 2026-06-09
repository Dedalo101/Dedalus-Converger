import hashlib
from pathlib import Path

DESIGN_HASH = "fa9f7473fef3b2f82469ee875298713684ec4db96e512707053ae8bb8ed22279"


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
