#!/usr/bin/env python3
"""CDF/EFK Monitor — Surveille les mentions du CDF sur Telegram et Reddit."""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from config import KEYWORDS, TELEGRAM_CHANNELS, REDDIT_SUBREDDITS, RSS_FEEDS
from sources.telegram import check_telegram
from sources.reddit import check_reddit
from sources.rss_feeds import check_rss
from notifier import send_alert

STATE_FILE = Path(__file__).parent / "data" / "state.json"


def load_state() -> dict:
    """Charge l'état de la dernière vérification."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "last_check": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "seen_ids": [],
    }


def save_state(state: dict):
    """Sauvegarde l'état courant."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    print("🔎 CDF/EFK Monitor — Démarrage")
    print(f"   Heure: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    state = load_state()
    since = datetime.fromisoformat(state["last_check"])
    seen_ids = set(state.get("seen_ids", []))

    print(f"   Dernière vérification: {since.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Mots-clés: {', '.join(KEYWORDS)}")
    print()

    all_mentions = []

    # --- Telegram ---
    if TELEGRAM_CHANNELS:
        print("📡 Vérification Telegram...")
        tg = check_telegram(TELEGRAM_CHANNELS, KEYWORDS, since)
        all_mentions.extend(tg)
    else:
        print("📡 Telegram: aucun channel configuré")

    # --- RSS Médias suisses ---
    if RSS_FEEDS:
        print("\n📰 Vérification flux RSS...")
        rss = check_rss(RSS_FEEDS, KEYWORDS, since)
        all_mentions.extend(rss)

    # --- Reddit ---
    if REDDIT_SUBREDDITS:
        print("\n🔍 Vérification Reddit...")
        rd = check_reddit(REDDIT_SUBREDDITS, KEYWORDS, since)
        all_mentions.extend(rd)

    # Filtrer les doublons déjà vus
    new_mentions = [m for m in all_mentions if m["msg_id"] not in seen_ids]

    print(f"\n📊 Résultat: {len(new_mentions)} nouvelle(s) mention(s)")

    if new_mentions:
        for m in new_mentions:
            print(f"   • [{m['source']}] {m['channel']}: {m['text'][:80]}...")

        print("\n📤 Envoi de l'alerte Threema...")
        send_alert(new_mentions)

        for m in new_mentions:
            seen_ids.add(m["msg_id"])
    else:
        print("   Rien de nouveau.")

    # Sauvegarder l'état (garder les 1000 derniers IDs)
    state = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "seen_ids": list(seen_ids)[-1000:],
    }
    save_state(state)

    print("\n✅ Terminé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
