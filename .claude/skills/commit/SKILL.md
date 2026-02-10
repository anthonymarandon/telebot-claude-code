---
Name: commit
Description: Analyse les changements, détermine le type de version (patch/minor/major), met à jour le CHANGELOG.md et crée un commit structuré avec le bon tag de version.
---

# Workflow de commit

Tu es un agent de gestion de versions. Quand l'utilisateur invoque ce skill, exécute les étapes suivantes dans l'ordre.

## Étape 1 — Analyser l'historique

- Lis les 10 derniers commits avec `git log --oneline -10` pour comprendre le style et le contexte.
- Lis le fichier `CHANGELOG.md` à la racine du projet pour identifier la version actuelle.
- Si le fichier n'existe pas ou si aucune version n'est présente, la version de départ est `1.0.0`.

## Étape 2 — Analyser les changements en cours

- Exécute `git status` pour voir les fichiers modifiés, ajoutés ou supprimés.
- Exécute `git diff` (staged et unstaged) pour comprendre le contenu exact des changements.
- Résume en une phrase ce qui a changé et pourquoi.

## Étape 3 — Déterminer le type de version

Évalue les changements selon ces critères :

| Type | Incrémentation | Critères |
|---|---|---|
| **Patch** | `x.x.+1` | Correction de bug, typo, petit ajustement, refactoring sans impact fonctionnel |
| **Minor** | `x.+1.0` | Nouvelle fonctionnalité, amélioration notable, ajout de commande/option |
| **Major** | `+1.0.0` | Changement cassant, refonte d'architecture, suppression de fonctionnalité, migration |

Présente ton analyse à l'utilisateur avec la version proposée et attends sa validation avant de continuer.

## Étape 4 — Vérifier les badges du README.md

Vérifie que les badges en haut de `README.md` sont cohérents avec l'état actuel du projet :

| Badge | Source | Quand mettre à jour |
|---|---|---|
| **Version** | Dynamique (shields.io/github) | Jamais — se met à jour automatiquement via le tag git |
| **License** | Statique | Si la licence change |
| **Python** | Statique | Si la version Python minimale change |
| **Platform** | Statique | Si les plateformes supportées changent |
| **Author** | Statique | Si l'auteur change |

Si un changement dans le diff impacte l'un de ces éléments (ex: version Python minimale dans `requirements.txt`, licence, plateformes supportées), mets à jour le badge correspondant dans `README.md` et inclus le fichier dans le commit.

## Étape 5 — Mettre à jour le CHANGELOG.md

Ajoute une nouvelle entrée **en haut** de la section des versions dans `CHANGELOG.md` avec ce format :

```
## [X.Y.Z] - YYYY-MM-DD

### Type (Added / Changed / Fixed / Removed)
- Description concise du changement
```

Catégories possibles :
- **Added** : nouvelle fonctionnalité
- **Changed** : modification d'une fonctionnalité existante
- **Fixed** : correction de bug
- **Removed** : suppression de fonctionnalité

## Étape 6 — Créer le commit

- Stage les fichiers pertinents (y compris `CHANGELOG.md`). Ne jamais utiliser `git add -A` ou `git add .`. Ajouter les fichiers par nom.
- Ne jamais inclure de fichiers sensibles (`.env`, credentials, etc.).
- Crée le commit avec ce format de message :

```
[X.Y.Z] Type: description courte

Description détaillée si nécessaire.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

Où **Type** est un des suivants : `fix`, `feat`, `refactor`, `docs`, `chore`, `breaking`.

- Vérifie avec `git status` que le commit a réussi.

## Étape 7 — Créer le tag git

- Crée un tag git annoté : `git tag -a vX.Y.Z -m "vX.Y.Z"`
- Pousse le tag sur le remote : `git push origin vX.Y.Z`

## Règles

- Ne jamais committer sans avoir mis à jour le CHANGELOG.md.
- Ne jamais pousser les **commits** sur le remote sans demande explicite de l'utilisateur.
- Le push du **tag** est automatique (fait partie de l'étape 6).
- Ne jamais amender un commit existant sauf demande explicite.
- Toujours attendre la validation de l'utilisateur sur le type de version avant de committer.
