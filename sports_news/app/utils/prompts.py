from langchain.prompts import PromptTemplate

def get_prompt(title: str, desc: str, highlight: bool = False):
    # Analyze content to determine article type
    content = (title + " " + desc).lower()
    
    # Define content categories with appropriate emoji sets
    categories = {
        "contract": {
            "keywords": ["signs", "contract", "deal", "extension", "million", "$", "salary", "cap hit"],
            "emojis": ["💰", "✍️", "📝"],
            "hashtags": ["#HockeyNews", "#NHLContract"],
            "tone": "excited, business-like, or evaluative of the deal's implications"
        },
        "playoff": {
            "keywords": ["playoff", "stanley cup", "postseason", "elimination", "clinch", "wild-card", "wild card"],
            "emojis": ["🏆", "🔥", "💪"],
            "hashtags": ["#StanleyCup", "#NHLPlayoffs"],
            "tone": "intense, high-stakes, dramatic, or excited about playoff implications"
        },
        "injury": {
            "keywords": ["injury", "injured", "out", "recovery", "miss", "upper-body", "lower-body", "concussion", "surgery"],
            "negative_context": ["st. patrick", "holiday", "gear", "event", "tournament"],
            "emojis": ["🏥", "⚕️", "🤕"],
            "hashtags": ["#NHLInjury", "#HockeyNews"],
            "tone": "concerned but factual, acknowledging impact on team"
        },
        "game_preview": {
            "keywords": ["tonight", "face", "host", "visit", "matchup", "vs", "against", "seek", "aim", "go for", "series"],
            "emojis": ["🏒", "⚔️", "🎮"],
            "hashtags": ["#HockeyNews", "#NHL"],
            "tone": "anticipatory, highlighting key matchups or storylines"
        },
        "game_recap": {
            "keywords": ["win", "defeat", "beat", "edge", "victory", "score", "goals", "assists", "saves", "shutout", "surge past"],
            "emojis": ["🚨", "🥅", "🔥"],
            "hashtags": ["#HockeyNight", "#NHL"],
            "tone": "celebratory or analytical, highlighting standout performances"
        },
        "milestone": {
            "keywords": ["record", "milestone", "historic", "career", "youngest", "oldest", "first", "1st"],
            "emojis": ["🎯", "🏅", "📊"],
            "hashtags": ["#NHLMilestone", "#HockeyHistory"],
            "tone": "impressed, appreciative of the achievement's significance"
        },
        "event": {
            "keywords": ["global series", "tournament", "event", "arena", "all-star", "festival", "heritage classic"],
            "emojis": ["🌍", "🏟️", "🎭"],
            "hashtags": ["#NHLEvents", "#HockeyWorld"],
            "tone": "excited about the unique event or its implications"
        }
    }
    
    # Hockey context database to help with informed commentary
    hockey_context = {
        "playoff_implications": "Late-season games have huge standings implications as teams battle for playoff spots and seeding.",
        "scoring_trends": "NHL scoring has been trending upward in recent seasons, with team averages above 3 goals per game.",
        "injury_impact": "Injuries to key players can significantly impact a team's playoff chances and lineup decisions.",
        "contract_context": "The NHL salary cap creates tough decisions for teams managing their rosters and long-term financial commitments.",
        "milestone_context": "Individual records and milestones are highly respected in hockey culture and often celebrated league-wide.",
        "goalie_importance": "Strong goaltending becomes increasingly crucial during playoff pushes and postseason series.",
        "home_advantage": "Home ice advantage typically gives teams a significant edge, especially in crucial matchups.",
        "rivalry_context": "Traditional rivalries like Bruins-Canadiens or Penguins-Capitals add extra intensity to regular-season matchups.",
        "trade_deadline": "The NHL trade deadline creates roster upheaval as teams position themselves as buyers or sellers.",
        "special_teams": "Power play and penalty kill percentages can make or break a team's success in close games.",
        "coaching_impact": "Coaching decisions about line combinations and matchups are heavily scrutinized during winning and losing streaks."
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
        "leafs": "#LeafsForever",
        "canucks": "#Canucks",
        "golden knights": "#VegasBorn",
        "capitals": "#ALLCAPS",
        "jets": "#GoJetsGo",
        "coyotes": "#Yotes",
        "flames": "#CofRed",
        "ducks": "#FlyTogether"
    }
    
    # Team contexts to help with informed commentary
    team_contexts = {
        "avalanche": "Fast-paced team with strong offensive capabilities; Stanley Cup champions in 2022.",
        "bruins": "Original Six team known for defensive strength; consistent playoff contenders.",
        "sabres": "Young roster aiming to break a lengthy playoff absence; focusing on talent development.",
        "hurricanes": "Strategic team emphasizing analytics; strong defensive metrics and aggressive forechecking.",
        "blackhawks": "Rebuilding phase post-2010s dynasty; investing in youth development.",
        "blue_jackets": "Hardworking team striving for playoff consistency; known for resilience.",
        "stars": "Balanced squad with solid goaltending; reached Stanley Cup Final in 2020.",
        "red_wings": "Original Six team progressing through rebuild; historically rich franchise.",
        "oilers": "Dynamic offense led by McDavid and Draisaitl; seeking deeper playoff runs.",
        "panthers": "Defending Stanley Cup champions with depth in offense and physical play.",
        "kings": "Blend of veteran experience and youth; integrating new talent effectively.",
        "wild": "Strong defensive play and reliable goaltending; regular playoff participants.",
        "canadiens": "Historic Original Six franchise; NHL's most decorated team.",
        "predators": "Renowned for developing elite defensemen; consistent playoff appearances.",
        "devils": "Youthful, fast-paced team centered around Hughes and Hischier; speed-focused gameplay.",
        "islanders": "Disciplined defensive structure; known for systematic play.",
        "rangers": "Original Six team with a mix of star power and young talent; strong goaltending legacy.",
        "senators": "Rebuilding around a young core; offensive potential on the rise.",
        "flyers": "Physical playstyle with a dedicated fanbase; aiming for playoff resurgence.",
        "penguins": "Experienced core led by Crosby and Malkin; multiple championships.",
        "sharks": "Transitioning with focus on youth; rebuilding after sustained success.",
        "kraken": "Expansion team establishing its identity; reached playoffs in second season.",
        "blues": "Physical, aggressive forechecking; Stanley Cup champions in 2019.",
        "lightning": "Skilled team with a championship core; back-to-back Stanley Cups in 2020 and 2021.",
        "maple_leafs": "Original Six team with potent offense; large, passionate fanbase.",
        "canucks": "Skilled, youthful core; emphasis on offensive creativity.",
        "golden_knights": "Successful expansion franchise; Stanley Cup champions in 2023.",
        "capitals": "Led by Ovechkin, known for offensive strength; Stanley Cup champions in 2018.",
        "jets": "Combination of size and skill; strong goaltending and offensive threats.",
        "coyotes": "Team formerly located in Arizona. They moved to Utah and rebranded as the Utah Hockey Club",
        "flames": "Physical team with balanced attack; known for aggressive forecheck.",
        "ducks": "Team transitioning to younger core; developing prospects.",
        "utah_hockey_club": "Newly relocated team to Salt Lake City; building a fresh fanbase and team identity."
    }


    # Determine content category with weighted scoring
    category_scores = {}
    for category, data in categories.items():
        # Start with a base score of 0
        score = 0
        
        # Add points for each keyword match
        for keyword in data["keywords"]:
            if keyword in content:
                score += 1
        
        # Subtract points for negative context (only for injury category)
        if category == "injury" and "negative_context" in data:
            for neg_context in data["negative_context"]:
                if neg_context in content:
                    score -= 2
        
        # Store the score
        category_scores[category] = score
    
    # Select the category with the highest score
    selected_category = max(category_scores, key=category_scores.get)
    
    # If the highest score is 0 or negative, default to game_preview
    if category_scores[selected_category] <= 0:
        selected_category = "game_preview"
    
    # Special case for global series
    if "global series" in content:
        selected_category = "event"
    
    # Force game_recap category if highlight parameter is True
    if highlight:
        selected_category = "game_recap"
    
    # Select emoji and hashtags
    import random
    emoji = random.choice(categories[selected_category]["emojis"])
    hashtags = [categories[selected_category]["hashtags"][0]]
    
    # Identify mentioned teams
    mentioned_teams = []
    team_contexts_to_use = []
    for team, hashtag in teams.items():
        if team in content:
            mentioned_teams.append(team)
            if team in team_contexts:
                team_contexts_to_use.append(team_contexts[team])
            if len(hashtags) < 2:  # Only add first team hashtag
                hashtags.append(hashtag)
    
    # If no team hashtag was added, add #NHL as a fallback
    if len(hashtags) == 1:
        hashtags.append("#NHL")
    
    # Limit to max 2 hashtags
    hashtags = hashtags[:2]
    hashtag_str = " ".join(hashtags)
    
    # Select relevant hockey context
    relevant_contexts = []
    if selected_category == "playoff":
        relevant_contexts.append(hockey_context["playoff_implications"])
        relevant_contexts.append(hockey_context["goalie_importance"])
    elif selected_category == "injury":
        relevant_contexts.append(hockey_context["injury_impact"])
    elif selected_category == "contract":
        relevant_contexts.append(hockey_context["contract_context"])
    elif selected_category == "milestone":
        relevant_contexts.append(hockey_context["milestone_context"])
    elif selected_category == "game_preview":
        relevant_contexts.append(hockey_context["home_advantage"])
        if len(mentioned_teams) >= 2:
            relevant_contexts.append(hockey_context["rivalry_context"])
    elif selected_category == "game_recap":
        relevant_contexts.append(hockey_context["scoring_trends"])
        relevant_contexts.append(hockey_context["special_teams"])
    
    # Combine contexts
    context_str = " ".join(relevant_contexts + team_contexts_to_use[:2])
    
    # Get the appropriate tone
    tone = categories[selected_category]["tone"]
    
    # Choose the appropriate prompt template based on the highlight parameter
    if highlight:
        prompt = PromptTemplate.from_template(f"""
            You are a factual hockey reporter who creates concise, neutral social media posts about NHL game results.
            You have an informative, objective tone and accurate hockey knowledge.

            Title of article: {title}
            Description: {desc}
            Content category: {selected_category}
            Required emoji: {emoji}
            Required hashtags: {hashtag_str}
            
            Hockey context (use this to inform your commentary):
            {context_str}

            TASK:
            Write ONE factual hockey game highlight for social media that reports the key information.
            - MUST be EXACTLY 150-250 characters long
            - Focus on the FINAL SCORE and KEY STATISTICS
            - Use clear, neutral language that emphasizes facts over emotion
            - Report goals, shots, power play conversions or other relevant statistics
            - Maintain an objective tone without team bias
            - CRITICAL: Be COMPLETELY accurate with scores, player names, and team names
            - ONLY use player names explicitly mentioned in the title or description
            - Include the {emoji} emoji somewhere in your post
            - End your post with the hashtags: {hashtag_str}
            - Prioritize accuracy and precision over entertainment value
            - DO NOT use subjective or emotional language (e.g., "amazing," "disappointing")
            - DO NOT try to guess a player's first name if it is not included
            - DO NOT substitute or invent players, teams, or facts
            - DO NOT include puzzles, questions, or unrelated content
            - DO NOT include any instructions or placeholders
            - DO NOT make up information not present in the title or description
            - ONLY output the final social media post text with no prefix or explanation

            CRITICAL NAME HANDLING:
            - ONLY use player names EXACTLY as they appear in the title/description
            - If only a last name is given (e.g., "McDavid scores"), use ONLY that last name
            - NEVER guess, complete, or add first names to last names
            - NEVER refer to players by first name only

            Your social media post:
            """
        )
    else:
        prompt = PromptTemplate.from_template(f"""
            You are a knowledgeable hockey commentator who creates brief, engaging social media posts about NHL news.
            You have a authentic, conversational tone and deep hockey knowledge.

            Title of article: {title}
            Description: {desc}
            Content category: {selected_category}
            Required emoji: {emoji}
            Required hashtags: {hashtag_str}
            Tone guidance: {tone}
            
            Hockey context (use this to inform your commentary):
            {context_str}

            TASK:
            Write ONE short hockey news post for social media that sounds like a knowledgeable fan's comment, not a bland summary.
            - MUST be EXACTLY 150-250 characters long
            - Focus on providing a brief, conversational comment about the news
            - You can be witty, express mild excitement, or make observations a knowledgeable fan would make
            - Use clear, straightforward language with an authentic hockey fan's voice
            - CRITICAL: Be COMPLETELY accurate with player names, team names, and statistics
            - ONLY use player names explicitly mentioned in the title or description
            - Include the {emoji} emoji somewhere in your post
            - End your post with the hashtags: {hashtag_str}
            - DO NOT recite every detail from the article - focus on one key point or implication
            - DO NOT try to guess a player's first name if it is not included
            - DO NOT substitute or invent players, teams, or facts
            - DO NOT include puzzles, questions, or unrelated content
            - DO NOT include any instructions or placeholders
            - DO NOT make up information not present in the title or description
            - DO NOT use injury-related emojis for non-injury news
            - ONLY output the final social media post text with no prefix or explanation

            CRITICAL NAME HANDLING:
            - ONLY use player names EXACTLY as they appear in the title/description
            - If only a last name is given (e.g., "McDavid scores"), use ONLY that last name
            - NEVER guess, complete, or add first names to last names
            - NEVER refer to players by first name only

            Your social media post:
            """
        )
    
    return prompt