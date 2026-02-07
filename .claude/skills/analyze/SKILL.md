# Analyse de projet

Tu es un agent d'analyse. Quand l'utilisateur invoque ce skill, analyse le projet courant pour en comprendre le contexte complet.

## Étape 1 — Détecter le contexte existant

- Vérifie si un `.claude/CLAUDE.md` existe dans le répertoire courant
- Si oui, lis-le intégralement ainsi que tous les skills (`.claude/skills/*/SKILL.md`)
- Présente un résumé du contexte trouvé à l'utilisateur

## Étape 2 — Analyser la structure

- Liste l'arborescence du projet (2 niveaux max)
- Identifie les fichiers clés : `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `Makefile`, `Dockerfile`, `pyproject.toml`, etc.
- Lis les fichiers de configuration trouvés pour en extraire les métadonnées (nom, version, dépendances)

## Étape 3 — Identifier le langage et les frameworks

À partir des fichiers détectés, détermine :
- Le(s) langage(s) principal(aux)
- Les frameworks et bibliothèques utilisés
- Le système de build / gestionnaire de paquets
- Les outils de test s'ils sont configurés

## Étape 4 — Analyser les conventions

- Lis les 10 derniers commits (`git log --oneline -10`) pour comprendre le style de commit
- Vérifie la présence de linters, formatters, CI/CD (`.eslintrc`, `.prettierrc`, `.github/workflows/`, etc.)
- Identifie les conventions de nommage dans le code (camelCase, snake_case, etc.)

## Étape 5 — Présenter le résumé

Présente à l'utilisateur un résumé structuré :

```
Projet : [nom]
Langage : [langage(s)]
Framework : [framework(s)]
Build : [outil]
Tests : [outil]
Conventions de commit : [format détecté]
Contexte .claude/ : [présent / absent]
```

Suivi de recommandations :
- Si pas de `.claude/`, proposer `/init-context` pour en créer un
- Si le contexte existe, signaler les éventuelles incohérences

## Règles

- Ne modifier aucun fichier — ce skill est en lecture seule
- Toujours vérifier le `.claude/` du projet avant toute analyse
- Adapter le vocabulaire technique au langage du projet
