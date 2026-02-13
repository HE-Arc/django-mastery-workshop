# Module 1 Enseignant - CRUD DRF

## Duree totale

- 90 minutes

## Plan minute par minute

1. 0-10 min: objectif du module et architecture Django/DRF
2. 10-25 min: modele + migrations
3. 25-40 min: serializer
4. 40-55 min: viewset
5. 55-70 min: routing
6. 70-85 min: tests API live
7. 85-90 min: recap + quiz

## Script de demo

1. Montrer `blog/models.py` et expliquer chaque champ.
2. Lancer:

```bash
python manage.py makemigrations
python manage.py migrate
```

3. Montrer `blog/serializers.py`.
4. Montrer `blog/views.py` (`ModelViewSet`).
5. Montrer `blog/urls.py` + `newspaper/urls.py`.
6. Lancer:

```bash
python manage.py runserver
```

7. Tester:

```bash
curl http://127.0.0.1:8000/api/posts/
```

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Post demo\",\"content\":\"Contenu long de test pour la classe.\",\"status\":\"draft\"}"
```

## Questions a poser

1. Quelle est la difference entre modele et serializer ?
2. Pourquoi `makemigrations` et `migrate` sont separes ?
3. Que genere un `ModelViewSet` sans code supplementaire ?
4. Pourquoi on utilise un router DRF ?

## Mini quiz (5 min)

1. `makemigrations` modifie la base directement. Vrai/Faux ?
2. `fields = "__all__"` expose tous les champs. Vrai/Faux ?
3. Le router DRF cree aussi la route detail. Vrai/Faux ?

Corrige:

1. Faux
2. Vrai
3. Vrai

## Critere de reussite

- Les etudiants savent creer un endpoint CRUD complet.
- Les etudiants savent expliquer pipeline: model -> serializer -> viewset -> urls.

