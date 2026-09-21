"""Fail if tuya_ble imports removed Home Assistant Tuya constants."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "tuya_ble"
FORBIDDEN_MODULE_PREFIX = "homeassistant.components.tuya"


def _core_tuya_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == FORBIDDEN_MODULE_PREFIX or node.module.startswith(
                FORBIDDEN_MODULE_PREFIX + "."
            ):
                names = ", ".join(alias.name for alias in node.names)
                found.append(f"{path}:{node.lineno} from {node.module} import {names}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == FORBIDDEN_MODULE_PREFIX or alias.name.startswith(
                    FORBIDDEN_MODULE_PREFIX + "."
                ):
                    found.append(f"{path}:{node.lineno} import {alias.name}")
    return found


def test_no_core_tuya_imports() -> None:
    offenders: list[str] = []
    for path in ROOT.rglob("*.py"):
        offenders.extend(_core_tuya_imports(path))
    assert not offenders, "do not import core tuya constants:\n" + "\n".join(offenders)


def test_conf_app_type_is_local() -> None:
    const_text = (ROOT / "const.py").read_text()
    assert 'CONF_APP_TYPE = "app_type"' in const_text
    assert 'CONF_APP_TYPE_LEGACY = "tuya_app_type"' in const_text


def test_cloud_maps_legacy_app_type() -> None:
    cloud_text = (ROOT / "cloud.py").read_text()
    assert "def _normalize_login_data" in cloud_text
    assert "CONF_APP_TYPE_LEGACY" in cloud_text


def test_abort_does_not_reload_with_update_listener() -> None:
    flow_text = (ROOT / "config_flow.py").read_text()
    assert "_abort_if_unique_id_configured(reload_on_update=False)" in flow_text
    assert "_abort_if_unique_id_configured()" not in flow_text
    init_text = (ROOT / "__init__.py").read_text()
    assert "add_update_listener" in init_text


if __name__ == "__main__":
    test_no_core_tuya_imports()
    test_conf_app_type_is_local()
    test_cloud_maps_legacy_app_type()
    test_abort_does_not_reload_with_update_listener()
    print("ok")
