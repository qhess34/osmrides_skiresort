# AGENTS.md — osmrides_skiresort

Dépôt de les stations de ski d'OSMrides (Vars Les Claux d'abord, télésiège Escondus V15) : données OSM des remontées et pistes, réglages, pages de jeu.
Fait partie d'OSMrides (simulations d'exploitation sur données OpenStreetMap, jeu de fan non officiel, interface en français). Organisation des quatre dépôts et règles communes : `docs/ORGANISATION.md` du dépôt `qhess34/osmrides` (à lire une fois).

## Responsable : Chef stations

Session longue lancée par le propriétaire ; mémoire et reprise : `docs/PILOTAGE.md`. Le chef code peu : il lit les issues, découpe, délègue à un sous-agent (`.claude/agents/`), vérifie, publie sur `main`, rend compte au propriétaire en français court (fait, testé, non testé, estimé).

## Règles du propriétaire

- Réalisme : rendu crédible, couleurs sourdes, aucun pictogramme ni emoji, rien d'enfantin.
- OSM est la référence ; tout ce qui est estimé est signalé dans le code et dit au propriétaire.
- Code lisible, KISS ; aucune dépendance, tout marche en ouvrant le fichier (`file://`), sans `fetch` ni modules ES.
- Moteur et éditeur **chargés par version** (`const MOTEUR='0.0.1';` dans `jeu.html`, mode d'emploi : `docs/versions.md` d'osmrides) : aucun dossier `engine/` ni `editor/` ici. Le code propre au ski (télésiège, remontées, pistes) se fait ici ; un besoin du noyau générique = issue `inter-equipe` dans `qhess34/osmrides`.
- Éditeur : `docker compose up -d` → http://127.0.0.1:8787/ (`compose.yaml`). Tests en session cloud : clone voisin d'osmrides, `jeu.html?…&moteur=../osmrides/engine/`.
- Git : branche `main`, commits directs, messages en anglais à l'impératif.

## Tests

tests de jeu propres aux remontées (à écrire sur le modèle de `tools/check.js` d'osmrides) ; relever les erreurs de page. Captures seulement pour un point visuel (une petite, ≈ 600×450, JPEG ≈ 70, regardée une fois).

## Économie de tokens

- Lire : ce fichier, `docs/PILOTAGE.md`, les issues ouvertes. Le reste par l'`explorateur` (Haiku).
- Un sous-agent par tâche, consigne autonome (réponses du propriétaire recopiées), rapport ≤ 8 lignes. Modèle : Haiku (recherche, tests), Sonnet (travail courant), Opus seulement sur demande du propriétaire.
- Ne jamais lire en entier un fichier de données généré (`*.data.js`).
