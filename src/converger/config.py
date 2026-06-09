import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


@dataclass(frozen=True)
class ArtifactPaths:
    current: str = "current.json"
    plan: str = "plan.json"
    result: str = "result.json"


@dataclass(frozen=True)
class ProxmoxConfig:
    host: str
    user: str
    token_name: str
    token_value: str
    verify_ssl: bool = False
    node: Optional[str] = None

    def as_adapter_config(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "user": self.user,
            "token_name": self.token_name,
            "token_value": self.token_value,
            "verify_ssl": self.verify_ssl,
            "node": self.node,
        }


@dataclass(frozen=True)
class ConvergerConfig:
    proxmox: Optional[ProxmoxConfig]
    artifacts: ArtifactPaths
    config_path: Optional[Path] = None


def _substitute_env(value: Any) -> Any:
    if isinstance(value, str):

        def replacer(match: re.Match[str]) -> str:
            key = match.group(1)
            env_value = os.environ.get(key)
            if env_value is None:
                raise ValueError(f"Environment variable {key!r} is not set")
            return env_value

        return _ENV_PATTERN.sub(replacer, value)
    if isinstance(value, dict):
        return {key: _substitute_env(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_substitute_env(item) for item in value]
    return value


def _proxmox_from_env() -> Optional[ProxmoxConfig]:
    host = os.environ.get("PROXMOX_HOST")
    user = os.environ.get("PROXMOX_USER")
    token_name = os.environ.get("PROXMOX_TOKEN_NAME")
    token_value = os.environ.get("PROXMOX_TOKEN_VALUE")
    if not all([host, user, token_name, token_value]):
        return None

    return ProxmoxConfig(
        host=host,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=os.environ.get("PROXMOX_VERIFY_SSL", "false").lower() == "true",
        node=os.environ.get("PROXMOX_NODE"),
    )


def load_config(path: Optional[str | Path] = None) -> ConvergerConfig:
    config_path = Path(path) if path else _default_config_path()
    artifacts = ArtifactPaths()
    proxmox: Optional[ProxmoxConfig] = _proxmox_from_env()

    if config_path and config_path.exists():
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        raw = _substitute_env(raw)

        artifact_raw = raw.get("artifacts", {})
        artifacts = ArtifactPaths(
            current=artifact_raw.get("current", artifacts.current),
            plan=artifact_raw.get("plan", artifacts.plan),
            result=artifact_raw.get("result", artifacts.result),
        )

        proxmox_raw = raw.get("proxmox")
        if proxmox_raw:
            proxmox = ProxmoxConfig(
                host=proxmox_raw["host"],
                user=proxmox_raw["user"],
                token_name=proxmox_raw["token_name"],
                token_value=proxmox_raw["token_value"],
                verify_ssl=bool(proxmox_raw.get("verify_ssl", False)),
                node=proxmox_raw.get("node"),
            )

    return ConvergerConfig(
        proxmox=proxmox,
        artifacts=artifacts,
        config_path=config_path if config_path and config_path.exists() else None,
    )


def _default_config_path() -> Path:
    for candidate in (Path("converger.yaml"), Path("converger.yml")):
        if candidate.exists():
            return candidate
    return Path("converger.yaml")


def require_proxmox(config: ConvergerConfig) -> ProxmoxConfig:
    if config.proxmox is None:
        raise ValueError(
            "Proxmox credentials are required. Provide converger.yaml or set "
            "PROXMOX_HOST, PROXMOX_USER, PROXMOX_TOKEN_NAME, PROXMOX_TOKEN_VALUE."
        )
    return config.proxmox
