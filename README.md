# Telebot

Pilotez [Claude Code](https://docs.anthropic.com/en/docs/claude-code) à distance depuis Telegram.

Envoyez des prompts, recevez les réponses en streaming, approuvez les dialogues de permission — le tout depuis votre téléphone.

## Prérequis

### Outils requis

| Outil | Rôle | Installation |
|---|---|---|
| [Python 3.10+](https://www.python.org/) | Runtime du bot et du CLI | Voir ci-dessous |
| [tmux](https://github.com/tmux/tmux) | Pilotage de Claude Code via terminal | Voir ci-dessous |
| [git](https://git-scm.com/) | Installation et mises à jour | Voir ci-dessous |
| [Node.js](https://nodejs.org/) | Nécessaire pour installer Claude Code | Voir ci-dessous |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | L'outil piloté à distance | `npm install -g @anthropic-ai/claude-code` |

### Par plateforme

| | macOS | Linux | Windows |
|---|---|---|---|
| Python | `brew install python` | `sudo apt install python3` | via WSL |
| tmux | `brew install tmux` | `sudo apt install tmux` | via WSL |
| git | `brew install git` | `sudo apt install git` | via WSL |
| Node.js | `brew install node` | `sudo apt install nodejs npm` | via WSL |

> **Windows** : Telebot nécessite un environnement POSIX. Utilisez [WSL](https://learn.microsoft.com/windows/wsl/install) (Windows Subsystem for Linux), puis suivez les instructions Linux.

### Comptes Telegram

Avant l'installation, munissez-vous de :
- Un **token de bot** obtenu via [@BotFather](https://t.me/BotFather)
- Votre **User ID** obtenu via [@userinfobot](https://t.me/userinfobot)

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/anthonymarandon/telebot-claude-code/main/install.sh | bash
```

Le script clone le projet dans `~/.telebot/`, crée un environnement virtuel, installe les dépendances et ajoute la commande `telebot` dans `~/.local/bin/`.

## Utilisation

### CLI

```bash
telebot              # Menu interactif
telebot start        # Démarrer le bot
telebot stop         # Arrêter le bot
telebot status       # Voir l'état
telebot logs         # Voir les logs
telebot config       # Reconfigurer token / user ID
telebot settings     # Paramètres (permissions, mode)
telebot update       # Mettre à jour
telebot uninstall    # Désinstaller
```

### Telegram

Une fois le bot démarré, depuis Telegram :

| Commande | Action |
|---|---|
| `/open` | Ouvre une session Claude Code |
| `/close` | Ferme la session |
| `/esc` | Annuler (Escape) |
| `/pick N` | Choisir l'option N dans un dialogue |
| *texte libre* | Envoyé directement à Claude Code |

## Comment ça fonctionne

```
Telegram  -->  Bot Python  -->  tmux  -->  Claude Code
   <--  streaming  <--  capture-pane  <--
```

1. Le bot Python tourne en arrière-plan et écoute vos messages Telegram
2. Chaque message est envoyé dans une session tmux où Claude Code tourne
3. Le bot capture le terminal en continu et vous renvoie les réponses en streaming
4. Les dialogues de permission (Write, Edit, Bash...) sont détectés et transmis pour approbation

## Licence

MIT
