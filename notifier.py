"""Envoi d'alertes via Threema Gateway."""

import os

import requests


def format_message(mentions: list[dict]) -> str:
    """Formate les mentions en message lisible pour Threema."""
    n = len(mentions)
    lines = [f"🔔 *CDF/EFK Monitor*"]
    lines.append(f"_{n} nouvelle{'s' if n > 1 else ''} mention{'s' if n > 1 else ''}_")

    for i, m in enumerate(mentions[:10]):
        emoji = {"telegram": "📡", "rss": "📰", "reddit": "🔍"}.get(m["source"], "•")
        preview = m["text"][:200].replace("\n", " ").strip()

        lines.append("")
        lines.append(f"{emoji} *{m['channel']}*")
        lines.append("")
        lines.append(preview)
        if m.get("url"):
            lines.append("")
            lines.append(f"🔗 {m['url']}")

        if i < min(len(mentions), 10) - 1:
            lines.append("")
            lines.append("─ ─ ─ ─ ─ ─ ─ ─ ─ ─")

    if len(mentions) > 10:
        lines.append("")
        lines.append(f"⋯ +{len(mentions) - 10} autre{'s' if len(mentions) - 10 > 1 else ''}")

    return "\n".join(lines)


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
