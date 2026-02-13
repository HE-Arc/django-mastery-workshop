# Module 2 - Securite Django / DRF fondamentaux

## Objectifs

- Comprendre la surface d attaque d une API
- Poser des regles de base: validation, permissions, erreurs, logs, secrets
- Distinguer CORS et CSRF dans un contexte API

## Prerequis

- Module CRUD termine
- API fonctionnelle sur `/api/posts/`

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

### Step 1 - Renforcer la validation serializer

Fichier: `blog/serializers.py`

```python
from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_content(self, value):
        if len(value.strip()) < 50:
            raise serializers.ValidationError("Le contenu doit faire au moins 50 caracteres.")
        return value

    def validate(self, attrs):
        status = attrs.get("status", "draft")
        content = attrs.get("content", "")
        if status == "published" and len(content.strip()) < 50:
            raise serializers.ValidationError(
                {"status": "Impossible de publier un contenu trop court."}
            )
        return attrs
```

### Step 2 - Ajouter des permissions minimales

Fichier: `blog/views.py`

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from .models import Post
from .serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

### Step 3 - Uniformiser les erreurs API

Fichier a creer: `newspaper/api_exceptions.py`

```python
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "ok": False,
            "status_code": response.status_code,
            "errors": response.data,
        }
    return response
```

Fichier: `newspaper/settings.py`

```python
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "newspaper.api_exceptions.custom_exception_handler",
}
```

### Step 4 - Sortir les secrets du code

Installer:

```bash
pip install python-decouple
```

Fichier: `.env` (a creer)

```dotenv
SECRET_KEY=change-me-please
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Fichier: `newspaper/settings.py`

```python
from decouple import config, Csv

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
```

Fichier: `.gitignore` (ajouter)

```gitignore
.env
```

### Step 5 - CORS (si frontend separe)

Installer:

```bash
pip install django-cors-headers
```

Fichier: `newspaper/settings.py`

```python
INSTALLED_APPS = [
    # ...
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]
```

Note:

- Evite `CORS_ALLOW_ALL_ORIGINS=True` en dehors des demos.

### Step 6 - Introduire une Security Policy (CRA style)

Fichier a creer: `SECURITY_POLICY.md`

Contenu minimal recommande:

- scope du projet
- gestion des dependances pinnees
- frequence des audits
- politique de reponse aux vulnerabilites
- SLA de correction (ex: 72h pour critique)

Un exemple complet est deja present dans ce repo: `SECURITY_POLICY.md`.

### Step 7 - Audits de vulnerabilites + SBOM

Installer outils:

```bash
pip install pip-audit cyclonedx-bom
```

Audit local:

```bash
pip-audit -r requirements.txt > audit-report.txt
```

Audit via Docker:

```bash
docker compose exec web pip-audit -r requirements.txt > audit-report.txt
```

Generation SBOM:

```bash
cyclonedx-py requirements --output-file sbom.json --output-format json
```

Bonnes pratiques:

- conserver `audit-report.txt` dans les artefacts CI ou dossier `security/`
- regenerer `sbom.json` apres chaque changement de dependances
- tracer la date et le resultat dans `SECURITY_POLICY.md`

## Tests de validation

- Un utilisateur anonyme ne peut pas `POST` si endpoint protege
- Les erreurs de validation sont explicites
- Les secrets ne sont plus hardcodes
- CORS accepte uniquement les origines autorisees
- `audit-report.txt` est genere sans vuln critique
- `sbom.json` est genere

## Erreurs frequentes

- Confondre `401` et `403`
- Ouvrir CORS sur `*` sans raison
- Utiliser `AllowAny` en production par oubli
- Lancer `pip-audit` sans figer les versions dans `requirements.txt`

## Exercice de fin

1. Mettre `IsAuthenticatedOrReadOnly` sur `PostViewSet`
2. Ajouter validation `content >= 50 caracteres`
3. Bloquer `status=published` si contenu trop court
4. Verifier les messages d erreur uniformises
5. Creer `SECURITY_POLICY.md` avec cadence d audit + SLA
6. Generer `audit-report.txt` et `sbom.json`

## Checklist fin de module

- Validation metier en place
- Permissions minimales en place
- Secrets externalises
- CORS/CSRF expliques et testes
- Security Policy documentee
- Audit + SBOM produits
