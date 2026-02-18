# django-mastery-workshop

Workshop Django academique concu pour apprendre a construire une API robuste, securisee et temps reel, de la base CRUD jusqu au deploiement.

- **Auteur :** Abraham Ricardo Hernandez Sompare
- **Supervision :** David Grunenwald

Ce README suit un format tutorial pas a pas.  
Objectif: partir d un projet Django + DRF et arriver a:

- une API CRUD `Post`
- une doc Swagger
- un event WebSocket envoye a la creation d un post

## Parcours modulaire 

Tu peux aussi suivre le cours par modules separes dans `docs/`:

1. `docs/01-crud-drf.md`
2. `docs/02-securite-drf.md`
3. `docs/03-auth-jwt-permissions.md`
4. `docs/04-websockets-realtime.md`
5. `docs/05-admin-wysiwyg-mini-cms.md`
6. `docs/06-bonus-qualite-tests-deploiement.md`

Index global: `docs/README.md`

Version enseignant: `docs/teacher/README.md`

## Sommaire

- [django-mastery-workshop](#django-mastery-workshop)
  - [Parcours modulaire (nouveau)](#parcours-modulaire-nouveau)
  - [Sommaire](#sommaire)
  - [Step 0 - Prerequis](#step-0---prerequis)
  - [Step 1 - Creer et activer l environnement](#step-1---creer-et-activer-l-environnement)
  - [Step 2 - Installer les dependances](#step-2---installer-les-dependances)
  - [Step 3 - Creer le projet et l app](#step-3---creer-le-projet-et-l-app)
  - [Step 4 - Declarer les apps dans settings](#step-4---declarer-les-apps-dans-settings)
  - [Step 5 - Creer le modele Post](#step-5---creer-le-modele-post)
  - [Step 6 - Generer et appliquer les migrations](#step-6---generer-et-appliquer-les-migrations)
  - [Step 7 - Creer le serializer](#step-7---creer-le-serializer)
  - [Step 8 - Creer le ViewSet](#step-8---creer-le-viewset)
  - [Step 9 - Exposer les routes CRUD](#step-9---exposer-les-routes-crud)
  - [Step 10 - Activer Swagger](#step-10---activer-swagger)
  - [Step 11 - Activer Channels (WebSocket)](#step-11---activer-channels-websocket)
  - [Step 12 - Routing WebSocket](#step-12---routing-websocket)
  - [Step 13 - Consumer WebSocket](#step-13---consumer-websocket)
  - [Step 14 - Envoyer un event WS au create](#step-14---envoyer-un-event-ws-au-create)
  - [Step 15 - Tester REST + Swagger + WS](#step-15---tester-rest--swagger--ws)
    - [15.1 Demarrer le serveur](#151-demarrer-le-serveur)
    - [15.2 Tester CRUD](#152-tester-crud)
    - [15.3 Ouvrir Swagger](#153-ouvrir-swagger)
    - [15.4 Tester le WebSocket rapidement](#154-tester-le-websocket-rapidement)
  - [FAQ courte](#faq-courte)
  - [Ressources](#ressources)
  - [Auteur et supervision](#auteur-et-supervision)

## Step 0 - Prerequis

- Python 3.12+
- `pip`
- terminal (PowerShell/CMD/bash)

## Step 1 - Creer et activer l environnement

```bash
mkdir django-project
cd django-project
python -m venv env
```

Activation:

- Windows PowerShell:

```powershell
env\Scripts\Activate.ps1
```

- Linux/macOS:

```bash
source env/bin/activate
```

## Step 2 - Installer les dependances

```bash
pip install django djangorestframework drf-spectacular channels daphne
```

## Step 3 - Creer le projet et l app

```bash
django-admin startproject newspaper .
python manage.py startapp blog
```

## Step 4 - Declarer les apps dans settings

Fichier: `newspaper/settings.py`

Ajoute/valide:

```python
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "channels",
    "blog",
]
```

Ajoute aussi:

```python
WSGI_APPLICATION = "newspaper.wsgi.application"
ASGI_APPLICATION = "newspaper.asgi.application"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Newspaper API",
    "DESCRIPTION": "API CRUD newspaper Django/DRF",
    "VERSION": "1.0.0",
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
```

Et pour servir les templates de demo:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        # ...
    }
]
```

## Step 5 - Creer le modele Post

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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

## Step 6 - Generer et appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

Rappel:

- `makemigrations` genere les fichiers de migration
- `migrate` applique ces migrations en base

## Step 7 - Creer le serializer

Fichier: `blog/serializers.py`

```python
from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
```

## Step 8 - Creer le ViewSet

Fichier: `blog/views.py`

```python
from rest_framework.viewsets import ModelViewSet
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Post
from .serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        post = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "blog_feed",
            {
                "type": "blog_event",
                "data": {
                    "event": "post_created",
                    "id": post.id,
                    "title": post.title,
                    "status": post.status,
                },
            },
        )
```

## Step 9 - Exposer les routes CRUD

Fichier: `blog/urls.py`

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

Fichier: `newspaper/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("blog.urls")),
    path("ws-demo/", TemplateView.as_view(template_name="ws_demo.html"), name="ws-demo"),
]
```

Endpoints CRUD disponibles:

- `GET /api/posts/`
- `POST /api/posts/`
- `GET /api/posts/{id}/`
- `PUT /api/posts/{id}/`
- `PATCH /api/posts/{id}/`
- `DELETE /api/posts/{id}/`

## Step 10 - Activer Swagger

Swagger est deja configure via:

- `drf_spectacular` dans `INSTALLED_APPS`
- `REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"]`
- routes `/api/schema/` et `/api/docs/`

URLs:

- Schema JSON: `http://127.0.0.1:8000/api/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`

## Step 11 - Activer Channels (WebSocket)

Channels est deja configure via:

- `daphne` installe et present dans `INSTALLED_APPS` (pour avoir WS avec `runserver`)
- `channels` dans `INSTALLED_APPS`
- `ASGI_APPLICATION = "newspaper.asgi.application"`
- `CHANNEL_LAYERS` (InMemory)

Fichier: `newspaper/asgi.py`

```python
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import blog.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspaper.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(blog.routing.websocket_urlpatterns),
    }
)
```

## Step 12 - Routing WebSocket

Fichier: `blog/routing.py`

```python
from django.urls import path
from .consumers import BlogConsumer

websocket_urlpatterns = [
    path("ws/blog/", BlogConsumer.as_asgi()),
]
```

## Step 13 - Consumer WebSocket

Fichier: `blog/consumers.py`

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BlogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "blog_feed"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def blog_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))
```

## Step 14 - Envoyer un event WS au create

Deja fait dans `blog/views.py` avec la methode `perform_create`.

Payload envoye:

```json
{
  "event": "post_created",
  "id": 1,
  "title": "Mon post",
  "status": "draft"
}
```

## Step 15 - Tester REST + Swagger + WS

### 15.1 Demarrer le serveur

Option A (celle que tu utilises maintenant, avec `daphne` dans `INSTALLED_APPS`):

```bash
python manage.py runserver
```

Option B (equivalente, en lancant Daphne explicitement):

```bash
daphne -b 127.0.0.1 -p 8000 newspaper.asgi:application
```

### 15.2 Tester CRUD

```bash
curl http://127.0.0.1:8000/api/posts/
```

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Mon post\",\"content\":\"Contenu\",\"status\":\"draft\"}"
```

### 15.3 Ouvrir Swagger

- `http://127.0.0.1:8000/api/docs/`

### 15.4 Tester le WebSocket rapidement

1. Ouvre `http://127.0.0.1:8000/ws-demo/` dans ton navigateur.
2. Fais un `POST /api/posts/`.
3. Verifie le message recu dans le log.

Important:

- n ouvre pas `ws_demo.html` en `file://...`, sinon tu auras une erreur CORS
- la page a utiliser pour le test est `http://127.0.0.1:8000/ws-demo/`

## FAQ courte

`Q: Pourquoi j ai "No module named drf_spectacular" ou "No module named channels" ?`

- L environnement actif n a pas toutes les deps.
- Refaire: `pip install drf-spectacular channels daphne`.

`Q: Pourquoi le WS ne recoit rien ?`

- Verifie `newspaper/asgi.py` (ProtocolTypeRouter)
- Verifie `blog/routing.py` et URL `ws://127.0.0.1:8000/ws/blog/`
- Verifie que `perform_create` est present dans `blog/views.py`

`Q: Pourquoi j ai `404 /ws/blog/` ?`

- Verifie que `daphne` est installe.
- Verifie que `"daphne"` est dans `INSTALLED_APPS`.
- Relance le serveur (`python manage.py runserver`).

`Q: Pourquoi j ai une erreur CORS dans ws_demo.html ?`

- Tu as probablement ouvert le fichier en `file://`.
- Ouvre la page via Django: `http://127.0.0.1:8000/ws-demo/`.

`Q: Quelle difference entre WSGI et ASGI ?`

- WSGI: HTTP classique
- ASGI: HTTP + protocoles async (ex: WebSocket)

## Ressources

- Django Models: https://docs.djangoproject.com/en/6.0/topics/db/models/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- drf-spectacular: https://drf-spectacular.readthedocs.io/
- Django Channels: https://channels.readthedocs.io/


## Auteur et supervision

- Auteur: ABRAHAM RICARDO HERNANDEZ SOMPARE
- Concu sous la supervision de David Grunenwald
