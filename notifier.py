"""Envoi d'alertes via Threema Gateway."""

import os

import requests


def format_message(mentions: list[dict]) -> str:
    """Formate les mentions en message lisible pour Threema."""
    from datetime import datetime, timezone, timedelta

    n = len(mentions)
    tz_ch = timezone(timedelta(hours=2))
    now = datetime.now(tz_ch)
    timestamp = now.strftime("%d.%m.%Y %H:%M")

    source_emoji = {"telegram": "📡", "rss": "📰", "reddit": "🟠"}
    source_label = {"telegram": "Telegram", "rss": "Médias", "reddit": "Reddit"}

    # Header compact
    lines = [
        f"🔔 ALERTE CDF — {timestamp}",
        f"{n} mention{'s' if n > 1 else ''} détectée{'s' if n > 1 else ''}",
        "",
    ]

    # Regrouper par source
    by_source = {}
    for m in mentions[:10]:
        src = m["source"]
        by_source.setdefault(src, []).append(m)

    for src in ["rss", "telegram", "reddit"]:
        items = by_source.get(src, [])
        if not items:
            continue

        emoji = source_emoji.get(src, "•")
        label = source_label.get(src, src)

        lines.append(f"── {emoji} {label} ({len(items)}) ──")
        lines.append("")

        for m in items:
            # Extraire le titre (première ligne du texte)
            text_lines = m["text"].split("\n", 1)
            title = text_lines[0].strip()[:120]

            # Heure de la mention
            time_str = ""
            if m.get("timestamp"):
                try:
                    dt = datetime.fromisoformat(m["timestamp"]).astimezone(tz_ch)
                    time_str = dt.strftime("%H:%M")
                except (ValueError, TypeError):
                    pass

            # Ligne principale
            header = f"▸ {m['channel']}"
            if time_str:
                header += f" • {time_str}"
            lines.append(header)
            lines.append(f"  {title}")
            if m.get("url"):
                lines.append(f"  → {m['url']}")
            lines.append("")

    if len(mentions) > 10:
        lines.append(f"… +{len(mentions) - 10} autre(s)")
        lines.append("")

    return "\n".join(lines).rstrip()


def send_alert(mentions: list[dict]) -> bool:
    """
    Envoie un résumé des mentions via Threema Gateway.

    Returns:
        True si le message a été envoyé avec succès
    """
    gateway_id = os.environ.get("THREEMA_GATEWAY_ID")
    gateway_secret = os.environ.get("THREEMA_GATEWAY_SECRET")
    recipient_id = os.environ.get("THREEMA_RECIPIENT_ID")

    if not all([gateway_id, gateway_secret, recipient_id]):
        print("❌ Variables Threema manquantes (THREEMA_GATEWAY_ID, THREEMA_GATEWAY_SECRET, THREEMA_RECIPIENT_ID)")
        return False

    message = format_message(mentions)

    try:
        resp = requests.post(
            "https://msgapi.threema.ch/send_simple",
            data={
                "from": gateway_id,
                "to": recipient_id,
                "secret": gateway_secret,
                "text": message,
            },
            timeout=30,
        )

        if resp.status_code == 200:
            print(f"✅ Alerte envoyée via Threema (ID: {resp.text.strip()})")
            return True
        else:
            print(f"❌ Erreur Threema: {resp.status_code} — {resp.text}")
            return False

    except requests.RequestException as e:
        print(f"❌ Erreur envoi Threema: {e}")
        return False
