# Telebot

Pilotez [Claude Code](https://docs.anthropic.com/en/docs/claude-code) à distance depuis Telegram. Envoyez des prompts, recevez les réponses en streaming, approuvez les dialogues de permission — le tout depuis votre téléphone.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/anthonymarandon/telebot-claude-code/main/install.sh | bash
```

Le script installe tout dans `~/.telebot/` et crée la commande `telebot`.

## Prérequis

|  | macOS | Linux | Windows (WSL) |
|---|---|---|---|
| **Python 3.10+** | `brew install python` | `sudo apt install python3` | `sudo apt install python3` |
| **git** | `brew install git` | `sudo apt install git` | `sudo apt install git` |
| **tmux** | `brew install tmux` | `sudo apt install tmux` | `sudo apt install tmux` |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | idem | idem |

> Sur Windows, utilisez [WSL](https://learn.microsoft.com/windows/wsl/install) (Windows Subsystem for Linux). Telebot ne supporte pas PowerShell/CMD nativement.

Vous aurez aussi besoin de :
- Un **token Telegram** obtenu via [@BotFather](https://t.me/BotFather)
- Votre **User ID Telegram** obtenu via [@userinfobot](https://t.me/userinfobot)

## Utilisation

```bash
telebot              # Menu interactif
telebot start        # Démarrer le bot
telebot stop         # Arrêter le bot
telebot status       # Voir l'état
telebot logs         # Voir les logs
telebot config       # Reconfigurer token / user ID
telebot update       # Mettre à jour
```

## Commandes Telegram

Une fois le bot démarré, depuis Telegram :

| Commande | Description |
|---|---|
| `/open` | Ouvre une session Claude Code (tmux) |
| `/close` | Ferme la session |
| `/esc` | Envoie Escape (annuler un dialogue) |
| `/pick N` | Sélectionne l'option N dans un dialogue |
| *texte libre* | Envoyé directement à Claude Code |

## Mise à jour

```bash
telebot update
```

Le menu interactif vous notifie automatiquement quand une nouvelle version est disponible.

## Licence

MIT
