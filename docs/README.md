# Parcours Cours - Index

Ce dossier contient le parcours complet du cours, module par module.

## Etape 0 obligatoire - Environnement virtuel

Depuis la racine du projet:

```bash
python -m venv env
```

Activation Windows (PowerShell):

```powershell
env\Scripts\Activate.ps1
```

Activation macOS/Linux:

```bash
source env/bin/activate
```

Installer les dependances:

```bash
pip install -r requirements.txt
```

## Ordre recommande

1. `docs/01-crud-drf.md`
2. `docs/02-securite-drf.md`
3. `docs/03-auth-jwt-permissions.md`
4. `docs/04-websockets-realtime.md`
5. `docs/05-admin-wysiwyg-mini-cms.md`
6. `docs/06-bonus-qualite-tests-deploiement.md`

## Version enseignant

- Index: `docs/teacher/README.md`
- Fiches animees avec timing, questions et quiz par module

## Format commun

Chaque fichier suit la meme structure:

- Objectifs
- Prerequis
- Steps numerotes
- Tests de validation
- Erreurs frequentes
- Exercice de fin
- Checklist de fin de module
