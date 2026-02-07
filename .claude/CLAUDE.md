# Claude — Référentiel Projet

Ce fichier est l'orchestrateur central du projet. Il référence toutes les règles, commandes et skills disponibles.

## Projet

- **Nom** : Telegram Bot Claude Code
- **Langage** : Python
- **But** : Piloter Claude Code à distance via Telegram + tmux
- **Version actuelle** : voir `CHANGELOG.md`

## Structure

```
.
├── bot.py              # Bot Telegram (commandes /open, /send, /read, etc.)
├── cli.py              # CLI interactif (menu flèches + commandes directes)
├── requirements.txt    # Dépendances Python
├── CHANGELOG.md        # Historique des versions
├── .env                # Configuration (token, user ID) — non versionné
├── .gitignore
└── .claude/
    ├── CLAUDE.md       # Ce fichier — orchestrateur central
    └── skills/
        ├── commit.md/
        │   └── SKILL.md
        └── auto-update.md/
            └── SKILL.md
```

## Skills

| Skill | Invocation | Description |
|---|---|---|
| [commit](.claude/skills/commit.md/SKILL.md) | `/commit` | Analyse les changements, détermine la version (patch/minor/major), met à jour le CHANGELOG et commit avec tag |
| [auto-update](.claude/skills/auto-update.md/SKILL.md) | `/auto-update` | Met à jour les consignes, règles et skills quand un problème est détecté ou une amélioration identifiée |

## Règles globales

### Versioning
- Format : **semver** `MAJOR.MINOR.PATCH`
- Chaque commit est taggé `vX.Y.Z`
- Le `CHANGELOG.md` est **toujours** mis à jour avant un commit

### Git
- Ne jamais push sans demande explicite
- Ne jamais amend sauf demande explicite
- Ne jamais `git add -A` ou `git add .` — toujours ajouter les fichiers par nom
- Ne jamais committer `.env`, credentials ou fichiers sensibles
- Format de commit : `[X.Y.Z] type: description`
- Types : `fix`, `feat`, `refactor`, `docs`, `chore`, `breaking`

### Code
- Garder le code minimal et lisible
- Python uniquement, pas de sur-ingénierie
- Les dépendances sont dans le venv, jamais en global
- Cross-platform : macOS, Linux, Windows

### Sécurité
- Authentification par `ALLOWED_USER_ID` sur le bot Telegram
- Aucun secret dans le code source
- `.env` exclu du versioning
