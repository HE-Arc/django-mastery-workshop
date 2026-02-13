# Module 2 Enseignant - Securite DRF fondamentaux

## Duree totale

- 75 minutes

## Plan minute par minute

1. 0-10 min: surface d attaque API
2. 10-25 min: validation serializer
3. 25-40 min: permissions DRF
4. 40-55 min: gestion d erreurs
5. 55-65 min: secrets et .env
6. 65-72 min: CORS/CSRF
7. 72-75 min: Security Policy + quiz

## Script de demo

1. Ajouter validation dans `blog/serializers.py`.
2. Ajouter permission:

```python
permission_classes = [IsAuthenticatedOrReadOnly]
```

3. Faire un POST anonyme et montrer le refus.
4. Ajouter `.env` puis remplacer `SECRET_KEY` hardcode.
5. Expliquer difference:
   - CORS (navigateur)
   - CSRF (session/cookie)
6. Introduire `SECURITY_POLICY.md`:
   - scope
   - frequence audit
   - SLA vuln critique (72h)
7. Montrer commandes:

```bash
pip-audit -r requirements.txt > audit-report.txt
cyclonedx-py requirements --output-file sbom.json --output-format json
```

## Questions a poser

1. Pourquoi une validation metier ne doit pas rester seulement dans le front ?
2. Difference entre `401` et `403` ?
3. Pourquoi `CORS_ALLOW_ALL_ORIGINS=True` est dangereux ?
4. Pourquoi stocker les secrets dans `.env` ?
5. A quoi sert une Security Policy dans une API ?

## Mini quiz (5 min)

1. `IsAuthenticatedOrReadOnly` autorise ecriture anonyme. Vrai/Faux ?
2. CORS protege contre les injections SQL. Vrai/Faux ?
3. Un secret commit dans Git peut rester expose meme apres suppression. Vrai/Faux ?
4. Un audit deps et un SBOM doivent etre rejoues apres update dependances. Vrai/Faux ?

Corrige:

1. Faux
2. Faux
3. Vrai
4. Vrai

## Critere de reussite

- Les etudiants appliquent une permission de base correcte.
- Les etudiants savent externaliser les secrets.
- Les etudiants distinguent clairement CORS et CSRF.
- Les etudiants comprennent le role d une Security Policy et des audits SBOM/audit.
