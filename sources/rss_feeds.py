"""Surveillance des flux RSS des médias suisses pour les mentions CDF/EFK."""

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser


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


def _parse_date(entry) -> datetime | None:
    """Tente d'extraire une datetime depuis un entry RSS."""
    for field in ("published", "updated"):
        raw = entry.get(field)
        if not raw:
            continue
        try:
            return parsedate_to_datetime(raw).astimezone(timezone.utc)
        except Exception:
            pass
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            pass
    return None


def check_rss(feeds: dict[str, str], keywords: list[str], since: datetime) -> list[dict]:
    """
    Parcourt les flux RSS et détecte les articles contenant les mots-clés.

    Args:
        feeds: Dict {nom_du_média: url_du_flux}
        keywords: Liste de mots-clés
        since: Ne retourner que les articles après cette date

    Returns:
        Liste de mentions avec métadonnées
    """
    pattern = _build_pattern(keywords)
    results = []
    seen_ids = set()

    for name, url in feeds.items():
        print(f"  📰 RSS: {name}...")
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                print(f"     ⚠️  Flux inaccessible ou invalide")
                continue

            for entry in feed.entries:
                # Texte à analyser : titre + résumé
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                content = f"{title} {summary}"

                if not pattern.search(content):
                    continue

                # Vérifier la date
                pub_date = _parse_date(entry)
                if pub_date and pub_date <= since:
                    continue

                link = entry.get("link", "")
                entry_id = f"rss_{name}_{entry.get('id', link)}"

                if entry_id in seen_ids:
                    continue
                seen_ids.add(entry_id)

                found_keywords = list(set(pattern.findall(content)))

                results.append(
                    {
                        "source": "rss",
                        "channel": name,
                        "text": f"{title}\n{summary[:300]}".strip(),
                        "url": link,
                        "msg_id": entry_id,
                        "keywords": found_keywords,
                        "timestamp": (
                            pub_date.isoformat()
                            if pub_date
                            else datetime.now(timezone.utc).isoformat()
                        ),
                    }
                )

        except Exception as e:
            print(f"     ⚠️  Erreur {name}: {e}")

    if results:
        print(f"     → {len(results)} mention(s) trouvée(s) au total")

    return results
