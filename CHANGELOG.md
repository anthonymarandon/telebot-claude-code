# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [1.8.8] - 2026-02-10

### Fixed
- AskUserQuestion multi-lots : le Enter en trop après un chiffre validait le lot suivant avec la valeur par défaut — détection de dialogue actif avant envoi
- Texte résumé après plan mode (Write/Edit) jamais envoyé — `in_tool` restait bloqué à `True` dans `extract_claude_text`
- Polling post-completion trop court (2s) pour détecter les dialogues tardifs — augmenté à 5s (8s avec tool pending)
- Capture tmux limitée à 500 lignes insuffisante pour les longues réponses plan mode — augmentée à 2000 lignes

## [1.8.7] - 2026-02-10

### Fixed
- Messages de configuration manquante proposent deux options (telebot config + Menu Paramètres) au lieu d'une seule

## [1.8.6] - 2026-02-10

### Added
- Badges shields.io dans le README (version, licence, Python, plateforme, auteur)
- Étape de vérification des badges README dans le skill de commit

## [1.8.5] - 2026-02-10

### Removed
- Saisie du token et user ID dans le script d'installation — la configuration se fait via le CLI qui se lance automatiquement après l'installation

## [1.8.4] - 2026-02-10

### Fixed
- Installation via `curl | bash` : les inputs (token, user ID) et le lancement du CLI lisent depuis `/dev/tty` au lieu du pipe stdin

## [1.8.3] - 2026-02-10

### Changed
- Le script d'installation lance automatiquement le CLI interactif à la fin, au lieu d'afficher la liste des commandes

## [1.8.2] - 2026-02-10

### Fixed
- Le bot refuse de démarrer si le token ou le user ID sont manquants dans le `.env`, avec message d'erreur précis

### Changed
- README réécrit : prérequis détaillés par plateforme, Node.js ajouté, section "Comment ça fonctionne"

## [1.8.1] - 2026-02-10

### Fixed
- Confirmation de désinstallation sans accent (`DESINSTALLER` au lieu de `DÉSINSTALLER`) — le É majuscule n'est pas accessible sur tous les claviers

## [1.8.0] - 2026-02-10

### Added
- Option "Désinstaller" dans le menu interactif du CLI (avant "Quitter") et en commande directe (`telebot uninstall`)
- Double confirmation de sécurité (menu + saisie du mot DÉSINSTALLER) avant suppression
- Nettoyage complet : arrêt du bot, fermeture tmux, suppression du wrapper `~/.local/bin/telebot` et du dossier `~/.telebot/`

## [1.7.8] - 2026-02-09

### Fixed
- Latence jusqu'à 30s entre les messages — `auto_read` lancé en tâche de fond au lieu de bloquer le handler, avec annulation automatique de la tâche précédente

## [1.7.7] - 2026-02-09

### Fixed
- Trust prompt au premier lancement ("Is this a project you trust?") non détecté par le bot — ajout de `auto_read` après `/open`

## [1.7.6] - 2026-02-09

### Fixed
- Script d'installation crashait si le venv existant était cassé (pip absent après mise à jour Python système) — recréation automatique du venv

## [1.7.5] - 2026-02-08

### Changed
- Menu des commandes Telegram réduit à `/open`, `/close` et `/help` (plus aéré)
- Commande `/help` ajoutée, liste toutes les commandes par catégorie (Session / Interaction)

## [1.7.4] - 2026-02-08

### Fixed
- Mode `bypassPermissions` manquant dans le menu des paramètres de permission

## [1.7.3] - 2026-02-08

### Fixed
- Détection des dialogues de permission élargie à tous les outils (EnterPlanMode, Glob, Read, MCP, etc.) au lieu de 4 seulement (Write, Edit, Bash, NotebookEdit)
- Outils sans arguments (EnterPlanMode, ExitPlanMode) non reconnus comme tool headers

## [1.7.2] - 2026-02-08

### Fixed
- Configuration Token/User ID affiche désormais les valeurs actuelles (token masqué) au lieu de les écraser systématiquement

## [1.7.1] - 2026-02-08

### Fixed
- Duplication de lignes dans le menu des permissions (codes ANSI dans les items TerminalMenu causaient des artefacts de rendu)

## [1.7.0] - 2026-02-08

### Added
- Menu Paramètres dans le CLI avec sous-menu dédié (mode de permission, permissions auto-acceptées, visualisation config, réinitialisation)
- Module `settings.py` pour gérer `.claude/settings.local.json` (permissions allow/deny, presets, règles Bash custom)
- Toggle de presets de permissions (édition fichiers, accès web, lecture) et ajout/suppression de règles Bash
- Le bot passe les flags `--permission-mode` au lancement de la session Claude via tmux
- Commande CLI directe `bot settings` pour accéder aux paramètres

### Changed
- Entrée "Configurer (token / user ID)" remplacée par "Paramètres" dans le menu principal (token/user ID déplacé dans le sous-menu)

## [1.6.1] - 2026-02-08

### Fixed
- Le CLI restait sur l'ancienne version après une mise à jour (relancement automatique via `os.execv`)

## [1.6.0] - 2026-02-08

### Fixed
- Session tmux démarrait dans `~` au lieu du répertoire d'installation (contexte `.claude/` non chargé)
- Processus bot héritait du cwd de l'appelant au lieu de `~/.telebot/`

### Added
- Préservation des personnalisations `.claude/` lors des mises à jour (choix garder/écraser)
- Commande `reset-context` pour restaurer les fichiers de contexte par défaut (menu + CLI)

## [1.5.4] - 2026-02-07

### Added
- Animation d'apparition du banner ligne par ligne au premier lancement du menu interactif

## [1.5.3] - 2026-02-07

### Changed
- Skill commit : push automatique du tag sur le remote après création
- Skill commit : clarification des règles (push tag auto, push commits sur demande)

## [1.5.2] - 2026-02-07

### Changed
- Confirmation de mise à jour remplacée par un menu interactif (flèches directionnelles) au lieu de `[O/n]`

## [1.5.1] - 2026-02-07

### Added
- Affichage dynamique du numéro de version dans le menu interactif du CLI (via `git describe --tags`)

## [1.5.0] - 2026-02-07

### Added
- Règle de priorité dans CLAUDE.md : Claude lit et priorise le contexte du projet cible avant d'appliquer les règles par défaut
- Skill `/analyze` : analyse un projet (structure, langage, frameworks, conventions, contexte .claude/)
- Skill `/init-context` : initialise un `.claude/` adapté dans n'importe quel projet avec CLAUDE.md et skills pré-remplis

### Changed
- CLAUDE.md rendu polyvalent et générique (plus spécifique à Python, s'adapte au projet cible)
- Le `.claude/` est désormais conservé à l'installation (plus supprimé par install.sh)

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
