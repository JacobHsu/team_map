import json

with open('upsets/upsets_30.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total upsets: {len(data['upsets'])}")
print(f"Date: {data['date']}")
print(f"Total games: {data['total_games']}")
print("\nUpsets:")
for i, u in enumerate(data['upsets']):
    print(f"{i+1}. {u['winner_tricode']} (+{u['winner_odds']}) beat {u['loser_tricode']} ({u['loser_odds']}) - {u['winner_score']}-{u['loser_score']}")
