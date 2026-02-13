# Module 6 Enseignant - Qualite, tests, deploiement

## Duree totale

- 90 minutes

## Plan minute par minute

1. 0-15 min: DRF avance (pagination/filter/search/ordering)
2. 15-30 min: ressources imbriquees (comments)
3. 30-50 min: tests API pytest
4. 50-65 min: qualite outillee (ruff/black/pre-commit)
5. 65-75 min: Conventional Commits
6. 75-83 min: CI GitHub Actions (controle des commits)
7. 83-88 min: docker compose run local
8. 88-90 min: quiz final

## Script de demo

1. Installer:

```bash
pip install django-filter pytest pytest-django ruff black pre-commit commitizen
```

2. Ajouter config DRF avancee dans `settings.py`.
3. Ajouter une ressource `Comment`.
4. Ajouter test minimal `blog/tests/test_posts_api.py`.
5. Lancer:

```bash
pytest
```

6. Ajouter `.pre-commit-config.yaml` puis:

```bash
pre-commit install
```

7. Introduire Conventional Commits (`https://www.conventionalcommits.org/en/v1.0.0/`):

```text
feat(auth): add register endpoint
fix(posts): enforce owner delete permission
docs(module6): explain conventional commits
```

7.bis Ressources bonus a montrer rapidement (optionnel):

- `https://gist.github.com/parmentf/359667bf23e08a1bd8241fbf47ecdef0`
- `https://conventional-emoji-commits.site/quick-summary/summary`
- `https://gitmoji.dev/`

Message a faire passer:

- La base reste `type(scope): description`.
- Les emojis sont un choix d equipe, pas une obligation.

8. Ajouter `.cz.toml`, puis installer hook commit message:

```bash
pre-commit install --hook-type commit-msg
```

9. Verifier un message:

```bash
cz check --message "feat(api): add pagination"
```

10. Ajouter workflow `.github/workflows/commit-message-check.yml` et expliquer:

- `fetch-depth: 0` pour lire l historique complet.
- `cz check --rev-range` pour verifier plusieurs commits.
- verification sur `push` et `pull_request`.

11. Montrer `Dockerfile` + `docker-compose.yml`.
12. Lancer:

```bash
docker compose up --build
```

## Questions a poser

1. Pourquoi tester les permissions avant deploiement ?
2. Pourquoi separer settings dev/prod ?
3. Pourquoi automatiser lint/format ?
4. Pourquoi imposer Conventional Commits en equipe ?
5. Pourquoi verifier les commits aussi en CI, pas seulement en local ?
6. Quel est l interet pedagogique de Docker en cours ?
7. Dans quel cas utiliser (ou ne pas utiliser) une convention emoji ?

## Mini quiz (5 min)

1. `pytest` remplace totalement les tests d integration manuels. Vrai/Faux ?
2. `pre-commit` peut bloquer un commit non conforme. Vrai/Faux ?
3. `feat(auth): add login` respecte Conventional Commits. Vrai/Faux ?
4. Un workflow GitHub Actions peut bloquer une PR avec des commits non conformes. Vrai/Faux ?
5. Docker garantit qu il n y aura aucun bug en production. Vrai/Faux ?

Corrige:

1. Faux
2. Vrai
3. Vrai
4. Vrai
5. Faux

## Critere de reussite

- Les etudiants savent ajouter un test API simple.
- Les etudiants savent mettre en place une base qualite.
- Les etudiants savent ecrire des commits au format Conventional Commits.
- Les etudiants savent configurer un workflow CI de verification de commits.
- Les etudiants savent lancer un run local conteneurise.
