---
Name: auto-update
Description: Met à jour les consignes, règles et skills du projet lorsqu'un problème est détecté, une erreur corrigée ou une amélioration identifiée. Permet au référentiel d'évoluer de manière autonome.
---

# Workflow d'auto-update

Tu es un agent d'évolution du référentiel projet. Ce skill est déclenché quand une règle, un skill ou une convention doit être ajoutée, corrigée ou améliorée.

## Déclencheurs

Ce skill doit être invoqué dans les cas suivants :
- Une erreur récurrente a été identifiée et une règle doit la prévenir
- Un nouveau skill a été créé et doit être référencé
- Une convention existante s'avère inadaptée ou incomplète
- La structure du projet a changé (nouveau fichier, nouvelle dépendance)
- Un retour utilisateur nécessite une mise à jour des consignes

## Étape 1 — Diagnostic

- Identifie le problème ou l'amélioration à apporter.
- Lis le `CLAUDE.md` pour comprendre l'état actuel des règles et références.
- Lis les SKILL.md concernés si la mise à jour touche un skill.
- Résume en une phrase ce qui doit changer et pourquoi.

## Étape 2 — Proposition

Présente à l'utilisateur :
- **Ce qui change** : la règle, le skill ou la convention concernée
- **Pourquoi** : le problème constaté ou l'amélioration visée
- **Comment** : les fichiers qui seront modifiés et le contenu prévu

Attends la validation de l'utilisateur avant de continuer.

## Étape 3 — Appliquer les modifications

Selon le cas, mets à jour un ou plusieurs de ces fichiers :

### CLAUDE.md (orchestrateur)
- Mettre à jour la **table des skills** si un skill est ajouté, renommé ou supprimé
- Mettre à jour la **structure** si l'arborescence du projet a changé
- Mettre à jour les **règles globales** si une convention évolue

### SKILL.md (skill concerné)
- Corriger ou compléter les étapes du workflow
- Ajouter des règles ou des cas limites
- Mettre à jour le frontmatter (Name, Description) si nécessaire

### Nouveau skill
- Créer le dossier `.claude/skills/<nom>.md/SKILL.md`
- Respecter le format : frontmatter (Name, Description) + workflow par étapes
- Référencer le nouveau skill dans la table des skills du `CLAUDE.md`

## Étape 4 — Vérification

- Relis chaque fichier modifié pour vérifier la cohérence.
- Vérifie que le `CLAUDE.md` est synchronisé avec l'état réel du projet.
- Vérifie qu'aucune référence n'est cassée (liens vers des skills supprimés, structure obsolète).

## Étape 5 — Commit

- Invoque le skill `/commit` pour versionner les changements.

## Règles

- Ne jamais supprimer une règle ou un skill sans validation explicite de l'utilisateur.
- Ne jamais modifier le comportement d'un skill sans le signaler.
- Toujours garder le `CLAUDE.md` comme source de vérité synchronisée.
- Privilégier l'ajout et la correction plutôt que la réécriture complète.
