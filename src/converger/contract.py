import hashlib
import os

DESIGN_HASH = "7021488b8418c146bd1d82c289ed403ba07acabb2eadf0fa10989d2e1b66f956"

def verify_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "DESIGN.md")
    try:
        with open(path, "rb") as f:
            content = f.read()
        computed = hashlib.sha256(content).hexdigest()
        if computed != DESIGN_HASH:
            raise ValueError(
                f"DESIGN.md contract violated!\n"
                f"Expected: {DESIGN_HASH}\n"
                f"Got:      {computed}"
            )
    except FileNotFoundError:
        raise FileNotFoundError("DESIGN.md missing from repository root")
