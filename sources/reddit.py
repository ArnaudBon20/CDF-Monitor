"""Surveillance de Reddit pour les mentions CDF/EFK via JSON public (sans API key)."""

import re
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests


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


def check_reddit(
    subreddits: list[str], keywords: list[str], since: datetime
) -> list[dict]:
    """
    Recherche des mentions dans les subreddits via les endpoints JSON publics.
    Ne nécessite aucune API key ni credentials Reddit.

    Args:
        subreddits: Liste de noms de subreddits
        keywords: Liste de mots-clés
        since: Ne retourner que les posts après cette date

    Returns:
        Liste de mentions avec métadonnées
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CDF-Monitor/1.0)",
    }
    pattern = _build_pattern(keywords)
    results = []
    seen_ids = set()
    since_ts = since.timestamp()

    for sub_name in subreddits:
        print(f"  🔍 Reddit: r/{sub_name}...")

        for keyword in keywords:
            url = (
                f"https://www.reddit.com/r/{sub_name}/search.json"
                f"?q={quote_plus(keyword)}&restrict_sr=on&sort=new&t=day&limit=25"
            )

            try:
                resp = requests.get(url, headers=headers, timeout=15)

                if resp.status_code == 429:
                    print(f"     ⚠️  Rate limited, pause 5s...")
                    time.sleep(5)
                    resp = requests.get(url, headers=headers, timeout=15)

                if resp.status_code != 200:
                    print(f"     ⚠️  HTTP {resp.status_code} pour r/{sub_name} ({keyword})")
                    continue

                data = resp.json()
                posts = data.get("data", {}).get("children", [])

                for item in posts:
                    post = item.get("data", {})
                    created = post.get("created_utc", 0)

                    if created <= since_ts:
                        continue

                    post_id = f"reddit_{post.get('id', '')}"
                    if post_id in seen_ids:
                        continue

                    title = post.get("title", "")
                    body = (post.get("selftext") or "")[:300]
                    content = f"{title} {body}"

                    if not pattern.search(content):
                        continue

                    seen_ids.add(post_id)
                    found_keywords = list(set(pattern.findall(content)))
                    permalink = post.get("permalink", "")

                    results.append(
                        {
                            "source": "reddit",
                            "channel": f"r/{sub_name}",
                            "text": f"{title}\n{body}".strip(),
                            "url": f"https://reddit.com{permalink}",
                            "msg_id": post_id,
                            "keywords": found_keywords,
                            "timestamp": datetime.fromtimestamp(
                                created, tz=timezone.utc
                            ).isoformat(),
                        }
                    )

            except Exception as e:
                print(f"     ⚠️  Erreur r/{sub_name} ({keyword}): {e}")

            time.sleep(1)

    if results:
        print(f"     → {len(results)} mention(s) trouvée(s) au total")

    return results
