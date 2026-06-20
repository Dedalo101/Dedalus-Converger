"""Create or update a GitHub-connected Cloudflare Pages project."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "cf0fd21cb134442849cf898375cbdbe3")
PROJECT_NAME = os.environ.get("CLOUDFLARE_PAGES_PROJECT", "dedalus-converger")
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")


def cf_request(method: str, path: str, payload: dict | None = None) -> dict:
    if not API_TOKEN:
        raise RuntimeError("CLOUDFLARE_API_TOKEN is required")

    data = None
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
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
        raise RuntimeError(f"Cloudflare API {method} {path} failed: {exc.code} {body}") from exc


def project_exists() -> bool:
    response = cf_request(
        "GET", f"/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}"
    )
    return bool(response.get("success"))


def create_project() -> None:
    payload = {
        "name": PROJECT_NAME,
        "production_branch": "main",
        "source": {
            "type": "github",
            "config": {
                "owner": "Dedalo101",
                "repo_name": "Dedalus-Converger",
                "production_branch": "main",
                "pr_comments_enabled": True,
                "deployments_enabled": True,
                "production_deployments_enabled": True,
                "preview_deployment_setting": "all",
                "preview_branch_includes": ["*"],
                "preview_branch_excludes": [],
                "path_includes": ["*"],
                "path_excludes": [],
            },
        },
        "build_config": {
            "build_command": "",
            "destination_dir": "site",
            "root_dir": "",
        },
    }
    response = cf_request(
        "POST", f"/accounts/{ACCOUNT_ID}/pages/projects", payload
    )
    if not response.get("success"):
        raise RuntimeError(f"Create project failed: {response}")


def main() -> int:
    if project_exists():
        print(f"Project {PROJECT_NAME} already exists.")
        return 0
    create_project()
    print(f"Created Cloudflare Pages project {PROJECT_NAME}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())