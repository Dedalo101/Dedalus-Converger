from pathlib import Path

import pytest
import yaml

from converger.config import load_config, require_proxmox


def test_load_config_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PROXMOX_HOST", raising=False)
    config_file = tmp_path / "converger.yaml"
    config_file.write_text(
        yaml.safe_dump(
            {
                "proxmox": {
                    "host": "pve.local",
                    "user": "root@pam",
                    "token_name": "converger",
                    "token_value": "secret-token",
                    "verify_ssl": True,
                    "node": "pve1",
                },
                "artifacts": {
                    "current": "snap.json",
                    "plan": "diff.json",
                    "result": "out.json",
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_file)
    assert config.proxmox is not None
    assert config.proxmox.host == "pve.local"
    assert config.proxmox.node == "pve1"
    assert config.artifacts.current == "snap.json"
    assert config.artifacts.plan == "diff.json"
    assert config.artifacts.result == "out.json"


def test_env_substitution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "from-env")
    config_file = tmp_path / "converger.yaml"
    config_file.write_text(
        "proxmox:\n"
        "  host: pve.local\n"
        "  user: root@pam\n"
        "  token_name: converger\n"
        "  token_value: ${PROXMOX_TOKEN_VALUE}\n",
        encoding="utf-8",
    )

    config = load_config(config_file)
    assert config.proxmox.token_value == "from-env"


def test_env_fallback_when_no_yaml(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PROXMOX_HOST", "pve.local")
    monkeypatch.setenv("PROXMOX_USER", "root@pam")
    monkeypatch.setenv("PROXMOX_TOKEN_NAME", "converger")
    monkeypatch.setenv("PROXMOX_TOKEN_VALUE", "secret")
    config = load_config(Path("missing.yaml"))
    proxmox = require_proxmox(config)
    assert proxmox.host == "pve.local"
