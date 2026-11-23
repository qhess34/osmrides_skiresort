#!/usr/bin/env python3
"""Fabrique lieux/ski/vars/escondus.data.js à partir de l'API OpenStreetMap (sans dépendance).

Usage :
  python3 tools/make_ski.py                       télécharge les tuiles dans tools/.cache/ (si absentes) et écrit les données
  python3 tools/make_ski.py extrait1.osm [...]    utilise ces extraits (.osm) au lieu de télécharger

Tuiles API : 0,045 x 0,05 degré au plus (docs/vars-notes.md d'osmrides). Origine (0, 0) = gare aval de la remontée ; x vers l'est, z vers le sud, en mètres.
Données OSM : remontée Escondus V15 (way 21103735) -> circuit du câble (OSM.cps, boucle fermée : montée, poulie amont, descente, poulie aval) ;
bâtiments, routes et chemins, bois, eau, arbres, pylônes, autres remontées (OSM.lifts), pistes (OSM.pistes : piste:type, difficulté, nom).
ESTIMÉ (signalé dans le fichier généré) : profil en hauteur (aucun « ele » dans OSM), écart entre brins montant et descendant, rayon des poulies.
"""
import sys, os, json, math, urllib.request, xml.etree.ElementTree as ET

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, '..', 'lieux', 'ski', 'vars', 'escondus.data.js')
CACHE = os.path.join(ICI, '.cache')
LIFT = '21103735'                      # Escondus V15 (chair_lift)
STATION_AVAL = '226930878'             # gare aval (aerialway:access=entry)
BLD_AVAL = '1034567095'                # bâtiment de la gare aval
# fenêtre conservée (mètres autour de la gare aval) : x0, x1, z0, z1
BBOX = [-900, 320, -230, 1340]
# tuiles API (lon0, lat0, lon1, lat1), chacune <= 0,045 x 0,05
TUILES = [(6.655, 44.555, 6.700, 44.585)]
ECART = 4.2          # ESTIMÉ : écart entre le brin montant et le brin descendant du câble (m)
H_CABLE = 5.0        # ESTIMÉ : hauteur du câble au-dessus du sol (m)
DENIVELE = 230.0     # ESTIMÉ : dénivelé gare aval -> gare amont (m), aucun « ele » dans OSM ; altitude aval ~1850 m (ESTIMÉ)
ST_LEN = 18.0        # ESTIMÉ : longueur de la gare (de st0 à st1)
RAYON = 2.4          # ESTIMÉ : rayon des poulies (m)


def telecharger():
    os.makedirs(CACHE, exist_ok=True)
    fichiers = []
    for i, (a, b, c, d) in enumerate(TUILES):
        f = os.path.join(CACHE, 'tuile%d.osm' % i)
        if not os.path.exists(f):
            url = 'https://api.openstreetmap.org/api/0.6/map?bbox=%s,%s,%s,%s' % (a, b, c, d)
            print('téléchargement', url)
            req = urllib.request.Request(url, headers={'User-Agent': 'osmrides_skiresort/make_ski'})
            with urllib.request.urlopen(req, timeout=180) as r, open(f, 'wb') as o:
                o.write(r.read())
        fichiers.append(f)
    return fichiers


fichiers = sys.argv[1:] or telecharger()
NODE, NTAG, WAY, WTAG, VER = {}, {}, {}, {}, {}
for f in fichiers:
    for e in ET.parse(f).getroot():
        if e.tag not in ('node', 'way'): continue
        i = e.get('id'); t = {x.get('k'): x.get('v') for x in e.findall('tag')}
        VER[e.tag[0] + i] = int(e.get('version') or 0)
        if e.tag == 'node':
            NODE[i] = (float(e.get('lat')), float(e.get('lon')))
            if t: NTAG[i] = t
        else:
            WAY[i] = [x.get('ref') for x in e.findall('nd')]; WTAG[i] = t

lat0, lon0 = NODE[STATION_AVAL]
kx = 111320 * math.cos(math.radians(lat0))
def xy(i): la, lo = NODE[i]; return [round((lo - lon0) * kx, 1), round(-(la - lat0) * 111320, 1)]
def inb(p): return BBOX[0] <= p[0] <= BBOX[1] and BBOX[2] <= p[1] <= BBOX[3]
def pts(w): return [xy(i) for i in WAY[w] if i in NODE]
def src(w): return 'w' + w
dist = lambda a, b: math.hypot(b[0] - a[0], b[1] - a[1])

