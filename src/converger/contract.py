import hashlib
import os

DESIGN_HASH = "7e7b17c8bc05f4fdae25b5c6a3ea0c21fe012cdea4d3cb77a8228aadeca3da8e"

def verify_contract():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "DESIGN.md")
    try:
        with open(path, "rb") as f:
            content = f.read()
        computed = hashlib.sha256(content).hexdigest()
        if computed != DESIGN_HASH:
            raise ValueError(
                f"DESIGN.md violated!\nExpected: {DESIGN_HASH}\nGot: {computed}"
            )
    except FileNotFoundError:
        raise FileNotFoundError("DESIGN.md missing")
