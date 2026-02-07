# Claude — Référentiel Telebot

Ce fichier est l'orchestrateur central de Telebot. Il fournit des règles par défaut et des skills polyvalents utilisables sur n'importe quel projet.

## Règle de priorité — IMPORTANT

Quand tu travailles sur un projet externe (après un `cd` vers un autre dossier) :

1. **Lis immédiatement** le `.claude/CLAUDE.md` du projet cible s'il existe
2. **Lis les skills** du projet cible (`.claude/skills/`)
3. Les règles et conventions du projet cible **priment** sur celles de ce fichier
4. Si le projet cible n'a pas de `.claude/`, applique les règles par défaut ci-dessous

Cette lecture est **obligatoire** avant toute action sur un projet externe. Ne jamais supposer les conventions d'un projet sans avoir vérifié son contexte.

## Projet Telebot

- **Nom** : Telebot — Telegram Bot Claude Code
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
        ├── commit/
        │   └── SKILL.md
        ├── auto-update/
        │   └── SKILL.md
        ├── analyze/
        │   └── SKILL.md
        └── init-context/
            └── SKILL.md
```

## Skills

| Skill | Invocation | Description |
|---|---|---|
| [commit](.claude/skills/commit/SKILL.md) | `/commit` | Analyse les changements, détermine la version (patch/minor/major), met à jour le CHANGELOG et commit avec tag |
| [auto-update](.claude/skills/auto-update/SKILL.md) | `/auto-update` | Met à jour les consignes, règles et skills quand un problème est détecté ou une amélioration identifiée |
| [analyze](.claude/skills/analyze/SKILL.md) | `/analyze` | Analyse un projet pour en comprendre la structure, le langage, les conventions et le contexte |
| [init-context](.claude/skills/init-context/SKILL.md) | `/init-context` | Initialise un `.claude/` dans le projet courant avec CLAUDE.md et skills adaptés |

## Règles par défaut

Ces règles s'appliquent quand le projet cible n'a pas ses propres conventions.

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
- Pas de sur-ingénierie
- S'adapter au langage et aux conventions du projet cible
- Cross-platform quand possible

### Sécurité
- Aucun secret dans le code source
- `.env` et fichiers sensibles exclus du versioning
