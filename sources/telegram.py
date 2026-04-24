"""Surveillance des channels Telegram publics pour les mentions CDF/EFK."""

import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


def _build_pattern(keywords: list[str]) -> re.Pattern:
    """Construit un regex avec word boundary pour les mots courts."""
    parts = []
    for kw in keywords:
        escaped = re.escape(kw)
        if len(kw) <= 4:
            parts.append(rf"\b{escaped}\b")
        else:
            parts.append(escaped)
    return re.compile("|".join(parts), re.IGNORECASE)


def scrape_channel(channel_name: str, keywords: list[str], since: datetime) -> list[dict]:
    """
    Scrape la prévisualisation web d'un channel Telegram public.

    Args:
        channel_name: Nom du channel (sans @)
        keywords: Liste de mots-clés
        since: Ne retourner que les messages après cette date

    Returns:
        Liste de mentions avec métadonnées
    """
    url = f"https://t.me/s/{channel_name}"

    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CDF-Monitor/1.0)"},
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ⚠️  Erreur accès {channel_name}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    messages = soup.select(".tgme_widget_message_wrap")
    pattern = _build_pattern(keywords)
    results = []

    for msg in messages:
        text_el = msg.select_one(".tgme_widget_message_text")
        if not text_el:
            continue
        text = text_el.get_text(strip=True)

        if not pattern.search(text):
            continue

        # Date du message
        time_el = msg.select_one(".tgme_widget_message_date time")
        msg_time = None
        if time_el and time_el.get("datetime"):
            msg_time = datetime.fromisoformat(
                time_el["datetime"].replace("Z", "+00:00")
            )
            if msg_time <= since:
                continue

        # ID du message
        link_el = msg.select_one(".tgme_widget_message_date")
        msg_id = ""
        if link_el and link_el.get("href"):
            msg_id = link_el["href"].split("/")[-1]

        found_keywords = list(set(pattern.findall(text)))

        results.append(
            {
                "source": "telegram",
                "channel": f"@{channel_name}",
                "text": text[:500],
                "url": f"https://t.me/{channel_name}/{msg_id}" if msg_id else url,
                "msg_id": f"tg_{channel_name}_{msg_id}",
                "keywords": found_keywords,
                "timestamp": (
                    msg_time.isoformat()
                    if msg_time
                    else datetime.now(timezone.utc).isoformat()
                ),
            }
        )

    return results


def check_telegram(
    channels: list[str], keywords: list[str], since: datetime
) -> list[dict]:
    """Vérifie tous les channels Telegram configurés."""
    all_results = []
    for channel in channels:
        print(f"  📡 Telegram: @{channel}...")
        results = scrape_channel(channel, keywords, since)
        all_results.extend(results)
        if results:
            print(f"     → {len(results)} mention(s) trouvée(s)")
    return all_results
