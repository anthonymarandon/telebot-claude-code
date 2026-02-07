# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

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
