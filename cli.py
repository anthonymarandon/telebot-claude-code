#!/usr/bin/env python3
"""CLI interactif de gestion du bot Telegram Claude Code."""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

from simple_term_menu import TerminalMenu

import settings as telebot_settings

DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(DIR, ".bot.pid")
LOG_FILE = os.path.join(DIR, "bot.log")
ENV_FILE = os.path.join(DIR, ".env")
VENV_PYTHON = os.path.join(DIR, "venv", "bin", "python")
BOT_SCRIPT = os.path.join(DIR, "bot.py")


# --- Helpers ---


def get_python():
    if os.path.exists(VENV_PYTHON):
        return VENV_PYTHON
    return sys.executable


def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        os.remove(PID_FILE)
        return None


def bot_status_label():
    pid = read_pid()
    return f"\033[32m● actif (PID {pid})\033[0m" if pid else "\033[31m○ inactif\033[0m"


def tmux_status_label():
    ret = subprocess.run("tmux has-session -t claude", shell=True, capture_output=True)
    return (
        "\033[32m● active\033[0m"
        if ret.returncode == 0
        else "\033[31m○ inactive\033[0m"
    )


def parse_version(tag):
    """Convertit 'v1.3.0' en tuple (1, 3, 0) pour comparaison."""
    return tuple(int(x) for x in tag.lstrip("v").split("."))


