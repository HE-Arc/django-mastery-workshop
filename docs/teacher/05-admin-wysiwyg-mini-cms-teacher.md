# Module 5 Enseignant - Admin WYSIWYG mini CMS

## Duree totale

- 75 minutes

## Plan minute par minute

1. 0-10 min: pourquoi un mini CMS admin
2. 10-25 min: install ckeditor5 + pillow
3. 25-40 min: modele + migrations
4. 40-55 min: admin + media
5. 55-70 min: rendu HTML et securite
6. 70-75 min: quiz

## Script de demo

1. Installer:

```bash
pip install django-ckeditor-5 pillow
```

2. Ajouter app `django_ckeditor_5` + media dans `newspaper/settings.py`.
3. Modifier `blog/models.py` pour `CKEditor5Field`.
4. Faire migrations.
5. Configurer `blog/admin.py` list/filter/search.
6. Ajouter route `ckeditor5/` + media en debug dans `newspaper/urls.py`.
7. Creer un post via admin avec image.
8. Afficher sur template detail.

Option: installer tout via `pip install -r requirements.txt`.

## Questions a poser

1. Pourquoi `|safe` est riske si source non fiable ?
2. Pourquoi `pillow` est obligatoire pour `ImageField` ?
3. Difference entre stockage media et static ?
4. Quel est le role d un back office admin dans une API ?

## Mini quiz (5 min)

1. `ImageField` fonctionne sans `pillow`. Vrai/Faux ?
2. `MEDIA_ROOT` sert aux uploads runtime. Vrai/Faux ?
3. Tout contenu HTML peut etre rendu avec `|safe` sans risque. Vrai/Faux ?

Corrige:

1. Faux
2. Vrai
3. Faux

## Critere de reussite

- Les etudiants savent configurer un champ riche.
- Les etudiants savent gerer media en dev.
- Les etudiants comprennent le risque XSS.
