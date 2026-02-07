# Initialisation de contexte projet

Tu es un agent d'initialisation. Quand l'utilisateur invoque ce skill, crée un `.claude/` adapté dans le projet courant.

## Étape 1 — Vérifier l'état actuel

- Vérifie si un `.claude/` existe déjà dans le répertoire courant
- Si oui, demande à l'utilisateur s'il veut le compléter ou le réinitialiser
- Si non, continue avec la création

## Étape 2 — Analyser le projet

Avant de créer quoi que ce soit, analyse le projet (comme `/analyze`) :
- Langage(s), frameworks, outils de build
- Conventions de commit (git log)
- Structure des dossiers
- Linters, formatters, CI/CD existants

## Étape 3 — Créer le CLAUDE.md

Crée `.claude/CLAUDE.md` avec les sections suivantes, pré-remplies à partir de l'analyse :

```markdown
# Claude — Référentiel Projet

## Projet
- **Nom** : [détecté depuis package.json, pyproject.toml, etc.]
- **Langage** : [détecté]
- **Framework** : [détecté]
- **But** : [demander à l'utilisateur]

## Structure
[arborescence simplifiée du projet]

## Skills
[table des skills installés]

## Règles
### Git
[conventions détectées depuis l'historique de commits]

### Code
[conventions détectées : nommage, formatage, etc.]

### Tests
[commande de test si détectée]
```

Présente le contenu proposé à l'utilisateur **avant** de l'écrire.

## Étape 4 — Installer les skills

Crée les dossiers de skills dans `.claude/skills/` :

- **`commit/SKILL.md`** — Copier le workflow de commit standard (semver, changelog, tag). Adapter le format de commit si le projet a ses propres conventions.
- **`auto-update/SKILL.md`** — Copier le workflow d'auto-évolution du référentiel.

Si d'autres skills sont pertinents (ex: un skill de test, de déploiement), les proposer à l'utilisateur.

## Étape 5 — Confirmer

- Afficher la liste des fichiers créés
- Proposer d'ajouter `.claude/settings.local.json` au `.gitignore` (il contient des permissions locales)
- Rappeler que le CLAUDE.md peut être enrichi au fil du temps via `/auto-update`

## Règles

- Toujours demander confirmation avant d'écrire les fichiers
- Ne jamais écraser un `.claude/` existant sans accord explicite
- Adapter le contenu au langage et aux conventions du projet, pas de copier-coller aveugle
- Le CLAUDE.md généré doit être concis et actionnable, pas un roman
