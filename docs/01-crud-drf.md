# Module 1 - CRUD API avec Django REST Framework

## Objectifs

- Construire un modele `Post`
- Exposer un CRUD REST via `ModelViewSet`
- Comprendre `makemigrations` vs `migrate`
- Tester l API avec cURL et Swagger

## Prerequis

- Environnement virtuel actif
- Dependances installees: `django`, `djangorestframework`

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

### Step 1 - Verifier la base projet

```bash
python manage.py check
```

### Step 2 - Configurer les apps

Fichier: `newspaper/settings.py`

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "blog",
]
```

### Step 3 - Definir le modele

Fichier: `blog/models.py`

```python
from django.db import models


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

### Step 4 - Generer et appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5 - Creer le serializer

Fichier a creer: `blog/serializers.py`

```python
from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
```

### Step 6 - Creer le ViewSet

Fichier: `blog/views.py`

```python
from rest_framework.viewsets import ModelViewSet
from .models import Post
from .serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
```

### Step 7 - Declarer les routes de l app

Fichier a creer: `blog/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
```

### Step 8 - Brancher les routes globales

Fichier: `newspaper/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("blog.urls")),
]
```

### Step 9 - Lancer et tester

```bash
python manage.py runserver
```

```bash
curl http://127.0.0.1:8000/api/posts/
```

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Post demo\",\"content\":\"Mon contenu\",\"status\":\"draft\"}"
```

## Tests de validation

- `GET /api/posts/` retourne une liste
- `POST /api/posts/` cree un objet
- `GET /api/posts/{id}/` retourne l objet cree
- `PATCH /api/posts/{id}/` met a jour un champ
- `DELETE /api/posts/{id}/` supprime l objet

## Erreurs frequentes

- `No module named rest_framework`: package non installe
- Table non creee: migrations non appliquees
- `404 /api/posts/`: route `include("blog.urls")` absente

## Exercice de fin

1. Ajouter un champ `summary` (max 300)
2. Rendre `summary` optionnel
3. Exposer ce champ dans le serializer
4. Verifier la migration et les endpoints

## Checklist fin de module

- Modele OK
- Serializer OK
- ViewSet OK
- Routes OK
- CRUD teste de bout en bout
