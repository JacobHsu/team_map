"""
Analyze NBA game results and identify upsets using The Odds API.
Compares completed game scores with cached pre-game odds.
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


def is_underdog(odds: int) -> bool:
    """Check if odds indicate underdog (positive American odds)."""
    return odds > 0


def determine_upset(winner_odds: int, loser_odds: int) -> bool:
    """
    Determine if the result is an upset.
    An upset occurs when the underdog (positive odds) beats the favorite (negative odds).
    """
    # Classic upset: underdog (positive) beats favorite (negative)
    if winner_odds > 0 and loser_odds < 0:
        return True
    # Both negative: winner had higher (less negative) odds = subtle underdog
    if winner_odds < 0 and loser_odds < 0 and winner_odds > loser_odds:
        return True
    # Both positive: winner had higher odds = underdog
    if winner_odds > 0 and loser_odds > 0 and winner_odds > loser_odds:
        return True
    return False


def analyze_odds():
    """Fetch game results and compare with cached odds to identify upsets."""
    api_key = os.environ.get("THE_ODDS_API_KEY")
    if not api_key:
        print("THE_ODDS_API_KEY not set")
        return

    base_dir = Path(__file__).parent.parent
    taiwan_tz = timezone(timedelta(hours=8))
    now = datetime.now(taiwan_tz)
    day = now.strftime("%d")

    # Load cached odds from previous day (when odds were fetched)
    # Analysis runs the next day at 15:00 TW time
    prev_day = (now - timedelta(days=1)).strftime("%d")
    cache_dir = base_dir / "odds_cache"
    cache_path = cache_dir / f"odds_{prev_day}.json"

    if not cache_path.exists():
        print(f"No odds cache found: {cache_path}")
        print("Run fetch_odds.py first to cache pre-game odds.")
        return

    with open(cache_path, "r", encoding="utf-8") as f:
        odds_data = json.load(f)

    print(f"Loaded odds cache: {odds_data['date']} ({len(odds_data['games'])} games)")

    # Build lookup by game ID
    odds_lookup = {g["id"]: g for g in odds_data["games"]}

    # Fetch completed game scores
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/scores"
    params = {
        "apiKey": api_key,
        "daysFrom": 1,
    }

    print("Fetching game scores...")
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"API error: {response.status_code} - {response.text}")
        return

    scores = response.json()
    completed = [g for g in scores if g.get("completed")]
    print(f"Found {len(completed)} completed games")

    # Analyze each completed game
    upsets = []
    total_games = 0

    for game in completed:
        game_id = game["id"]
        cached = odds_lookup.get(game_id)

        if not cached:
            print(f"  Skipping {game['away_team']} @ {game['home_team']} - no cached odds")
            continue

        # Get scores
        scores_map = {}
        for score in game.get("scores", []):
            scores_map[score["name"]] = int(score["score"])

        home_score = scores_map.get(game["home_team"], 0)
        away_score = scores_map.get(game["away_team"], 0)

        if home_score == 0 and away_score == 0:
            print(f"  Skipping {game['away_team']} @ {game['home_team']} - no scores")
            continue

        total_games += 1

        # Determine winner
        if home_score > away_score:
            winner = game["home_team"]
            winner_score = home_score
            winner_odds = cached["home_odds"]
            loser = game["away_team"]
            loser_score = away_score
            loser_odds = cached["away_odds"]
        else:
            winner = game["away_team"]
            winner_score = away_score
            winner_odds = cached["away_odds"]
            loser = game["home_team"]
            loser_score = home_score
            loser_odds = cached["home_odds"]

        winner_tricode = get_tricode(winner)
        loser_tricode = get_tricode(loser)

        print(
            f"  {winner_tricode} {winner_score} - {loser_score} {loser_tricode} "
            f"(odds: {winner_odds} vs {loser_odds})"
        )

        # Check if upset
        if winner_odds is not None and loser_odds is not None:
            if determine_upset(winner_odds, loser_odds):
                upsets.append({
                    "winner_tricode": winner_tricode,
                    "winner": winner,
                    "winner_score": winner_score,
                    "winner_odds": winner_odds,
                    "loser_tricode": loser_tricode,
                    "loser": loser,
                    "loser_score": loser_score,
                    "loser_odds": loser_odds,
                })
                print(f"    ^ UPSET!")

    # Build output data
    upset_rate = round(len(upsets) / total_games * 100, 2) if total_games > 0 else 0
    output_data = {
        "total_games": total_games,
        "upset_count": len(upsets),
        "upset_rate": upset_rate,
        "upsets": upsets,
        "date": now.strftime("%Y-%m-%d"),
        "updated": now.strftime("%Y-%m-%d %H:%M"),
    }

    # Save to upsets/upsets_DD.json
    output_dir = base_dir / "upsets"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"upsets_{day}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {output_path}")
    print(f"Total: {total_games} games, {len(upsets)} upsets ({upset_rate}%)")

    # Show remaining API credits
    remaining = response.headers.get("x-requests-remaining")
    used = response.headers.get("x-requests-used")
    print(f"API credits: {remaining} remaining, {used} used")


if __name__ == "__main__":
    analyze_odds()
