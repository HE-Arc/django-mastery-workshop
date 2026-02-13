# Module 3 Enseignant - JWT et permissions

## Duree totale

- 90 minutes

## Plan minute par minute

1. 0-10 min: panorama auth (session/token/basic/jwt/oauth2)
2. 10-25 min: install + config SimpleJWT
3. 25-40 min: routes token
4. 40-60 min: protection CRUD
5. 60-80 min: tests swagger/postman/curl
6. 80-90 min: quiz + recap

## Script de demo

1. Installer:

```bash
pip install djangorestframework-simplejwt
```

2. Creer un utilisateur de test:

```bash
python manage.py createsuperuser
```

3. Ajouter config JWT dans `newspaper/settings.py`.
4. Ajouter routes:
   - `api/token/`
   - `api/token/refresh/`
5. Ajouter endpoints metier:
   - `POST /api/auth/register/`
   - `POST /api/auth/login/`
   - `POST /api/auth/password-reset/request/`
   - `POST /api/auth/password-reset/confirm/`
6. Ajouter documentation Swagger des endpoints auth via `@extend_schema`:
   - tag `Auth`
   - schemas request/response
7. Proteger `PostViewSet` avec `IsAuthenticatedOrReadOnly`.
8. Test live:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"etudiant1\",\"email\":\"etudiant1@example.com\",\"password\":\"Password123!\",\"password_confirm\":\"Password123!\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"etudiant1@example.com\",\"password\":\"Password123!\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/api/auth/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"etudiant1@example.com\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d "{\"uid\":\"<UID>\",\"token\":\"<TOKEN>\",\"new_password\":\"Password456!\",\"new_password_confirm\":\"Password456!\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin\"}"
```

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"JWT demo\",\"content\":\"Contenu long pour la classe.\",\"status\":\"draft\"}"
```

9. Verification visuelle dans Swagger:
   - Ouvrir `http://127.0.0.1:8000/api/docs/`
   - Verifier le tag `Auth`
   - Executer `register`, `login`, `password-reset/request`, `password-reset/confirm`

## Questions a poser

1. Pourquoi JWT est pratique pour un front SPA/mobile ?
2. Difference access token vs refresh token ?
3. Pourquoi auth != autorisation ?
4. A quoi sert une permission custom objet ?
5. Pourquoi la reponse password-reset/request doit rester generique ?

## Mini quiz (5 min)

1. Le refresh token sert a acceder directement aux ressources. Vrai/Faux ?
2. Sans header `Authorization`, endpoint protege doit refuser. Vrai/Faux ?
3. JWT remplace automatiquement les permissions DRF. Vrai/Faux ?

Corrige:

1. Faux
2. Vrai
3. Faux

## Critere de reussite

- Les etudiants savent obtenir et utiliser un token.
- Les etudiants savent proteger lecture/ecriture.
- Les etudiants savent debugger un `401 Unauthorized`.
