"""The one question Laya answers about a draft post. Shared by data, training, tests and the UI.

Eight archetypes of LinkedIn / X post, scored in ONE forward pass so the meter can show a whole
distribution on every keystroke (Laya gives per-option probabilities for a `choice` question).
Labels are bare words on purpose: on CPU the token count of the question sets the speed.
"""
LABEL_ORDER = [
    "genuine",           # specific, honest, useful or a plain update: numbers, a real lesson, a real question
    "humblebrag",        # "humbled / honoured / thrilled to announce": self-promotion dressed as gratitude
    "fake_parable",      # invented-feeling story with a tidy moral (intern, janitor, Uber driver, CEO in the lift)
    "engagement_bait",   # "Agree?", "comment GUIDE", "tag someone", "repost to help": asks for reach, gives nothing
    "hustle_guru",       # grindset absolutes: 5AM, "nobody is coming to save you", discipline speeches
    "buzzword_salad",    # synergy, leverage, thought leadership, digital transformation: says nothing
    "shameless_plug",    # hiring / course / agency / product pitch: "spots left", "DM me", "link below"
    "ai_thread_bro",     # "10 AI tools that will replace you", "the exact prompt I use", save-this-post threads
]
INSTRUCTION = "What kind of social media post is this?"
QUESTIONS = {"kind": {"type": "choice", "instructions": INSTRUCTION, "criteria": {k: "" for k in LABEL_ORDER}}}

# Laya cannot write text, so the "voice" of the meter is canned lines chosen by code from the top label.
VERDICTS = {
    "genuine": ["Suspiciously useful.", "Specific, honest, no fog machine. Post it.", "Alarmingly normal. Ship it."],
    "humblebrag": ["You are 'humbled'. You are not humbled.", "Brag detected wearing a gratitude costume.", "Nobody is fooled by 'honoured'."],
    "fake_parable": ["No janitor ever said that.", "This story has a moral and no witnesses.", "Ah, the wise Uber driver returns."],
    "engagement_bait": ["You are asking for likes with a straight face.", "'Agree?' is not an idea.", "The algorithm is thrilled. Humans are not."],
    "hustle_guru": ["Somewhere a 5AM alarm just screamed.", "Discipline speech: 100% delivered, 0% specifics.", "Nobody is coming to save you, but also this is a lot."],
    "buzzword_salad": ["Synergy levels critical.", "Fluent in corporate, empty in meaning.", "You leveraged a paradigm. What did it do?"],
    "shameless_plug": ["Ah, a commercial break.", "'Link in bio' energy.", "It's an ad. Own it."],
    "ai_thread_bro": ["Thread bro alert: 'you're using AI wrong'.", "Save this post (you will not).", "Ten tools that will change your life by Tuesday."],
}