# ── circuit du câble : brin montant (way OSM, sens aval -> amont), poulie amont, brin descendant décalé, poulie aval
A = pts(LIFT)
if dist(A[0], [0, 0]) > dist(A[-1], [0, 0]): A.reverse()
def resample(P, step):
    out = [P[0]]; acc = 0.0; need = step
    for a, b in zip(P, P[1:]):
        d = dist(a, b)
        while acc + d >= need:
            t = (need - acc) / d; out.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]); need += step
        acc += d
    if dist(out[-1], P[-1]) > 1: out.append(P[-1])
    return out
def unit(a, b): d = dist(a, b) or 1; return [(b[0] - a[0]) / d, (b[1] - a[1]) / d]
u0 = unit(A[0], A[1])
A = [[A[0][0] - u0[0] * 8, A[0][1] - u0[1] * 8]] + A      # prolongement de 8 m en arrière : place de la poulie aval (ESTIMÉ)
# gare : droite st0 -> st1 dans l'axe du premier tronçon (le tracé OSM, lissé, n'est droit qu'approximativement)
R = resample(A, 12.0)
top = R[-1]; ut = unit(R[-2], R[-1])
tot = sum(dist(a, b) for a, b in zip(R, R[1:]))
def normale(P, i):
    a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]; u = unit(a, b); return [u[1], -u[0]]   # à droite du sens de marche (x est, z sud)
cps = []; s = 0.0
def h_au(s): return round(H_CABLE + DENIVELE * max(0.0, s - 8) / max(1.0, tot - 8), 2)  # ESTIMÉ : profil linéaire entre les gares
st1_fait = lift0_fait = False
cum = 0.0
for i, p in enumerate(R):
    if i: cum += dist(R[i - 1], p)
    tg = []
    if i == 0: pass
    cps.append([round(p[0], 2), h_au(cum), round(p[1], 2), 0] + tg)
# repères : st0 au 2e point (début de gare), st1 ~18 m plus loin, lift0 un point après, lift1 au dernier point du brin montant
def idx_at(d):
    c = 0.0
    for i in range(1, len(R)):
        c += dist(R[i - 1], R[i])
        if c >= d: return i
    return len(R) - 1
i_st0 = 1; i_st1 = idx_at(8 + ST_LEN); i_l0 = i_st1 + 1; i_l1 = len(R) - 1
cps[i_st0].append('st0'); cps[i_st1].append('st1'); cps[i_l0].append('lift0'); cps[i_l1].append('lift1')
# poulie amont : demi-cercle de rayon RAYON (ESTIMÉ), de l'axe montant vers l'axe descendant (écart ECART)
n_t = [ut[1], -ut[0]]; h_top = cps[-1][1]; r = ECART / 2
cx, cz = top[0] + n_t[0] * r, top[1] + n_t[1] * r
for k in range(1, 4):
    a = math.pi * k / 4
    x = cx + (-n_t[0]) * r * math.cos(a) + ut[0] * r * math.sin(a)
    z = cz + (-n_t[1]) * r * math.cos(a) + ut[1] * r * math.sin(a)
    cps.append([round(x, 2), h_top, round(z, 2), 0])
# brin descendant : mêmes points décalés de ECART à droite, parcourus en sens inverse
D = []
for i, p in enumerate(R):
    n = normale(R, i); D.append([p[0] + n[0] * ECART, p[1] + n[1] * ECART, cps[i][1]])
for p in reversed(D[:-1]):
    cps.append([round(p[0], 2), p[2], round(p[1], 2), 0])
# repères du moteur 0.0.1 (zone de freinage final avant la gare) : le moteur en exige un ; ici sur la fin du brin descendant (ESTIMÉ, sans objet pour un télésiège)
cps[-3].append('brk'); cps[-1].append('fin')
# poulie aval : fermeture de la boucle derrière la gare (le point 0 est le début du brin montant)
u = unit(R[0], R[1]); n0 = normale(R, 0)
cps.append([round(R[0][0] + n0[0] * ECART / 2 - u[0] * 1.6, 2), cps[0][1], round(R[0][1] + n0[1] * ECART / 2 - u[1] * 1.6, 2), 0])
print('cps %d points, brin montant %.0f m (OSM : 1367 m ; prolongement de 8 m en plus)' % (len(cps), tot - 8))

