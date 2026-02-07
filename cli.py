#!/usr/bin/env python3
"""CLI interactif de gestion du bot Telegram Claude Code."""

import argparse
import os
import signal
import subprocess
import sys

from simple_term_menu import TerminalMenu

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
    return "\033[32m● active\033[0m" if ret.returncode == 0 else "\033[31m○ inactive\033[0m"


# --- Actions ---

def do_start(foreground=False):
    if read_pid():
        print("Le bot tourne déjà.")
        return

    if not os.path.exists(ENV_FILE):
        print("Fichier .env manquant. Lance : bot config")
        return

    if foreground:
        print("Démarrage en avant-plan (Ctrl+C pour arrêter)...")
        os.execv(get_python(), [get_python(), BOT_SCRIPT])
    else:
        log = open(LOG_FILE, "a")
        proc = subprocess.Popen(
            [get_python(), BOT_SCRIPT],
            stdout=log, stderr=log,
            start_new_session=True,
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


def do_config():
    print("Configuration du bot\n")
    token = input("Token Telegram (BotFather) : ").strip()
    user_id = input("Ton User ID Telegram      : ").strip()
    with open(ENV_FILE, "w") as f:
        f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
        f.write(f"ALLOWED_USER_ID={user_id}\n")
    print("\n.env sauvegardé.")


def do_install():
    print("Installation des dépendances...")
    if not os.path.exists(os.path.join(DIR, "venv")):
        subprocess.run([sys.executable, "-m", "venv", os.path.join(DIR, "venv")], check=True)
        print("Environnement virtuel créé.")
    subprocess.run(
        [get_python(), "-m", "pip", "install", "-q", "-r", os.path.join(DIR, "requirements.txt")],
        check=True,
    )
    print("Dépendances installées.")


# --- Menu interactif ---

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def interactive_menu():
    while True:
        clear()
        print(f"\n  Bot: {bot_status_label()}  |  Tmux: {tmux_status_label()}\n")

        items = [
            "▶  Démarrer le bot",
            "■  Arrêter le bot",
            "↻  Redémarrer le bot",
            "ℹ  Statut",
            "📋 Voir les logs",
            "⚙  Configurer (token / user ID)",
            "📦 Installer les dépendances",
            "✖  Quitter",
        ]

        menu = TerminalMenu(
            items,
            title="Bot Telegram Claude Code",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )

        choice = menu.show()

        if choice is None or choice == 7:
            clear()
            print("Bye.")
            break

        clear()
        actions = [do_start, do_stop, do_restart, do_status, do_logs, do_config, do_install]
        actions[choice]()
        input("\n⏎  Entrée pour continuer...")


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

    sub.add_parser("config", help="Configurer token et user ID")
    sub.add_parser("install", help="Installer les dépendances")

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
        "config": do_config,
        "install": do_install,
    }
    cmds[args.command]()


if __name__ == "__main__":
    main()
