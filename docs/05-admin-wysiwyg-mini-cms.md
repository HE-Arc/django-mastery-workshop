# Module 5 - Admin WYSIWYG et mini CMS

## Objectifs

- Integrer un editeur riche pour `content`
- Gerer upload d images
- Afficher du HTML de facon maitrisee
- Rappeler les risques XSS

## Prerequis

- Module CRUD termine
- Admin Django actif

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

### Step 1 - Installer les dependances

```bash
pip install django-ckeditor-5 pillow
```

Ou via fichier:

```bash
pip install -r requirements.txt
```

### Step 2 - Configurer settings

Fichier: `newspaper/settings.py`

```python
INSTALLED_APPS = [
    # ...
    "django_ckeditor_5",
    "blog",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": ["heading", "|", "bold", "italic", "link", "bulletedList", "numberedList", "imageUpload", "undo", "redo"],
    },
    "extends": {
        "toolbar": ["heading", "|", "bold", "italic", "underline", "link", "bulletedList", "numberedList", "insertTable", "imageUpload", "undo", "redo"],
    },
}
```

### Step 3 - Mettre a jour le modele Post

Fichier: `blog/models.py`

```python
from django_ckeditor_5.fields import CKEditor5Field
from django.db import models


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField(max_length=200)
    content = CKEditor5Field("Text", config_name="extends")
    cover_image = models.ImageField(upload_to="posts/covers/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

Appliquer migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4 - Configurer l admin

Fichier: `blog/admin.py`

```python
from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "content")
```

### Step 5 - Exposer routes media et ckeditor en dev

Fichier: `newspaper/urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("api/", include("blog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Step 6 - Rendu HTML (avec precaution)

Fichier template exemple: `templates/post_detail.html`

```html
<h1>{{ post.title }}</h1>
{% if post.cover_image %}
  <img src="{{ post.cover_image.url }}" alt="{{ post.title }}" />
{% endif %}
<div>
  {{ post.content|safe }}
</div>
```

Note securite:

- `|safe` uniquement si le contenu vient d une source de confiance (admin).

## Tests de validation

- Creation d un post riche via admin
- Upload image fonctionnel
- Rendu HTML visible sur une page dediee

## Erreurs frequentes

- Oublier `pillow` pour les images
- `MEDIA_ROOT` non configure
- Usage abusif de `|safe` sur contenu non fiable

## Exercice de fin

1. Ajouter une page detail `post/<slug>/`
2. Afficher le contenu HTML
3. Afficher l image si presente
4. Documenter les garde-fous securite

## Checklist fin de module

- Editeur riche operationnel
- Upload media operationnel
- Rendu HTML controle
- Risques XSS compris
