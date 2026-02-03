"""
Fetch NBA pre-game odds from The Odds API and cache them.
Run daily before games start (e.g., UTC 10:00 / Taiwan 18:00).
"""
import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()


# NBA team name to tricode mapping
TEAM_TRICODES = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS",
}


def get_tricode(team_name: str) -> str:
    """Get team tricode from full name."""
    return TEAM_TRICODES.get(team_name, team_name[:3].upper())


def fetch_odds():
    """Fetch today's NBA odds and cache them."""
    api_key = os.environ.get("THE_ODDS_API_KEY")
    if not api_key:
        print("THE_ODDS_API_KEY not set")
        return

    base_dir = Path(__file__).parent.parent
    taiwan_tz = timezone(timedelta(hours=8))
    now = datetime.now(taiwan_tz)
    day = now.strftime("%d")

    # Fetch odds from The Odds API
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
    }

    print(f"Fetching NBA odds for {now.strftime('%Y-%m-%d')}...")
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"API error: {response.status_code} - {response.text}")
        return

    games = response.json()
    print(f"Found {len(games)} upcoming games")

    # Process and cache odds
    odds_data = {
        "date": now.strftime("%Y-%m-%d"),
        "fetched": now.strftime("%Y-%m-%d %H:%M"),
        "games": [],
    }

    for game in games:
        game_info = {
            "id": game["id"],
            "home_team": game["home_team"],
            "away_team": game["away_team"],
            "home_tricode": get_tricode(game["home_team"]),
            "away_tricode": get_tricode(game["away_team"]),
            "commence_time": game["commence_time"],
            "home_odds": None,
            "away_odds": None,
        }

        # Extract h2h odds from first bookmaker
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == game["home_team"]:
                            game_info["home_odds"] = outcome["price"]
                        elif outcome["name"] == game["away_team"]:
                            game_info["away_odds"] = outcome["price"]
                    break
            if game_info["home_odds"] is not None:
                break

        odds_data["games"].append(game_info)
        print(
            f"  {game_info['away_tricode']} @ {game_info['home_tricode']}: "
            f"{game_info['away_odds']} / {game_info['home_odds']}"
        )

    # Save to odds_cache/odds_DD.json
    cache_dir = base_dir / "odds_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"odds_{day}.json"

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(odds_data, f, ensure_ascii=False, indent=2)

    print(f"Saved odds to {cache_path}")

    # Show remaining API credits
    remaining = response.headers.get("x-requests-remaining")
    used = response.headers.get("x-requests-used")
    print(f"API credits: {remaining} remaining, {used} used")


if __name__ == "__main__":
    fetch_odds()
