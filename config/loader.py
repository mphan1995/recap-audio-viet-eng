import os
from typing import Any, Dict, Iterable, Optional

import yaml


DEFAULT_SETTINGS_PATH = os.getenv("RECAP_SETTINGS_PATH", "config/settings.yaml")


def load_settings(path: Optional[str] = None) -> Dict[str, Any]:
    settings_path = path or DEFAULT_SETTINGS_PATH
    if not os.path.exists(settings_path):
        return {}

    with open(settings_path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            return {}
        return data


def get_setting(settings: Dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    current: Any = settings
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def merge_settings(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not overrides:
        return base
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_settings(merged[key], value)
        else:
            merged[key] = value
    return merged
