"""
Scrape NBA odds data from OddsPortal using Jina AI Reader and find upset games.
An upset is when the team with higher odds (underdog) wins.

This script fetches real-time game results and odds from OddsPortal via Jina AI Reader API.
If the API is unavailable or JINA_API_KEY is not set, it falls back to sample data.

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
    Fetch NBA results with odds from OddsPortal using Jina AI Reader.
    Returns a list of game dictionaries.
    """
    import os
    import requests
    import re
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    jina_api_key = os.getenv("JINA_API_KEY")
    
    games = []
    
    try:
        # Use Jina AI Reader to fetch OddsPortal results
        url = "https://www.oddsportal.com/basketball/usa/nba/results/"
        headers = {}
        if jina_api_key:
            headers["Authorization"] = f"Bearer {jina_api_key}"
        
        response = requests.get(f"https://r.jina.ai/{url}", headers=headers, timeout=30)
        response.raise_for_status()
        content = response.text
        
        # Find the "Today" section first (current day's games)
        section_idx = content.find("Today,")
        if section_idx == -1:
            # Fall back to "Yesterday" if no "Today" found
            section_idx = content.find("Yesterday,")
        
        if section_idx != -1:
            # Find the end of this section (next date marker or "Tomorrow")
            section_start = section_idx
            # Look for the next date section to know where to stop
            next_section_patterns = ["Yesterday,", "Tomorrow,", "19 Mar 2026", "01 Apr 2026"]
            section_end = section_start + 20000  # default large value
            
            for pattern in next_section_patterns:
                next_idx = content.find(pattern, section_start + 20)  # +20 to skip current date
                if next_idx != -1 and next_idx < section_end:
                    section_end = next_idx
            
            # Extract only the target date's section
            section = content[section_start:section_end]
            
            # Split into lines for easier processing
            lines = section.split('\n')
            
            # Find all game entries by looking for the pattern:
            # Line with team names and scores, followed by odds
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Look for lines that contain game data with Image markers (team logos)
                # Pattern: [![Image XX: Team1](...) Team1 Score1](...) Score1 [–](...) Score2 [![Image YY: Team2](...) Team2 Score2](...)
                if '[![Image' in line and '–' in line:
                    # Extract team names from Image alt text
                    team_pattern = r'!\[Image\s+\d+:\s+([^\]]+)\]'
                    teams = re.findall(team_pattern, line)
                    
                    # Extract scores - look for pattern "Score1 [–](...) Score2"
                    score_pattern = r'(\d{2,3})\s+\[–\]\([^)]+\)\s+(\d{2,3})'
                    scores = re.findall(score_pattern, line)
                    
                    if len(teams) >= 2 and len(scores) >= 1:
                        team1 = teams[0].strip()
                        team2 = teams[1].strip()
                        score1 = int(scores[0][0])
                        score2 = int(scores[0][1])
                        
                        # Look for odds in the next few lines
                        odds1 = None
                        odds2 = None
                        for j in range(i+1, min(i+10, len(lines))):
                            odds_line = lines[j].strip()
                            # Match odds pattern: +XXX or -XXX
                            if re.match(r'^[+-]\d+$', odds_line):
                                if odds1 is None:
                                    odds1 = int(odds_line)
                                elif odds2 is None:
                                    odds2 = int(odds_line)
                                    break
                        
                        if odds1 is not None and odds2 is not None:
                            # Determine winner and if it's an upset
                            home_won = score1 > score2
                            winner = team1 if home_won else team2
                            loser = team2 if home_won else team1
                            winner_score = score1 if home_won else score2
                            loser_score = score2 if home_won else score1
                            
                            # Upset = winner had higher odds (positive American odds = underdog)
                            winner_odds = odds1 if home_won else odds2
                            loser_odds = odds2 if home_won else odds1
                            is_upset = winner_odds > 0
                            
                            games.append({
                                "home_team": team1,
                                "away_team": team2,
                                "home_tricode": TEAM_TRICODE.get(team1, team1[:3].upper()),
                                "away_tricode": TEAM_TRICODE.get(team2, team2[:3].upper()),
                                "home_score": score1,
                                "away_score": score2,
                                "home_odds": odds1,
                                "away_odds": odds2,
                                "winner": winner,
                                "winner_tricode": TEAM_TRICODE.get(winner, winner[:3].upper()),
                                "loser": loser,
                                "loser_tricode": TEAM_TRICODE.get(loser, loser[:3].upper()),
                                "winner_score": winner_score,
                                "loser_score": loser_score,
                                "winner_odds": winner_odds,
                                "loser_odds": loser_odds,
                                "is_upset": is_upset,
                            })
                
                i += 1
        
        if games:
            print(f"Successfully fetched {len(games)} games from OddsPortal via Jina AI Reader")
        else:
            print("Warning: No games found in Jina AI Reader response, using sample data")
            raise Exception("No games parsed")
            
    except Exception as e:
        print(f"Error fetching from Jina AI Reader: {e}")
        print("Falling back to sample data...")
        
        # Fallback sample data
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
            home_won = h_score > a_score
            winner = home if home_won else away
            loser = away if home_won else home
            winner_score = h_score if home_won else a_score
            loser_score = a_score if home_won else h_score
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
                "loser_odds": loser_odds,
                "is_upset": is_upset,
            })
    
    return games




def generate_upsets_json(games: list, output_path: str):
    """Generate JSON file with upset data for odds.html.
    
    Filename uses day of month (01-31) for automatic monthly rotation.
    e.g., upsets_27.json - will be overwritten next month on the 27th.
    
    Returns:
        dict: Data with upset information including list of underdog tricodes
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
                "loser_odds": g["loser_odds"],
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
    
    # Output underdog teams for GitHub Actions
    if upsets:
        underdog_teams = ",".join([g["winner_tricode"] for g in upsets])
        print(f"\n::set-output name=underdogs::{underdog_teams}")
        print(f"::set-output name=upset_count::{len(upsets)}")
    
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


