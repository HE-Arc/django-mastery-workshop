# Module 4 - WebSockets et temps reel avec Channels

## Objectifs

- Comprendre le modele WebSocket (connexion persistante)
- Mettre en place `consumer`, `routing`, `groupes`
- Diffuser des evenements metier en temps reel

## Prerequis

- `channels` et `daphne` installes
- `ASGI_APPLICATION` configure
- Module CRUD termine

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

### Step 1 - Configurer Channels

Fichier: `newspaper/settings.py`

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

ASGI_APPLICATION = "newspaper.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
```

### Step 2 - Configurer ASGI

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

### Step 3 - Creer le routing WebSocket

Fichier a creer: `blog/routing.py`

```python
from django.urls import path
from .consumers import BlogConsumer

websocket_urlpatterns = [
    path("ws/blog/", BlogConsumer.as_asgi()),
]
```

### Step 4 - Creer le consumer

Fichier a creer: `blog/consumers.py`

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

### Step 5 - Emettre des evenements depuis le ViewSet

Fichier: `blog/views.py`

```python
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.viewsets import ModelViewSet
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

    def perform_destroy(self, instance):
        post_id = instance.id
        title = instance.title
        status_value = instance.status
        instance.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "blog_feed",
            {
                "type": "blog_event",
                "data": {
                    "event": "post_deleted",
                    "id": post_id,
                    "title": title,
                    "status": status_value,
                },
            },
        )
```

Extension conseillee:

```python
    def perform_update(self, serializer):
        post = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "blog_feed",
            {
                "type": "blog_event",
                "data": {
                    "event": "post_updated",
                    "id": post.id,
                    "title": post.title,
                    "status": post.status,
                },
            },
        )
```

### Step 6 - Page de demo

Fichier template deja present: `templates/ws_demo.html`

Route de demo a verifier dans `newspaper/urls.py`:

```python
from django.views.generic import TemplateView

urlpatterns = [
    # ...
    path("ws-demo/", TemplateView.as_view(template_name="ws_demo.html"), name="ws-demo"),
]
```

Utilisation:

1. Lancer serveur
2. Ouvrir `http://127.0.0.1:8000/ws-demo/`
3. Se connecter dans le bloc "Authentification" (email/password) ou creer un compte avec "Register"
4. Verifier que les tokens JWT sont presents (access + refresh)
5. Creer un article avec le bloc "Create post"
6. Supprimer un article avec le bouton "Supprimer"
7. Verifier le log WS (`post_created`, `post_updated`, `post_deleted`)

Important:

- Ne pas ouvrir `ws_demo.html` en `file://` (sinon CORS).
- `DELETE` requiert un token JWT valide (`IsAuthenticatedOrReadOnly`).
- Si `DEBUG=True`, la section reset password affiche `uid/token` pour tester rapidement.

## Tests de validation

- Connexion WS etablie dans le navigateur
- POST API declenche un message WS
- DELETE API declenche un message WS `post_deleted`
- Le post est retire de la liste dans le template
- Les autres clients connectes recoivent aussi le message

## Erreurs frequentes

- `404 /ws/blog/`: serveur WS non actif ou config ASGI incomplete
- CORS en demo: page ouverte en `file://`
- Event envoye mais groupe incorrect (`blog_feed` mismatch)
- `401/403` sur DELETE: login/token JWT manquant ou invalide

## Exercice de fin

1. Ajouter `post_updated` (si absent)
2. Ajouter un compteur de clients connectes
3. Afficher l event dans la page demo avec timestamp

## Checklist fin de module

- WS connecte
- `post_created` diffuse
- `post_deleted` diffuse
- Page demo validee
- Cas d erreurs connus documentes
