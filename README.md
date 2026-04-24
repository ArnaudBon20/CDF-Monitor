# CDF/EFK Monitor

Système d'alerte personnel qui surveille les mentions du **Contrôle fédéral des finances (CDF/EFK)** sur Telegram et Reddit, et envoie des notifications via **Threema Gateway**.

## Sources surveillées

| Source | Méthode | Authentification |
|--------|---------|------------------|
| **Telegram** (5 channels) | Scraping des previews web (`t.me/s/channel`) | Aucune (channels publics) |
| **RSS** (8 flux) | Parsing des flux RSS médias suisses | Aucune |
| **Reddit** (4 subreddits) | API via PRAW | Client ID + Secret |

### Détail des sources

**Telegram** : swissinfofrench, swissinfoenglish, nebelspalterOnline, insideparadeplatz, schweizermonat

**RSS** : SRF News Schweiz, SRF Wirtschaft, NZZ Schweiz, NZZ Wirtschaft, NZZ Finanzen, Blick Politik, Blick News, Le Temps

**Reddit** : r/Switzerland, r/suisse, r/schweiz, r/SwissPolitics

## Fonctionnement

1. Le script s'exécute toutes les 30 min via GitHub Actions (8h–00h heure suisse)
2. Il scrape les channels Telegram publics et recherche sur Reddit
3. Les mentions contenant les mots-clés configurés sont détectées
4. Si de nouvelles mentions sont trouvées → alerte Threema
5. L'état (dernière vérification, IDs déjà vus) est persisté dans `data/state.json`

## Configuration

### Mots-clés et sources

Éditer `config.py` pour ajuster :
- `KEYWORDS` — mots-clés recherchés
- `TELEGRAM_CHANNELS` — channels Telegram publics à surveiller
- `REDDIT_SUBREDDITS` — subreddits à surveiller

### GitHub Secrets requis

| Secret | Description |
|--------|-------------|
| `THREEMA_GATEWAY_ID` | ID du Gateway Threema (ex: `*EFKCDF6`) |
| `THREEMA_GATEWAY_SECRET` | Secret du Gateway |
| `THREEMA_RECIPIENT_ID` | Ton ID Threema personnel |
| `REDDIT_CLIENT_ID` | Client ID de l'app Reddit |
| `REDDIT_CLIENT_SECRET` | Client Secret de l'app Reddit |

### Créer une app Reddit

1. Aller sur https://www.reddit.com/prefs/apps/
2. Cliquer "create another app..."
3. Choisir **script**
4. Nom : `CDF-Monitor`
5. Redirect URI : `http://localhost:8080`
6. Copier le **client ID** (sous le nom de l'app) et le **secret**

## Exécution locale

```bash
cd CDF-Monitor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Remplir les valeurs
export $(cat .env | xargs)
python monitor.py
```

## Structure

```
├── monitor.py              # Script principal
├── config.py               # Mots-clés, channels, subreddits
├── notifier.py             # Envoi Threema Gateway
├── sources/
│   ├── telegram.py         # Scraping channels Telegram publics
│   └── reddit.py           # Recherche Reddit via PRAW
├── data/
│   └── state.json          # État persisté (dernière vérif, IDs vus)
├── .github/workflows/
│   └── monitor.yml         # GitHub Actions (cron 30 min)
├── requirements.txt
└── .env.example
```
