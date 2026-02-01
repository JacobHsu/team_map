import json

from datetime import datetime, timezone, timedelta

# 取得台灣時區的日期
taiwan_tz = timezone(timedelta(hours=8))
day = datetime.now(taiwan_tz).strftime('%d')

filename = f'upsets/upsets_{day}.json'

with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total upsets: {len(data['upsets'])}")
print(f"Date: {data['date']}")
print(f"Total games: {data['total_games']}")
print("\nUpsets:")
for i, u in enumerate(data['upsets']):
    print(f"{i+1}. {u['winner_tricode']} (+{u['winner_odds']}) beat {u['loser_tricode']} ({u['loser_odds']}) - {u['winner_score']}-{u['loser_score']}")
