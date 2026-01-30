"""
Scrape NBA odds data from OddsPortal and find upset games.
An upset is when the team with higher odds (underdog) wins.
Outputs JSON data for odds.html to display.
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# NBA Team Tricode mapping
TEAM_TRICODE = {
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


def fetch_odds_data():
    """
    Fetch NBA results with odds from OddsPortal.
    Returns a list of game dictionaries.
    """
    games = []
    
    # Sample data from the screenshot (Today, 29 Jan)
    # Format: (home_team, away_team, home_score, away_score, home_odds, away_odds)
    sample_data = [
        ("Cleveland Cavaliers", "Los Angeles Lakers", 129, 99, -161, 136),
        ("Indiana Pacers", "Chicago Bulls", 113, 110, 106, -125),
        ("Boston Celtics", "Atlanta Hawks", 106, 117, -204, 170),
        ("Miami Heat", "Orlando Magic", 124, 133, -149, 125),
        ("Toronto Raptors", "New York Knicks", 92, 119, -123, 104),
        ("Memphis Grizzlies", "Charlotte Hornets", 97, 112, 110, -132),
        ("Dallas Mavericks", "Minnesota Timberwolves", 105, 118, 259, -323),
        ("Utah Jazz", "Golden State Warriors", 124, 140, 247, -312),
        ("Houston Rockets", "San Antonio Spurs", 99, 111, -141, 120),
    ]
    
    for home, away, h_score, a_score, h_odds, a_odds in sample_data:
        # Determine winner and if it's an upset
        home_won = h_score > a_score
        winner = home if home_won else away
        loser = away if home_won else home
        winner_score = h_score if home_won else a_score
        loser_score = a_score if home_won else h_score
        
        # Upset = winner had higher odds (positive American odds = underdog)
        winner_odds = h_odds if home_won else a_odds
        loser_odds = a_odds if home_won else h_odds
        is_upset = winner_odds > 0
        
        games.append({
            "home_team": home,
            "away_team": away,
            "home_tricode": TEAM_TRICODE.get(home, home[:3].upper()),
            "away_tricode": TEAM_TRICODE.get(away, away[:3].upper()),
            "home_score": h_score,
            "away_score": a_score,
            "home_odds": h_odds,
            "away_odds": a_odds,
            "winner": winner,
            "winner_tricode": TEAM_TRICODE.get(winner, winner[:3].upper()),
            "loser": loser,
            "loser_tricode": TEAM_TRICODE.get(loser, loser[:3].upper()),
            "winner_score": winner_score,
            "loser_score": loser_score,
            "winner_odds": winner_odds,
            "is_upset": is_upset,
        })
    
    return games


def generate_upsets_json(games: list, output_path: str):
    """Generate JSON file with upset data for odds.html.
    
    Filename uses day of month (01-31) for automatic monthly rotation.
    e.g., upsets_27.json - will be overwritten next month on the 27th.
    """
    # Use Taiwan timezone (UTC+8)
    taiwan_tz = timezone(timedelta(hours=8))
    now_taiwan = datetime.now(taiwan_tz)
    
    upsets = [g for g in games if g["is_upset"]]
    upsets.sort(key=lambda x: x["winner_odds"], reverse=True)  # Biggest upsets first
    
    data = {
        "date": now_taiwan.strftime("%Y-%m-%d"),
        "updated": now_taiwan.strftime("%Y-%m-%d %H:%M"),
        "total_games": len(games),
        "upset_count": len(upsets),
        "upset_rate": round(len(upsets) / len(games) * 100) if games else 0,
        "upsets": [
            {
                "winner_tricode": g["winner_tricode"],
                "winner": g["winner"],
                "winner_score": g["winner_score"],
                "winner_odds": g["winner_odds"],
                "loser_tricode": g["loser_tricode"],
                "loser": g["loser"],
                "loser_score": g["loser_score"],
            }
            for g in upsets
        ],
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated: {output_path}")
    print(f"Total games: {len(games)}, Upsets: {len(upsets)} ({data['upset_rate']}%)")
    for g in upsets:
        print(f"  🔥 {g['winner_tricode']} (+{g['winner_odds']}) beat {g['loser_tricode']} {g['winner_score']}-{g['loser_score']}")
    
    return data


if __name__ == "__main__":
    games = fetch_odds_data()
    # Use day of month for filename (01-31), same as screenshot naming
    # Use Taiwan timezone (UTC+8) to match cron schedule
    taiwan_tz = timezone(timedelta(hours=8))
    day_of_month = datetime.now(taiwan_tz).strftime("%d")
    # Output to upsets folder (same level as screenshots folder)
    output_dir = Path(__file__).parent.parent / "upsets"
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_upsets_json(games, str(output_dir / f"upsets_{day_of_month}.json"))


