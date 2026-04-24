"""Surveillance de Reddit pour les mentions CDF/EFK."""

import os
from datetime import datetime, timezone

import praw


def check_reddit(
    subreddits: list[str], keywords: list[str], since: datetime
) -> list[dict]:
    """
    Recherche des mentions dans les subreddits configurés via l'API Reddit.

    Args:
        subreddits: Liste de noms de subreddits
        keywords: Liste de mots-clés
        since: Ne retourner que les posts après cette date

    Returns:
        Liste de mentions avec métadonnées
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("  ⚠️  Reddit: credentials manquants (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")
        return []

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="CDF-Monitor/1.0 (monitoring Swiss Federal Audit Office mentions)",
    )

    results = []
    seen_ids = set()
    since_ts = since.timestamp()

    for sub_name in subreddits:
        print(f"  🔍 Reddit: r/{sub_name}...")
        try:
            subreddit = reddit.subreddit(sub_name)

            for keyword in keywords:
                for post in subreddit.search(
                    keyword, sort="new", time_filter="day", limit=25
                ):
                    if post.created_utc <= since_ts:
                        continue

                    post_id = f"reddit_{post.id}"
                    if post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)

                    body = (post.selftext or "")[:300]
                    results.append(
                        {
                            "source": "reddit",
                            "channel": f"r/{sub_name}",
                            "text": f"{post.title}\n{body}".strip(),
                            "url": f"https://reddit.com{post.permalink}",
                            "msg_id": post_id,
                            "keywords": [keyword],
                            "timestamp": datetime.fromtimestamp(
                                post.created_utc, tz=timezone.utc
                            ).isoformat(),
                        }
                    )

        except Exception as e:
            print(f"    ⚠️  Erreur r/{sub_name}: {e}")

    if results:
        print(f"     → {len(results)} mention(s) trouvée(s) au total")

    return results
