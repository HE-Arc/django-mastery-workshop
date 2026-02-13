# Module 4 Enseignant - WebSockets et temps reel

## Duree totale

- 90 minutes

## Plan minute par minute

1. 0-10 min: HTTP vs WebSocket
2. 10-25 min: settings channels/daphne
3. 25-40 min: asgi + routing
4. 40-55 min: consumer + groupes
5. 55-75 min: emission d events depuis le viewset
6. 75-85 min: demo live ws-demo
7. 85-90 min: quiz

## Script de demo

1. Verifier `INSTALLED_APPS`:
   - `daphne`
   - `channels`
2. Verifier `ASGI_APPLICATION`.
3. Montrer `newspaper/asgi.py`.
4. Montrer `blog/routing.py` + `blog/consumers.py`.
5. Ajouter `perform_create` et `perform_destroy` dans `blog/views.py`.
6. Lancer serveur et ouvrir:
   - `http://127.0.0.1:8000/ws-demo/`
7. Faire POST `/api/posts/` et observer event recu.
8. Faire login dans la page demo (JWT), supprimer un post et observer event `post_deleted`.

## Questions a poser

1. Pourquoi un groupe WS est utile ?
2. Difference entre websocket URL et URL REST ?
3. Pourquoi `file://` casse la demo (CORS) ?
4. Quand preferer WebSocket plutot que polling ?
5. Pourquoi la suppression demande un token JWT ?

## Mini quiz (5 min)

1. WebSocket ouvre une connexion persistante. Vrai/Faux ?
2. `404 /ws/blog/` peut indiquer un souci ASGI/routing. Vrai/Faux ?
3. `perform_create` est appele sur GET list. Vrai/Faux ?
4. `DELETE /api/posts/{id}/` peut etre anonyme avec `IsAuthenticatedOrReadOnly`. Vrai/Faux ?

Corrige:

1. Vrai
2. Vrai
3. Faux
4. Faux

## Critere de reussite

- Les etudiants comprennent pipeline WS complet.
- Event `post_created` diffuse vers les clients connectes.
- Event `post_deleted` diffuse vers les clients connectes.
- Les etudiants savent diagnostiquer les erreurs courantes.