# ── décor
KEYS = ('building', 'highway', 'natural', 'landuse', 'leisure', 'water', 'waterway', 'barrier', 'amenity', 'tourism', 'man_made')
CLASSE_RENDU = {'highway=path': 'highway=footway', 'highway=cycleway': 'highway=footway', 'highway=residential': 'highway=service',
                'highway=tertiary': 'highway=service', 'highway=secondary': 'highway=service', 'highway=living_street': 'highway=service',
                'highway=pedestrian': 'highway=footway', 'natural=bare_rock': 'natural=rock', 'natural=scree': 'natural=rock', 'natural=grassland': 'landuse=grass'}
feats = []; pistes = []; lifts = []; pylons = []; trees = []
for w, t in WTAG.items():
    p = pts(w)
    if len(p) < 2 or not any(inb(q) for q in p): continue
    if 'piste:type' in t:
        pistes.append({'t': t['piste:type'], 'd': t.get('piste:difficulty'), 'n': t.get('name') or t.get('piste:name'), 'ref': t.get('piste:ref'),
                       'c': 1 if WAY[w][0] == WAY[w][-1] and len(p) > 3 else 0, 'p': p, 'id': src(w), 'v': VER['w' + w]}); continue
    if 'aerialway' in t and t['aerialway'] not in ('station', 'pylon') and w != LIFT:
        lifts.append({'n': t.get('name'), 't': t['aerialway'], 'p': p, 'id': src(w), 'v': VER['w' + w]}); continue
    if w == LIFT: continue
    kind = next((k + '=' + t[k] for k in KEYS if k in t), None)
    if not kind or kind in ('landuse=winter_sports',): continue
    kind = CLASSE_RENDU.get(kind, kind)
    closed = WAY[w][0] == WAY[w][-1] and len(p) > 3
    if kind.startswith('highway=') and kind not in ('highway=footway', 'highway=service', 'highway=steps', 'highway=track', 'highway=unclassified'): continue
    f = {'k': kind, 'n': t.get('name'), 'c': 1 if closed else 0, 'p': p, 'id': src(w), 'v': VER['w' + w]}
    if kind.startswith('building'):
        for kk, m in (('height', 1), ('building:levels', 3)):
            try: f['bh'] = round(float(t[kk].replace(',', '.').replace('m', '')) * m, 1); break
            except (KeyError, ValueError): pass
    feats.append(f)
for i, t in NTAG.items():
    if i not in NODE: continue
    q = xy(i)
    if not inb(q): continue
    if t.get('natural') == 'tree': trees.append(q)
    if t.get('aerialway') == 'pylon': pylons.append(q)
poly = pts(BLD_AVAL)
nom = lambda l: sorted(l, key=lambda f: (f['k'], f['id']))
res = {'cps': cps, 'feats': nom(feats), 'others': [], 'paths': {}, 'polys': {'station': poly}, 'trees': trees,
       'pois': [[xy(i), t['name'], 'n' + i] for i, t in NTAG.items() if t.get('name') and i in NODE and inb(xy(i)) and t.get('aerialway') != 'station'][:40],
       'pylons': pylons, 'lifts': lifts, 'pistes': sorted(pistes, key=lambda x: x['id']),
       'origin': [lat0, lon0], 'ele': None, 'src': {'track': [src(LIFT)]}}
print('décor %d, pistes %d, autres remontées %d, pylônes %d, arbres %d' % (len(feats), len(pistes), len(lifts), len(pylons), len(trees)))
en_tete = ("/* Données © contributeurs OpenStreetMap (ODbL) — Escondus V15 (way %s), Vars Les Claux. Généré par tools/make_ski.py (API api.openstreetmap.org). "
           "ESTIMÉ : hauteur du câble et dénivelé (%d m, aucun « ele » dans OSM), écart des deux brins (%.1f m), poulies, longueur de gare (%d m). */\n" % (LIFT, DENIVELE, ECART, ST_LEN))
os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
with open(SORTIE, 'w', encoding='utf-8') as o:
    o.write(en_tete + 'const OSM=' + json.dumps(res, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('écrit', SORTIE, os.path.getsize(SORTIE), 'octets')
