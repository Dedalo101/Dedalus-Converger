import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")
VALID_SOURCES = {"proxmox", "aws", "hetzner", "replay", "dfir"}


@dataclass(frozen=True)
class ArtifactPaths:
    current: str = "current.json"
    plan: str = "plan.json"
    result: str = "result.json"
    post_apply: str = "post_apply.json"


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
class AwsConfig:
    region: str
    profile: Optional[str] = None
    vmid_tag: str = "converger:vmid"
    name_tag: str = "Name"
    scope_tag_key: Optional[str] = None
    scope_tag_value: Optional[str] = None

    def as_adapter_config(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "profile": self.profile,
            "vmid_tag": self.vmid_tag,
            "name_tag": self.name_tag,
            "scope_tag_key": self.scope_tag_key,
            "scope_tag_value": self.scope_tag_value,
        }


@dataclass(frozen=True)
class HetznerConfig:
    api_token: str
    label_selector: Optional[str] = None

    def as_adapter_config(self) -> dict[str, Any]:
        return {
            "api_token": self.api_token,
            "label_selector": self.label_selector,
        }


@dataclass(frozen=True)
class DfirConfig:
    format: str = "auto"
    entities_key: str = "systems"
    field_map: dict[str, str] = field(default_factory=dict)
    status_map: dict[str, str] = field(
        default_factory=lambda: {
            "running": "running",
            "on": "running",
            "online": "running",
            "up": "running",
            "stopped": "stopped",
            "off": "stopped",
            "offline": "stopped",
            "down": "stopped",
            "poweredoff": "stopped",
        }
    )

    def as_adapter_config(self, path: str) -> dict[str, Any]:
        return {
            "path": path,
            "format": self.format,
            "entities_key": self.entities_key,
            "field_map": self.field_map,
            "status_map": self.status_map,
        }


@dataclass(frozen=True)
class ConvergerConfig:
    source: str
    proxmox: Optional[ProxmoxConfig]
    aws: Optional[AwsConfig]
    hetzner: Optional[HetznerConfig]
    dfir: DfirConfig
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


def _aws_from_env() -> Optional[AwsConfig]:
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if not region:
        return None
    return AwsConfig(
        region=region,
        profile=os.environ.get("AWS_PROFILE"),
        vmid_tag=os.environ.get("CONVERGER_AWS_VMID_TAG", "converger:vmid"),
        name_tag=os.environ.get("CONVERGER_AWS_NAME_TAG", "Name"),
    )


def _hetzner_from_env() -> Optional[HetznerConfig]:
    token = os.environ.get("HETZNER_API_TOKEN")
    if not token:
        return None
    return HetznerConfig(api_token=token)


def load_config(path: Optional[str | Path] = None) -> ConvergerConfig:
    config_path = Path(path) if path else _default_config_path()
    artifacts = ArtifactPaths()
    source = os.environ.get("CONVERGER_SOURCE", "proxmox")
    proxmox: Optional[ProxmoxConfig] = _proxmox_from_env()
    aws: Optional[AwsConfig] = _aws_from_env()
    hetzner: Optional[HetznerConfig] = _hetzner_from_env()
    dfir = DfirConfig()

    if config_path and config_path.exists():
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        raw = _substitute_env(raw)

        source = raw.get("source", source)
        artifact_raw = raw.get("artifacts", {})
        artifacts = ArtifactPaths(
            current=artifact_raw.get("current", artifacts.current),
            plan=artifact_raw.get("plan", artifacts.plan),
            result=artifact_raw.get("result", artifacts.result),
            post_apply=artifact_raw.get("post_apply", artifacts.post_apply),
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

        aws_raw = raw.get("aws")
        if aws_raw:
            scope_tag = aws_raw.get("scope_tag", {})
            aws = AwsConfig(
                region=aws_raw["region"],
                profile=aws_raw.get("profile"),
                vmid_tag=aws_raw.get("vmid_tag", "converger:vmid"),
                name_tag=aws_raw.get("name_tag", "Name"),
                scope_tag_key=scope_tag.get("key"),
                scope_tag_value=scope_tag.get("value"),
            )

        hetzner_raw = raw.get("hetzner")
        if hetzner_raw:
            hetzner = HetznerConfig(
                api_token=hetzner_raw["api_token"],
                label_selector=hetzner_raw.get("label_selector"),
            )

        dfir_raw = raw.get("dfir", {})
        if dfir_raw:
            dfir = DfirConfig(
                format=dfir_raw.get("format", "auto"),
                entities_key=dfir_raw.get("entities_key", "systems"),
                field_map=dfir_raw.get("field_map", {}),
                status_map={**dfir.status_map, **dfir_raw.get("status_map", {})},
            )

    if source not in VALID_SOURCES:
        raise ValueError(f"Invalid source {source!r}. Must be one of: {VALID_SOURCES}")

    return ConvergerConfig(
        source=source,
        proxmox=proxmox,
        aws=aws,
        hetzner=hetzner,
        dfir=dfir,
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


def require_aws(config: ConvergerConfig) -> AwsConfig:
    if config.aws is None:
        raise ValueError(
            "AWS config is required. Provide aws.region in converger.yaml or set AWS_REGION."
        )
    return config.aws


def require_hetzner(config: ConvergerConfig) -> HetznerConfig:
    if config.hetzner is None:
        raise ValueError(
            "Hetzner config is required. Provide hetzner.api_token or set HETZNER_API_TOKEN."
        )
    return config.hetzner


def adapter_config_for_source(
    config: ConvergerConfig,
    source: str,
    *,
    replay_path: Optional[str] = None,
    dfir_path: Optional[str] = None,
) -> dict[str, Any]:
    if source == "proxmox":
        return require_proxmox(config).as_adapter_config()
    if source == "aws":
        return require_aws(config).as_adapter_config()
    if source == "hetzner":
        return require_hetzner(config).as_adapter_config()
    if source == "replay":
        if not replay_path:
            raise ValueError("Replay source requires --replay path")
        return {"path": replay_path}
    if source == "dfir":
        if not dfir_path:
            raise ValueError("DFIR source requires --dfir path")
        return config.dfir.as_adapter_config(dfir_path)
    raise ValueError(f"Unsupported source: {source}")
