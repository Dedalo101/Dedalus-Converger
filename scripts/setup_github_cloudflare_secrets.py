"""One-shot helper: set GitHub Actions secrets and dispatch Cloudflare deploy."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "Dedalo101/Dedalus-Converger"
ACCOUNT_ID = "cf0fd21cb134442849cf898375cbdbe3"


def git_github_token() -> str:
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise RuntimeError("GitHub token not found in credential manager")


def github_request(token: str, method: str, path: str, payload: dict | None = None):
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "dedalus-converger-setup",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def encrypt_secret(public_key: str, secret_value: str) -> str:
    try:
        from nacl import encoding, public
    except ImportError as exc:
        raise RuntimeError("PyNaCl is required: pip install pynacl") from exc

    pk = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed = public.SealedBox(pk).encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(sealed).decode("utf-8")


def put_secret(token: str, name: str, value: str, key_id: str, public_key: str) -> None:
    github_request(
        token,
        "PUT",
        f"/repos/{REPO}/actions/secrets/{name}",
        {
            "encrypted_value": encrypt_secret(public_key, value),
            "key_id": key_id,
        },
    )


def dispatch_deploy(token: str) -> None:
    github_request(
        token,
        "POST",
        f"/repos/{REPO}/actions/workflows/deploy-cloudflare.yml/dispatches",
        {"ref": "main"},
    )


def main() -> int:
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not cf_token:
        print("CLOUDFLARE_API_TOKEN is required", file=sys.stderr)
        return 1

    gh_token = git_github_token()
    key_info = github_request(
        gh_token, "GET", f"/repos/{REPO}/actions/secrets/public-key"
    )
    put_secret(
        gh_token,
        "CLOUDFLARE_API_TOKEN",
        cf_token,
        key_info["key_id"],
        key_info["key"],
    )
    put_secret(
        gh_token,
        "CLOUDFLARE_ACCOUNT_ID",
        ACCOUNT_ID,
        key_info["key_id"],
        key_info["key"],
    )
    dispatch_deploy(gh_token)
    print("GitHub secrets updated and deploy workflow dispatched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())