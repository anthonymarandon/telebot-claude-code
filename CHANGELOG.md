# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [1.4.3] - 2026-02-07

### Fixed
- Crash de `install.sh` quand `~/.telebot/` existe sans être un repo git (vérification `.git/` avant `git pull`)

## [1.4.2] - 2026-02-07

### Fixed
- URL du repo GitHub corrigée dans `install.sh` et `README.md` (`telebot-claude-code` au lieu de `telegram-bot`)

## [1.4.1] - 2026-02-07

### Added
- README.md avec instructions d'installation, prérequis (macOS/Linux/Windows WSL), commandes CLI et Telegram

## [1.4.0] - 2026-02-07

### Added
- Script d'installation one-liner `install.sh` (clone dans `~/.telebot/`, crée venv, installe deps, crée commande `telebot`)
- Commande `telebot update` pour mettre à jour depuis GitHub (git pull + réinstall deps + restart bot si actif)
- Vérification automatique des mises à jour au lancement du menu interactif (notification discrète)
- Fonctions utilitaires `parse_version()` et `check_update()` pour comparer les tags git locaux/distants

## [1.3.0] - 2026-02-07

### Fixed
- Dialogues de permission (Write/Edit/Bash) non envoyés sur Telegram (polling adaptatif + `_has_pending_tool`)
- Crash "Message is too long" sur les dialogues avec preview de fichier (utilisation de `send_chunks`)
- Réponses tronquées quand Claude utilise des séparateurs `────` dans son contenu (`_is_separator` colonne 0 uniquement)
- Crash `TimedOut` sur `send_action` qui cassait la boucle de surveillance

### Added
- Indicateur "typing" sur Telegram pendant que Claude travaille
- Fonction `_has_pending_tool()` pour détecter les outils en attente de confirmation

### Changed
- Boucle `auto_read` infinie avec idle timeout (30s d'inactivité) au lieu du timeout fixe 120s

## [1.2.0] - 2026-02-07

### Added
- Streaming filtré : envoi du texte de Claude au fil de l'eau, sans tool output ni blocs de code
- Fonction `extract_claude_text` avec machine à états pour séparer texte et outils

### Changed
- `/open` n'appelle plus `auto_read` (supprime le faux message "aucun changement" au démarrage)
- Corrections Pylance : guards de typage sur `update.message`, `update.effective_user`, `menu.show()`

## [1.1.0] - 2025-02-07

### Added
- Moteur de parsing terminal complet (extraction réponses, dialogues, détection spinner)
- Auto-read avec streaming : les réponses de Claude arrivent en temps réel
- Commandes `/esc` (Escape) et `/pick N` (sélection menu)
- Commande `kill` dans le CLI (coupe bot + session tmux)
- Bannière ASCII et menu contextuel dynamique dans le CLI

### Changed
- Messages texte libres envoyés directement à Claude avec auto-read de la réponse
- `/start` simplifié (fait office de help)

### Removed
- Commandes `/send`, `/read`, `/status`, `/cmd`, `/help`, `/enter`, `/up`, `/down`, `/tab`

## [1.0.0] - 2025-02-07

### Added
- Bot Telegram pour piloter Claude Code via tmux (bot.py)
- CLI interactif avec menu navigable aux flèches (cli.py)
- Commandes Telegram : /open, /send, /read, /close, /status, /cmd
- Commandes CLI : start, stop, restart, status, logs, config, install
- Authentification par user ID Telegram
- Envoi de messages texte libres directement à Claude Code
