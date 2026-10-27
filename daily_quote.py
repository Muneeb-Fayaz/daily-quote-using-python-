"""Daily Quote - shows one quote per day using the free DummyJSON fake quotes API.

Usage:
    python daily_quote.py           # today's quote (same all day)
    python daily_quote.py --random  # a new random quote each run
"""

import argparse
import json
import random
from datetime import date
from pathlib import Path

import requests

API_URL = "https://dummyjson.com/quotes"
CACHE_FILE = Path(__file__).with_name("quote_cache.json")

# Used only if the API is unreachable
FALLBACK_QUOTES = [
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "Well done is better than well said.", "author": "Benjamin Franklin"},
    {"quote": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"quote": "Start where you are. Use what you have. Do what you can.", "author": "Arthur Ashe"},
    {"quote": "Dreams don't work unless you do.", "author": "John C. Maxwell"},
]


def fetch_all_quotes():
    """Download the full quote list from the API."""
    response = requests.get(API_URL, params={"limit": 0}, timeout=10)
    response.raise_for_status()
    return response.json()["quotes"]


def fetch_random_quote():
    response = requests.get(f"{API_URL}/random", timeout=10)
    response.raise_for_status()
    return response.json()


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def get_daily_quote():
    """Return the same quote for the whole day, cached on disk."""
    today = date.today().isoformat()
    cache = load_cache()
    if cache.get("date") == today:
        return cache["quote"]

    try:
        quotes = fetch_all_quotes()
    except requests.RequestException:
        quotes = FALLBACK_QUOTES

    # Deterministic pick: the date number selects the quote
    quote = quotes[date.today().toordinal() % len(quotes)]
    CACHE_FILE.write_text(
        json.dumps({"date": today, "quote": quote}, ensure_ascii=False),
        encoding="utf-8",
    )
    return quote


def show(quote):
    print()
    print(f"  \"{quote['quote']}\"")
    print(f"      - {quote['author']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Daily quote from a fake quotes API")
    parser.add_argument("--random", action="store_true", help="show a random quote instead")
    args = parser.parse_args()

    if args.random:
        try:
            quote = fetch_random_quote()
        except requests.RequestException:
            quote = random.choice(FALLBACK_QUOTES)
    else:
        quote = get_daily_quote()

    print(f"Quote for {date.today():%A, %d %B %Y}")
    show(quote)


if __name__ == "__main__":
    main()
