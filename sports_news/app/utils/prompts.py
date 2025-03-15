from langchain.prompts import PromptTemplate

def get_prompt(title: str, desc: str):
    # Analyze content to determine article type
    content = (title + " " + desc).lower()
    
    # Define content categories with appropriate emoji sets
    categories = {
        "contract": {
            "keywords": ["signs", "contract", "deal", "extension", "million", "$"],
            "emojis": ["💰", "✍️", "📝"],
            "hashtags": ["#HockeyNews", "#NHLContract"]
        },
        "playoff": {
            "keywords": ["playoff", "stanley cup", "postseason", "elimination", "clinch"],
            "emojis": ["🏆", "🔥", "💪"],
            "hashtags": ["#StanleyCup", "#NHLPlayoffs"]
        },
        "injury": {
            "keywords": ["injury", "injured", "out", "return", "recovery", "miss"],
            "emojis": ["🏥", "⚕️", "🤕"],
            "hashtags": ["#NHLInjury", "#HockeyNews"]
        },
        "game_preview": {
            "keywords": ["tonight", "face", "host", "visit", "matchup", "vs", "against", "seek", "aim", "go for"],
            "emojis": ["🏒", "⚔️", "🎮"],
            "hashtags": ["#GameDay", "#NHL"]
        },
        "milestone": {
            "keywords": ["record", "milestone", "historic", "career", "youngest", "oldest", "first", "1st"],
            "emojis": ["🎯", "🏅", "📊"],
            "hashtags": ["#NHLMilestone", "#HockeyHistory"]
        }
    }
    
    # Detect team names to add team hashtags
    teams = {
        "avalanche": "#GoAvsGo",
        "bruins": "#NHLBruins",
        "sabres": "#LetsGoBuffalo",
        "hurricanes": "#LetsGoCanes",
        "blackhawks": "#Blackhawks",
        "blue jackets": "#CBJ",
        "stars": "#TexasHockey",
        "red wings": "#LGRW",
        "oilers": "#LetsGoOilers",
        "panthers": "#TimeToHunt",
        "kings": "#GoKingsGo",
        "wild": "#mnwild",
        "canadiens": "#GoHabsGo",
        "predators": "#Preds",
        "devils": "#NJDevils",
        "islanders": "#Isles",
        "rangers": "#NYR",
        "senators": "#GoSensGo",
        "flyers": "#BringItToBroad",
        "penguins": "#LetsGoPens",
        "sharks": "#SJSharks",
        "kraken": "#SeaKraken",
        "blues": "#STLBlues",
        "lightning": "#GoBolts",
        "maple leafs": "#LeafsForever",
        "canucks": "#Canucks",
        "golden knights": "#VegasBorn",
        "capitals": "#ALLCAPS",
        "jets": "#GoJetsGo",
        "coyotes": "#Yotes",
        "flames": "#CofRed",
        "ducks": "#FlyTogether"
    }
    
    # Determine content category
    selected_category = None
    for category, data in categories.items():
        if any(keyword in content for keyword in data["keywords"]):
            selected_category = category
            break
    
    # Default to game_preview if no category matches
    if not selected_category:
        selected_category = "game_preview"
    
    # Select emoji and hashtags
    import random
    emoji = random.choice(categories[selected_category]["emojis"])
    hashtags = [categories[selected_category]["hashtags"][0]]
    
    # Add team hashtag if detected
    for team, team_hashtag in teams.items():
        if team in content:
            hashtags.append(team_hashtag)
            break
    
    # If no team hashtag was added, add #NHL as a fallback
    if len(hashtags) == 1:
        hashtags.append("#NHL")
    
    # Limit to max 2 hashtags
    hashtags = hashtags[:2]
    hashtag_str = " ".join(hashtags)
    
    # Create customized prompt
    prompt = PromptTemplate.from_template(f"""
        You are a sports news summarizer that creates brief, engaging summaries for hockey social media posts.

        Title of article: {title}
        Description: {desc}
        Content category: {selected_category}
        Required emoji: {emoji}
        Required hashtags: {hashtag_str}

        TASK:
        Write ONE short summary of this hockey news article for social media.
        - MUST be EXACTLY 150-250 characters long
        - Focus only on the main news from the title and description
        - Use clear, straightforward language 
        - CRITICAL: Be COMPLETELY accurate with player names, team names, and statistics
        - ONLY use player names explicitly mentioned in the title or description
        - Include the {emoji} emoji somewhere in your summary
        - End your summary with the hashtags: {hashtag_str}
        - DO NOT substitute or invent players, teams, or facts
        - DO NOT include puzzles, rules, questions, or unrelated content
        - DO NOT include any instructions or placeholders
        - DO NOT make up information not present in the title or description
        - ONLY output the final summary text with no prefix or explanation

        Your summary:
        """
    )
    
    return prompt