def check_update(timeout=3):
    """Vérifie si une MAJ est dispo. Retourne (local, remote) ou None."""
    try:
        local = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if local.returncode != 0:
            return None
        local_tag = local.stdout.strip()

        remote = subprocess.run(
            ["git", "ls-remote", "--tags", "origin"],
            cwd=DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if remote.returncode != 0:
            return None

        tags = []
        for line in remote.stdout.splitlines():
            if "^{}" in line:
                continue
            m = re.search(r"refs/tags/(v[\d.]+)$", line)
            if m:
                tags.append(m.group(1))

        if not tags:
            return None

        latest = max(tags, key=parse_version)
        if parse_version(latest) > parse_version(local_tag):
            return (local_tag, latest)
        return None
    except Exception:
        return None


# --- Actions ---


def do_start(foreground=False):
    if read_pid():
        print("Le bot tourne déjà.")
        return

    if not os.path.exists(ENV_FILE):
        print("Fichier .env manquant.")
        print("  - telebot config")
        print("  - Menu > Paramètres > Configurer (token / user ID)")
        return

    env = _read_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    user_id = env.get("ALLOWED_USER_ID", "")
    if not token or not user_id:
        missing = []
        if not token:
            missing.append("Token Telegram")
        if not user_id:
            missing.append("User ID")
        print(f"Configuration incomplète ({', '.join(missing)}).")
        print("  - telebot config")
        print("  - Menu > Paramètres > Configurer (token / user ID)")
        return

    if foreground:
        print("Démarrage en avant-plan (Ctrl+C pour arrêter)...")
        os.execv(get_python(), [get_python(), BOT_SCRIPT])
    else:
        log = open(LOG_FILE, "a")
        proc = subprocess.Popen(
            [get_python(), BOT_SCRIPT],
            stdout=log,
            stderr=log,
            start_new_session=True,
            cwd=DIR,
        )
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        print(f"Bot démarré (PID {proc.pid}).")


def do_stop():
    pid = read_pid()
    if not pid:
        print("Le bot ne tourne pas.")
        return
    os.kill(pid, signal.SIGTERM)
    os.remove(PID_FILE)
    print("Bot arrêté.")


def do_restart():
    do_stop()
    do_start()


def do_status():
    print(f"Bot      : {bot_status_label()}")
    print(f"Session  : {tmux_status_label()}")


def do_logs(lines=30):
    if not os.path.exists(LOG_FILE):
        print("Aucun log.")
        return
    subprocess.run(["tail", f"-{lines}", LOG_FILE])


def _read_env():
    """Lit les valeurs actuelles du .env."""
    values = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    values[key.strip()] = val.strip()
    return values


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "***"
    return token[:4] + "…" + token[-4:]


def do_config():
    env = _read_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    user_id = env.get("ALLOWED_USER_ID", "")

    if token or user_id:
        print("  Configuration actuelle\n")
        print(f"  Token   : {_mask_token(token) if token else '(non défini)'}")
        print(f"  User ID : {user_id or '(non défini)'}")
        print()
        menu = TerminalMenu(
            ["Modifier", "← Retour"],
            title="  Que faire ?",
            menu_cursor="❯ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )
        if menu.show() != 0:
            return
        print()

    print("  Configuration du bot\n")
    new_token = input(
        f"  Token Telegram (BotFather) [{_mask_token(token) if token else ''}] : "
    ).strip()
    new_user_id = input(f"  User ID Telegram [{user_id}] : ").strip()
    with open(ENV_FILE, "w") as f:
        f.write(f"TELEGRAM_BOT_TOKEN={new_token or token}\n")
        f.write(f"ALLOWED_USER_ID={new_user_id or user_id}\n")
    print("\n  .env sauvegardé.")


def do_kill_all():
    pid = read_pid()
    if pid:
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        print("Bot arrêté.")
    else:
        print("Bot déjà inactif.")
    ret = subprocess.run("tmux has-session -t claude", shell=True, capture_output=True)
    if ret.returncode == 0:
        subprocess.run("tmux kill-session -t claude", shell=True, capture_output=True)
        print("Session tmux fermée.")
    else:
        print("Aucune session tmux active.")


def do_install():
    print("Installation des dépendances...")
    if not os.path.exists(os.path.join(DIR, "venv")):
        subprocess.run(
            [sys.executable, "-m", "venv", os.path.join(DIR, "venv")], check=True
        )
        print("Environnement virtuel créé.")
    subprocess.run(
        [
            get_python(),
            "-m",
            "pip",
            "install",
            "-q",
            "-r",
            os.path.join(DIR, "requirements.txt"),
        ],
        check=True,
    )
    print("Dépendances installées.")


def _get_modified_context_files():
    """Retourne la liste des fichiers .claude/ modifiés localement."""
    ret = subprocess.run(
        ["git", "diff", "--name-only", ".claude/"],
        cwd=DIR,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if ret.returncode != 0:
        return []
    return [f for f in ret.stdout.strip().splitlines() if f]


def do_update():
    print("Vérification des mises à jour...\n")
    result = check_update(timeout=10)
    if not result:
        print("Déjà à jour.")
        return
    local_tag, remote_tag = result
    print(f"  Version actuelle : {local_tag}")
    print(f"  Nouvelle version : \033[32m{remote_tag}\033[0m\n")
    menu = TerminalMenu(
        ["Oui, mettre à jour", "Non, annuler"],
        title="  Mettre à jour ?",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice != 0:
        print("Mise à jour annulée.")
        return

    # Détecter les fichiers de contexte modifiés par l'utilisateur
    modified = _get_modified_context_files()
    keep_context = False
    backup_dir = None

    if modified:
        print("\n  Fichiers de contexte personnalisés détectés :")
        for f in modified:
            print(f"    • {f}")
        print()
        ctx_menu = TerminalMenu(
            [
                "Garder mes personnalisations",
                "Écraser (revenir aux fichiers par défaut)",
            ],
            title="  Que faire de vos fichiers de contexte ?",
            menu_cursor="❯ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )
        ctx_choice = ctx_menu.show()
        keep_context = ctx_choice == 0

        if keep_context:
            # Sauvegarder les fichiers modifiés (arborescence préservée)
            backup_dir = os.path.join(DIR, ".claude_backup")
            for f in modified:
                src = os.path.join(DIR, f)
                dst = os.path.join(backup_dir, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

    was_running = read_pid() is not None
    if was_running:
        print("\nArrêt du bot avant mise à jour...")
        do_stop()

    # Reset les fichiers de contexte pour permettre le pull
    if modified:
        subprocess.run(
            ["git", "checkout", "--", ".claude/"],
            cwd=DIR,
            capture_output=True,
        )

    print("Téléchargement...")
    ret = subprocess.run(
        ["git", "pull", "--ff-only"],
        cwd=DIR,
        capture_output=True,
        text=True,
    )
    if ret.returncode != 0:
        print(f"\033[31mErreur git pull :\033[0m\n{ret.stderr}")
        # Restaurer le backup en cas d'échec
        if backup_dir:
            for f in modified:
                src = os.path.join(backup_dir, f)
                dst = os.path.join(DIR, f)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
            shutil.rmtree(backup_dir)
        return

    # Restaurer les personnalisations si demandé
    if keep_context and backup_dir:
        for f in modified:
            src = os.path.join(backup_dir, f)
            dst = os.path.join(DIR, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)
        shutil.rmtree(backup_dir)
        print("Personnalisations restaurées.")

    # Nettoyer le backup si écraser
    if backup_dir and os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)

    print("Mise à jour des dépendances...")
    subprocess.run(
        [
            get_python(),
            "-m",
            "pip",
            "install",
            "-q",
            "-r",
            os.path.join(DIR, "requirements.txt"),
        ],
        cwd=DIR,
    )

    print(f"\n\033[32mMis à jour vers {remote_tag}.\033[0m")

    if was_running:
        print("Redémarrage du bot...")
        do_start()

    print("Relancement du CLI...")
    python = get_python()
    os.execv(python, [python, os.path.join(DIR, "cli.py")])


def do_uninstall():
    """Désinstalle complètement Telebot (fichiers, venv, commande)."""
    bin_path = os.path.join(os.path.expanduser("~"), ".local", "bin", "telebot")

    print(f"  {C}Désinstallation de Telebot{R}\n")
    print("  Cette action va supprimer :")
    print(f"    • Le dossier complet    {D}{DIR}{R}")
    print(f"    • La commande           {D}{bin_path}{R}")
    print("    • Le .env (token inclus)")
    print("    • Les logs et le venv")
    print()

    menu = TerminalMenu(
        ["Oui, désinstaller", "Non, annuler"],
        title="  Supprimer définitivement Telebot ?",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
    )
    if menu.show() != 0:
        print("  Annulé.")
        return

    confirm = input(f"\n  Tape {C}DESINSTALLER{R} pour confirmer : ").strip()
    if confirm != "DESINSTALLER":
        print("  Annulé.")
        return

    print()

    # Arrêter le bot
    pid = read_pid()
    if pid:
        os.kill(pid, signal.SIGTERM)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        print("  Bot arrêté.")

    # Fermer la session tmux
    ret = subprocess.run("tmux has-session -t claude", shell=True, capture_output=True)
    if ret.returncode == 0:
        subprocess.run("tmux kill-session -t claude", shell=True, capture_output=True)
        print("  Session tmux fermée.")

    # Supprimer la commande telebot du PATH
    if os.path.exists(bin_path):
        os.remove(bin_path)
        print(f"  Commande supprimée : {bin_path}")

    # Supprimer le dossier complet
    install_dir = DIR
    shutil.rmtree(install_dir, ignore_errors=True)
    print(f"  Dossier supprimé : {install_dir}")

    print(f"\n  {C}Telebot a été désinstallé.{R}")
    sys.exit(0)


def do_reset_context():
    """Restaure les fichiers de contexte (.claude/) à leur état d'origine."""
    modified = _get_modified_context_files()
    if not modified:
        print("Les fichiers de contexte sont déjà à leur état d'origine.")
        return

    print("Fichiers modifiés :")
    for f in modified:
        print(f"  • {f}")
    print()
    menu = TerminalMenu(
        ["Oui, restaurer les fichiers par défaut", "Non, annuler"],
        title="  Remettre les fichiers de contexte par défaut ?",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice != 0:
        print("Annulé.")
        return

    subprocess.run(
        ["git", "checkout", "--", ".claude/"],
        cwd=DIR,
        capture_output=True,
    )
    print("Fichiers de contexte restaurés.")


C = "\033[36m"  # cyan
D = "\033[2m"  # dim
R = "\033[0m"  # reset


# --- Paramètres ---


def do_permission_mode():
    current = telebot_settings.get_permission_mode()
    items = []
    for mode, desc in telebot_settings.PERMISSION_MODES.items():
        check = " ✓" if mode == current else ""
        items.append(f"{mode:<16} — {desc}{check}")
    items.append("← Retour")
    print(f"  Mode actuel : {C}{current}{R}\n")
    menu = TerminalMenu(
        items,
        title="  Mode de permission",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    modes = list(telebot_settings.PERMISSION_MODES.keys())
    if choice is not None and isinstance(choice, int) and choice < len(modes):
        telebot_settings.set_permission_mode(modes[choice])
        print(f"\n  Mode changé : {C}{modes[choice]}{R}")


def do_permissions():
    while True:
        clear()
        print(f"\n  {C}Permissions auto-acceptées{R}\n")
        items = []
        presets = list(telebot_settings.PERMISSION_PRESETS.items())
        for name, rules in presets:
            enabled = telebot_settings.is_preset_enabled(rules)
            mark = "[x]" if enabled else "[ ]"
            items.append(f"{mark} {name}")
        bash_rules = telebot_settings.get_bash_rules()
        if bash_rules:
            patterns = ", ".join(r[5:-1] for r in bash_rules)  # Bash(x) → x
            items.append(f"Bash : {patterns}")
        else:
            items.append("Bash : (aucune règle)")
        items += ["+ Ajouter une règle Bash", "- Supprimer une règle", "← Retour"]
        menu = TerminalMenu(
            items,
            menu_cursor="❯ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )
        choice = menu.show()
        if choice is None or not isinstance(choice, int):
            return
        # Toggle preset
        if choice < len(presets):
            name, rules = presets[choice]
            enabled = telebot_settings.is_preset_enabled(rules)
            telebot_settings.toggle_preset(rules, not enabled)
            continue
        # Bash info line → skip
        bash_line_idx = len(presets)
        if choice == bash_line_idx:
            continue
        offset = bash_line_idx + 1
        if choice == offset:  # Ajouter Bash
            pattern = input("\n  Pattern Bash (ex: git *, npm run *) : ").strip()
            if pattern:
                telebot_settings.add_permission(f"Bash({pattern})")
                print(f"  Ajouté : Bash({pattern})")
            continue
        if choice == offset + 1:  # Supprimer
            removable = telebot_settings.get_user_allowed()
            if not removable:
                print("\n  Aucune permission à supprimer.")
                input(f"\n{D}  ⏎  Entrée pour continuer...{R}")
                continue
            rm_items = removable + ["← Annuler"]
            rm_menu = TerminalMenu(
                rm_items,
                title="  Supprimer quelle permission ?",
                menu_cursor="❯ ",
                menu_cursor_style=("fg_cyan", "bold"),
                menu_highlight_style=("fg_cyan", "bold"),
            )
            rm_choice = rm_menu.show()
            if (
                rm_choice is not None
                and isinstance(rm_choice, int)
                and rm_choice < len(removable)
            ):
                telebot_settings.remove_permission(removable[rm_choice])
                print(f"\n  Supprimé : {removable[rm_choice]}")
            continue
        return  # ← Retour


def do_show_settings():
    data = telebot_settings.load_settings()
    print(f"  {C}Configuration actuelle{R}")
    print(f"  Fichier : {telebot_settings.SETTINGS_FILE}\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def do_reset_settings():
    menu = TerminalMenu(
        ["Oui, réinitialiser", "Non, annuler"],
        title="  Remettre les paramètres par défaut ?",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice == 0:
        telebot_settings.reset_to_defaults()
        print("  Paramètres réinitialisés.")
    else:
        print("  Annulé.")


def do_settings():
    while True:
        clear()
        mode = telebot_settings.get_permission_mode()
        print(f"\n  {C}Paramètres{R}\n")
        items = [
            f"🔐 Mode de permission          ({mode})",
            "🛡  Permissions auto-acceptées",
            "📄 Voir la configuration",
            "🔑 Token / User ID (.env)",
            "♻  Réinitialiser les paramètres",
            "← Retour",
        ]
        menu = TerminalMenu(
            items,
            menu_cursor="❯ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )
        choice = menu.show()
        if choice is None or not isinstance(choice, int) or choice == 5:
            return
        clear()
        print(f"\n  {C}Paramètres{R}\n")
        if choice == 0:
            do_permission_mode()
        elif choice == 1:
            do_permissions()
            continue  # do_permissions gère son propre écran
        elif choice == 2:
            do_show_settings()
        elif choice == 3:
            do_config()
        elif choice == 4:
            do_reset_settings()
        input(f"\n{D}  ⏎  Entrée pour continuer...{R}")


# --- Menu interactif ---


def get_version():
    try:
        ret = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=DIR,
            capture_output=True,
            text=True,
            timeout=3,
        )
        return ret.stdout.strip() if ret.returncode == 0 else "?"
    except Exception:
        return "?"


BANNER = f"""\
{C}
  ████████╗███████╗██╗     ███████╗██████╗  ██████╗ ████████╗
  ╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
     ██║   █████╗  ██║     █████╗  ██████╔╝██║   ██║   ██║
     ██║   ██╔══╝  ██║     ██╔══╝  ██╔══██╗██║   ██║   ██║
     ██║   ███████╗███████╗███████╗██████╔╝╚██████╔╝   ██║
     ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝  ╚═════╝    ╚═╝
{D}              Telegram Bot — Claude Code{R}
"""

SEP = f"{D}  {'─' * 50}{R}"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def animate_banner():
    for line in BANNER.splitlines():
        print(line)
        time.sleep(0.04)


def interactive_menu():
    update_info = check_update()
    first_display = True

    while True:
        clear()
        bot_running = read_pid() is not None
        if first_display:
            animate_banner()
            first_display = False
        else:
            print(BANNER)
        print(f"{D}              {get_version()}{R}")
        print(f"\n  Bot: {bot_status_label()}  |  Tmux: {tmux_status_label()}")
        if update_info:
            print(f"  {D}{C}Mise à jour disponible : {update_info[1]}{R}")
        print(SEP)

        items = []
        actions = []

        if bot_running:
            items += ["■  Arrêter le bot", "↻  Redémarrer le bot"]
            actions += [do_stop, do_restart]
        else:
            items += ["▶  Démarrer le bot"]
            actions += [do_start]

        items += [
            "⏻  Tout couper (bot + session tmux)",
            "ℹ  Statut",
            "📋 Voir les logs",
            "⚙  Paramètres",
            "📦 Installer les dépendances",
            "🔄 Réinitialiser le contexte",
            "⬆  Mettre à jour",
            "🗑  Désinstaller",
            "✖  Quitter",
        ]
        actions += [
            do_kill_all,
            do_status,
            do_logs,
            do_settings,
            do_install,
            do_reset_context,
            do_update,
            do_uninstall,
            None,
        ]

        menu = TerminalMenu(
            items,
            menu_cursor="❯ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )

        choice = menu.show()

        if choice is None or not isinstance(choice, int) or actions[choice] is None:
            clear()
            print(f"{D}  Bye.{R}")
            break

        action = actions[choice]
        if action == do_settings:
            action()
            continue
        clear()
        print(BANNER)
        print(SEP + "\n")
        action()
        if action == do_update:
            update_info = check_update()
        input(f"\n{D}  ⏎  Entrée pour continuer...{R}")


# --- CLI direct ---


def main():
    parser = argparse.ArgumentParser(
        prog="bot",
        description="Gestion du bot Telegram Claude Code",
    )
    sub = parser.add_subparsers(dest="command")

    p_start = sub.add_parser("start", help="Démarrer le bot")
    p_start.add_argument("-f", "--foreground", action="store_true")

    sub.add_parser("stop", help="Arrêter le bot")
    sub.add_parser("restart", help="Redémarrer le bot")
    sub.add_parser("status", help="État du bot et des sessions")

    p_logs = sub.add_parser("logs", help="Voir les logs")
    p_logs.add_argument("-n", "--lines", type=int, default=30)

    sub.add_parser("kill", help="Tout couper (bot + session tmux)")
    sub.add_parser("config", help="Configurer token et user ID")
    sub.add_parser("install", help="Installer les dépendances")
    sub.add_parser("reset-context", help="Réinitialiser les fichiers de contexte")
    sub.add_parser("update", help="Mettre à jour depuis GitHub")
    sub.add_parser("settings", help="Gérer les paramètres Claude Code")
    sub.add_parser("uninstall", help="Désinstaller Telebot")

    args = parser.parse_args()

    if not args.command:
        interactive_menu()
        return

    cmds = {
        "start": lambda: do_start(args.foreground),
        "stop": do_stop,
        "restart": do_restart,
        "status": do_status,
        "logs": lambda: do_logs(args.lines),
        "kill": do_kill_all,
        "config": do_config,
        "install": do_install,
        "reset-context": do_reset_context,
        "update": do_update,
        "settings": do_settings,
        "uninstall": do_uninstall,
    }
    cmds[args.command]()


if __name__ == "__main__":
    main()
