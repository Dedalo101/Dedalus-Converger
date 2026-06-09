from typing import Dict

from .config import DfirConfig

PRESET_NAMES = frozenset({"velociraptor", "kape"})

_VELOCIRAPTOR = DfirConfig(
    format="envelope",
    entities_key="items",
    field_map={
        "vmid": "client_id",
        "name": "hostname",
        "status": "last_seen",
        "cpus": "cpu_count",
        "maxmem": "memory_bytes",
        "node": "site",
    },
    status_map={
        "online": "running",
        "offline": "stopped",
        "running": "running",
        "stopped": "stopped",
        "unknown": "unknown",
    },
)

_KAPE = DfirConfig(
    format="envelope",
    entities_key="hosts",
    field_map={
        "vmid": "system_id",
        "name": "computer_name",
        "status": "boot_state",
        "cpus": "processor_count",
        "maxmem": "physical_memory_bytes",
        "node": "collection_host",
    },
    status_map={
        "booted": "running",
        "shutdown": "stopped",
        "hibernate": "stopped",
        "online": "running",
        "offline": "stopped",
    },
)

PRESETS: Dict[str, DfirConfig] = {
    "velociraptor": _VELOCIRAPTOR,
    "kape": _KAPE,
}


def get_preset(name: str) -> DfirConfig:
    normalized = name.lower()
    if normalized not in PRESETS:
        raise ValueError(
            f"Unknown DFIR preset {name!r}. Available: {sorted(PRESET_NAMES)}"
        )
    return PRESETS[normalized]


def merge_dfir_config(base: DfirConfig, preset_name: str | None) -> DfirConfig:
    if not preset_name:
        return base

    preset = get_preset(preset_name)
    use_preset_entities = not base.field_map and base.entities_key == "systems"
    return DfirConfig(
        format=base.format if base.format != "auto" else preset.format,
        entities_key=preset.entities_key if use_preset_entities else base.entities_key,
        field_map={**preset.field_map, **base.field_map},
        status_map={**preset.status_map, **base.status_map},
    )
