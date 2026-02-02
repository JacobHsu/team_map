"""
Analyze NBA odds screenshot using GitHub Models (GPT-4o).
Extracts game data and identifies upsets directly from the image.
"""
import os
import json
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from openai import OpenAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_screenshot():
    # 1. Setup paths
    base_dir = Path(__file__).parent.parent
    taiwan_tz = timezone(timedelta(hours=8))
    day = datetime.now(taiwan_tz).strftime('%d')
    screenshot_path = base_dir / "screenshots" / f"oddsportal_nba_{day}.png"
    
    if not screenshot_path.exists():
        print(f"❌ Screenshot not found: {screenshot_path}")
        return

    print(f"📸 Analyzing screenshot: {screenshot_path}")

    # 2. Prepare OpenAI client for GitHub Models
    token = os.environ.get("GITHUB_TOKEN")
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o"

    if not token:
        print("❌ GITHUB_TOKEN not set. Cannot use GitHub Models.")
        print("   If running locally, ensure you have set GITHUB_TOKEN in your environment.")
        return

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    # 3. Encode image
    base64_image = encode_image(screenshot_path)

    # 4. Define Prompt
    system_prompt = """
    You are an expert NBA data analyst. Your job is to extract game results and odds from a screenshot of OddsPortal.
    
    Rules for extraction:
    1. Identify all COMPLETED games (games with final scores).
    2. Extract: Home Team, Away Team, Home Score, Away Score, Home Odds, Away Odds.
       - Odds are usually in American format (e.g., +150, -120).
       - If odds are Decimal (e.g., 2.50), convert to American:
         - >= 2.00: (Decimal - 1) * 100
         - < 2.00: -100 / (Decimal - 1)
    3. Determine the WINNER.
    4. Identify UPSETS. An upset is when the team with POSITIVE odds (the underdog, e.g., +150) wins against a team with NEGATIVE odds (the favorite, e.g., -180).
       - If both have negative odds (rare), the one with higher odds (closer to 0) is the subtle underdog.
       - If both have positive odds, the one with higher odds is the underdog.
    
    Output JSON format ONLY:
    {
        "total_games": 5,
        "upset_count": 2,
        "upset_rate": 40,
        "upsets": [
            {
                "winner_tricode": "TRICODE", (e.g., LAL, BOS)
                "winner": "Full Team Name",
                "winner_score": 110,
                "winner_odds": 150,
                "loser_tricode": "TRICODE",
                "loser": "Full Team Name",
                "loser_score": 105,
                "loser_odds": -180
            }
        ]
    }
    """

    user_prompt = "Extract today's completed NBA games from this image and identify any upsets."

    # 5. Call Model
    try:
        print("🤖 Sending request to GitHub Models (GPT-4o)...")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                },
            ],
            model=model_name,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        print("✅ Received response from AI")
        
        # 6. Process and Save Data
        data = json.loads(content)
        
        # Add metadata
        taiwan_tz = timezone(timedelta(hours=8))
        now = datetime.now(taiwan_tz)
        data["date"] = now.strftime("%Y-%m-%d")
        data["updated"] = now.strftime("%Y-%m-%d %H:%M")
        
        # Save to upsets/upsets_DD.json
        day_str = now.strftime("%d")
        output_dir = base_dir / "upsets"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"upsets_{day_str}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Saved upsets data to: {output_path}")
        print(f"📊 Identified {data['upset_count']} upsets from {data['total_games']} games.")
        
        # Set outputs for GitHub Actions
        if data.get("upsets"):
            underdogs = ",".join([u["winner_tricode"] for u in data["upsets"]])
            print(f"::set-output name=underdogs::{underdogs}")
            print(f"::set-output name=upset_count::{data['upset_count']}")

    except Exception as e:
        print(f"❌ Error during AI analysis: {e}")
        # Could implement fallback here if needed

if __name__ == "__main__":
    analyze_screenshot()
