# Module 6 - Bonus qualite, tests et deploiement

## Objectifs

- Ajouter pagination, filtres, search, ordering
- Introduire tests API et tests de permissions
- Structurer le projet pour dev/prod
- Faire un deploiement local simple avec Docker
- Standardiser les messages Git avec Conventional Commits
- Automatiser le controle des commits en CI

## Prerequis

- Modules precedents termines
- Base API stable

## Step by Step

### Step 0 - Activer l environnement virtuel

Windows (PowerShell):

```powershell
env\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source env/bin/activate
```

Installer les dependances:

```bash
pip install -r requirements.txt
```

### Step 1 - DRF avance (pagination, filtres, search, ordering)

Installer:

```bash
pip install django-filter
```

Fichier: `newspaper/settings.py`

```python
INSTALLED_APPS = [
    # ...
    "django_filters",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

Fichier: `blog/views.py`

```python
from rest_framework.viewsets import ModelViewSet
from .models import Post
from .serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    filterset_fields = ["status"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at", "title"]
```

### Step 2 - Ressource imbriquee: commentaires

Fichier a creer: `blog/comment_models.py` (ou dans `models.py`)

```python
from django.db import models
from .models import Post


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author_name = models.CharField(max_length=120)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author_name} - {self.post_id}"
```

Fichier a creer: `blog/comment_serializers.py`

```python
from rest_framework import serializers
from .comment_models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
```

Fichier a creer: `blog/comment_views.py`

```python
from rest_framework import generics
from .comment_models import Comment
from .comment_serializers import CommentSerializer


class PostCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["post_id"]).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs["post_id"])
```

Fichier: `blog/urls.py` (ajouter)

```python
from .comment_views import PostCommentListCreateView

urlpatterns += [
    path("posts/<int:post_id>/comments/", PostCommentListCreateView.as_view(), name="post-comments"),
]
```

### Step 3 - Tests API avec pytest

Installer:

```bash
pip install pytest pytest-django
```

Fichier a creer: `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = newspaper.settings
python_files = tests.py test_*.py *_tests.py
```

Fichier a creer: `blog/tests/test_posts_api.py`

```python
import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_list_posts_returns_200():
    client = APIClient()
    response = client.get("/api/posts/")
    assert response.status_code == 200
```

### Step 4 - Qualite code

Installer:

```bash
pip install ruff black pre-commit commitizen
```

Fichier a creer: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
```

Activer:

```bash
pre-commit install
```

### Step 5 - Conventional Commits

Reference officielle:

`https://www.conventionalcommits.org/en/v1.0.0/`

Format:

`type(scope): description`

Exemples:

```text
feat(auth): add login endpoint
fix(posts): prevent anonymous delete
docs(module6): add conventional commits section
```

Types les plus utiles:

- `feat`: nouvelle fonctionnalite
- `fix`: correction de bug
- `docs`: documentation
- `refactor`: refactor sans changement fonctionnel
- `test`: ajout/modif de tests
- `chore`: maintenance

Option 1 (simple): discipline d equipe, verifier les messages en review.

Option 2 (automatisee): hook `commit-msg` avec Commitizen.

Fichier: `.pre-commit-config.yaml` (ajouter ce repo en plus)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.31.0
    hooks:
      - id: commitizen
      - id: commitizen-branch
```

Activer aussi le hook `commit-msg`:

```bash
pre-commit install --hook-type commit-msg
```

Fichier a creer: `.cz.toml`

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v$version"
update_changelog_on_bump = true
```

Verifier un message:

```bash
cz check --message "feat(api): add pagination"
```

Ressources bonus (optionnelles):

- Cheatsheet Conventional Commits: `https://gist.github.com/parmentf/359667bf23e08a1bd8241fbf47ecdef0`
- Conventional Emoji Commits: `https://conventional-emoji-commits.site/quick-summary/summary`
- Gitmoji reference: `https://gitmoji.dev/`

Note pedagogique:

- Commencer par la convention texte standard (`feat`, `fix`, `docs`, etc.).
- Introduire les emojis seulement si toute l equipe est alignee sur la meme convention.

### Step 6 - Settings par environnement

Structure suggeree:

```text
newspaper/settings/
  base.py
  dev.py
  prod.py
```

Fichier exemple: `newspaper/settings/base.py`

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
```

Fichier exemple: `newspaper/settings/dev.py`

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
```

### Step 7 - Deploiement local avec Docker

Fichier a creer: `Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "newspaper.asgi:application"]
```

Fichier a creer: `docker-compose.yml`

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    command: daphne -b 0.0.0.0 -p 8000 newspaper.asgi:application
```

### Step 8 - CI GitHub Actions pour verifier les commits

Objectif: verifier automatiquement que les messages de commit respectent Conventional Commits.

Fichier a creer: `.github/workflows/commit-message-check.yml`

```yaml
name: Commit Message Check

on:
  push:
    branches:
      - main
      - develop
      - "feature/**"
  pull_request:

jobs:
  conventional-commits:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Commitizen
        run: pip install commitizen

      - name: Validate commit messages
        shell: bash
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            cz check --rev-range "${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}"
          else
            BEFORE="${{ github.event.before }}"
            if [ "$BEFORE" = "0000000000000000000000000000000000000000" ]; then
              cz check --rev-range "HEAD~20..HEAD"
            else
              cz check --rev-range "$BEFORE..${{ github.sha }}"
            fi
          fi
```

Tester en local avant push:

```bash
cz check --message "feat(module6): add ci workflow"
```

## Tests de validation

- Pagination et filtres fonctionnent
- Suite de tests passe (`pytest`)
- Lint/format propres
- Messages de commit conformes Conventional Commits
- Build Docker fonctionnel
- Workflow GitHub Actions valide les messages de commit

## Erreurs frequentes

- Config prod melangee avec dev
- Secrets commites
- Tests insuffisants sur permissions
- Messages de commit incoherents

## Exercice de fin

1. Ajouter pagination + search
2. Couvrir permissions par tests
3. Ecrire 5 commits avec le format Conventional Commits
4. Fournir un `docker-compose.yml` minimal
5. Ajouter un workflow CI qui bloque les commits non conformes
6. Ecrire une checklist de pre-deploiement

## Checklist fin de module

- Qualite outillee
- Tests robustes
- Convention de commit appliquee
- Config claire dev/prod
- Deploiement local reproductible
- CI activee pour verifier les messages de commit
