"""Gestion des settings Claude Code (permissions, mode)."""

import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(DIR, ".claude", "settings.local.json")

PERMISSION_MODES = {
    "default": "Demande pour chaque outil",
    "acceptEdits": "Auto-accepte les éditions de fichiers",
    "bypassPermissions": "Accepte tout sans confirmation",
    "dontAsk": "Refuse sauf permissions explicites",
    "plan": "Lecture seule (pas de modifications)",
}

PERMISSION_PRESETS = {
    "Édition de fichiers (Edit, Write)": ["Edit", "Write"],
    "Accès web (WebFetch, WebSearch)": ["WebFetch", "WebSearch"],
    "Lecture (Read, Glob, Grep)": ["Read", "Glob", "Grep"],
}

DEFAULT_SETTINGS = {
    "permissions": {
        "allow": ["mcp__acp__Edit", "mcp__acp__Bash", "mcp__acp__Write"],
        "deny": [],
    },
    "telebot": {
        "permission_mode": "default",
    },
}


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return json.loads(json.dumps(DEFAULT_SETTINGS))
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_SETTINGS))


def save_settings(data: dict):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_permission_mode() -> str:
    data = load_settings()
    return data.get("telebot", {}).get("permission_mode", "default")


def set_permission_mode(mode: str):
    data = load_settings()
    data.setdefault("telebot", {})["permission_mode"] = mode
    save_settings(data)


def get_allowed() -> list[str]:
    data = load_settings()
    return data.get("permissions", {}).get("allow", [])


def get_user_allowed() -> list[str]:
    """Retourne les permissions allow sans les mcp__*."""
    return [p for p in get_allowed() if not p.startswith("mcp__")]


def get_bash_rules() -> list[str]:
    """Retourne les règles Bash(pattern) de la liste allow."""
    return [p for p in get_allowed() if p.startswith("Bash(")]


def add_permission(rule: str):
    data = load_settings()
    allow = data.setdefault("permissions", {}).setdefault("allow", [])
    if rule not in allow:
        allow.append(rule)
    save_settings(data)


def remove_permission(rule: str):
    data = load_settings()
    allow = data.get("permissions", {}).get("allow", [])
    if rule in allow:
        allow.remove(rule)
        save_settings(data)


def is_preset_enabled(preset_rules: list[str]) -> bool:
    allowed = get_allowed()
    return all(r in allowed for r in preset_rules)


def toggle_preset(preset_rules: list[str], enable: bool):
    data = load_settings()
    allow = data.setdefault("permissions", {}).setdefault("allow", [])
    for rule in preset_rules:
        if enable and rule not in allow:
            allow.append(rule)
        elif not enable and rule in allow:
            allow.remove(rule)
    save_settings(data)


def get_claude_flags() -> str:
    mode = get_permission_mode()
    flags = []
    if mode != "default":
        flags.append(f"--permission-mode {mode}")
    return " ".join(flags)


def reset_to_defaults():
    save_settings(json.loads(json.dumps(DEFAULT_SETTINGS)))
