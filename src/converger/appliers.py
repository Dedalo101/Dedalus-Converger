from .adapters.aws_apply import AwsApplier
from .adapters.hetzner_apply import HetznerApplier
from .adapters.proxmox_apply import ProxmoxApplier
from .config import (
    ConvergerConfig,
    require_aws,
    require_hetzner,
    require_proxmox,
)

APPLICABLE_SOURCES = frozenset({"proxmox", "aws", "hetzner"})


def create_applier(config: ConvergerConfig, source: str, *, dry_run: bool = False):
    if source not in APPLICABLE_SOURCES:
        raise ValueError(
            f"Apply is not supported for source {source!r}. "
            f"Supported: {sorted(APPLICABLE_SOURCES)}"
        )

    if source == "proxmox":
        return ProxmoxApplier(
            require_proxmox(config).as_adapter_config(), dry_run=dry_run
        )
    if source == "aws":
        return AwsApplier(require_aws(config).as_adapter_config(), dry_run=dry_run)
    if source == "hetzner":
        return HetznerApplier(
            require_hetzner(config).as_adapter_config(), dry_run=dry_run
        )
    raise ValueError(f"Unsupported apply source: {source}")
