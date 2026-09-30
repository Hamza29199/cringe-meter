"""Synthetic LinkedIn / X post drafts for the eight archetypes in schema.py.

A post is assembled from class-specific pieces (hook + 0-3 middles + closer), then formatted and
decorated by transforms that are IDENTICAL for every class (blank-line "broetry", plain paragraph,
emoji, hashtags, ALL CAPS, lowercase), so line breaks and rocket emojis carry no label information.
The last two hooks / middles / closers of every class are held out for validation, so validation
measures unseen phrasings, not unseen slot fills.

    python gen_synthetic.py            -> data/synth.jsonl     (v1)
    python gen_synthetic.py --v2       -> data/synth_v2.jsonl  (adds synth_extra.py; more genuine variety)
"""
import collections, json, random

rng = random.Random(20260930)

SLOTS = dict(
    award=["Top 40 Under 40", "Leader of the Year", "Best Workplaces 2026", "Innovator of the Year", "Forbes 30 Under 30", "Rising Star"],
    conf=["TEDx", "SaaStr", "Web Summit", "a sold-out keynote", "the main stage at Dreamforce"],
    company=["Google", "a Fortune 500", "Acme", "a Series B startup", "Amazon", "McKinsey", "a tiny agency"],
    role=["Senior Engineer", "VP of Growth", "Head of Product", "Founder & CEO", "Director of Sales", "Chief of Staff"],
    city=["a small town in Ohio", "Karachi", "Lagos", "rural Texas", "a village in Punjab", "the Bronx"],
    field=["data engineering", "design", "sales", "embedded systems", "climate tech", "supply chain", "recruiting", "SEO"],
    tool=["Postgres", "Redis", "Figma", "dbt", "Kubernetes", "Excel", "Notion", "Terraform"],
    thing=["flaky test", "memory leak", "onboarding flow", "churn dashboard", "slow query", "broken CI job"],
    buzz=["AI-driven", "scalable", "holistic", "best-in-class", "synergistic", "next-gen", "end-to-end", "mission-critical"],
    noun=["ecosystem", "stakeholders", "value chain", "digital transformation", "paradigm", "thought leadership journey", "go-to-market motion"],
    person=["an intern", "a janitor", "my Uber driver", "a barista", "a homeless man outside the office", "my 6-year-old", "a stranger on a train", "our security guard"],
    course=["The 10x Creator Blueprint", "Cold Email Mastery", "LinkedIn Authority Accelerator", "Prompt Engineering Secrets"],
    audience=["founders", "coaches", "SaaS teams", "creators", "recruiters", "consultants"],
    month=["March", "next month", "Q4", "January"],
    n=["3", "4", "5", "7", "9", "12", "27", "50", "100"],
    pct=["23", "31", "40", "58", "72", "8", "14"],
    k=["12", "40", "250", "1,200", "8,000"],
    dur=["3 weeks", "two days", "a weekend", "6 months", "90 days"],
    mins=["10", "7", "15", "12"],
    name=["Priya", "Marcus", "Aisha", "Tomás", "Wei", "Sofia", "Daniel", "Ngozi", "Ravi", "Elena"],
)


def fill(s):
    return s.format(**{k: rng.choice(v) for k, v in SLOTS.items()})


# ---- pieces: (hooks, middles, closers). The last 2 of each are held out for validation. ------------
P = {}
P["genuine"] = (
    ["We shipped the new {tool} migration today. It took {dur}, and one rollback.",
     "Quick update: I'm looking for a new role in {field}. Open to contract or full-time.",
     "Lessons from debugging a {thing} at 2am:",
     "Here's the exact query that cut our dashboard load time from {n}s to under 1s.",
     "Question for the {field} people here: how do you handle {thing}s without losing a week?",
     "Congrats to the team on the launch. The last {dur} were rough and everyone showed up.",
     "Thanks to everyone who came to the meetup. About {k} of you, more than we planned for.",
     "I got the {thing} wrong for a full month before I understood it.",
     "Our churn went down {pct}% after we fixed one boring thing in onboarding.",
     "Reading list this month, with one line on each so you can skip what you don't need.",
     "I'm leaving {company} after {n} years. Some notes on what I learned and what I'd do differently.",
     "Honest post-mortem of last week's outage:",
     "We turned down a big client this week because the scope didn't fit. Here's how we decided.",
     "PSA: if you use {tool} with default settings, check this one config."],
    ["The cause was a missing index. Adding it fixed {pct}% of the slowdown.",
     "We measured it before and after. The numbers are in the table below.",
     "It cost us {n} hours and we'd do it again, but with a smaller first step.",
     "I'm not sure this generalises. It worked for a team of {n}, so treat it as one data point.",
     "The tradeoff is real: faster reads, slower writes. We chose reads.",
     "If it helps, the config is one line and I've pasted it below.",
     "Three things went wrong. First, we skipped the staging run. Second, nobody owned the alert. Third, the docs were stale.",
     "Happy to be corrected if I've got any of this wrong."],
    ["Happy to share the details if anyone's interested.",
     "Curious how others have handled this.",
     "That's it. Hope it saves someone a weekend.",
     "If you're hiring for {field}, my inbox is open.",
     "Thanks for reading.",
     "Corrections welcome.",
     "More notes in the doc I linked at the top.",
     "Back to work."],
)
P["humblebrag"] = (
    ["I'm humbled to announce that I've been named {award}.",
     "Thrilled and honored to share that I'll be speaking at {conf}.",
     "Some personal news (I promise I'm not bragging):",
     "I don't usually post about this, but I was just promoted to {role} at {company}.",
     "Grateful beyond words to receive {award}.",
     "Still processing this. I was just recognised as {award}.",
     "Today I got the news I've been waiting years for. Humbled. Speechless.",
     "Big day! Our company just crossed {k} customers and I'm feeling so blessed.",
     "I'm so incredibly honored to be listed among {award} this year.",
     "Never thought a kid from {city} would end up here.",
     "Excited (and slightly embarrassed) to share that {company} acquired our little startup.",
     "Pinch me. I just rang the bell at the stock exchange.",
     "Humbled and grateful. A quick thank you for the {award} nomination.",
     "It's official: I've joined {company} as {role}. Feeling so lucky."],
    ["This wouldn't be possible without my incredible team. I'm just the face of it.",
     "I never thought a kid from {city} would end up on {conf}. Life is wild.",
     "I still can't believe it. I'm just a small-town person doing what I love.",
     "To everyone who believed in me when I was nobody: this is for you.",
     "I didn't do this alone, but I did do a lot of it (kidding!).",
     "Honestly I don't feel like I deserve this, there are so many more talented people out there.",
     "Sleepless nights, {n} rejections, and now this. Grateful for every step.",
     "The messages coming in have been overwhelming. Thank you all."],
    ["Blessed and humbled. 🙏",
     "Onwards and upwards. #grateful",
     "Here's to the next chapter.",
     "Thank you, thank you, thank you.",
     "Just getting started.",
     "So grateful. So humbled. So excited.",
     "Feeling incredibly lucky and thankful.",
     "Sending love to everyone who reached out."],
)
P["fake_parable"] = (
    ["I fired {person} for being {mins} minutes late.",
     "{person} taught me more about leadership than my MBA.",
     "{person} asked me one question that changed my life.",
     "I was rejected by {n} companies. Then I met {person}.",
     "The CEO stopped me in the elevator and said 4 words.",
     "My daughter asked me why I work so much. I had no answer.",
     "I saw {person} crying at the airport. What happened next?",
     "Last week, {person} handed me a note. I still think about it.",
     "I almost quit yesterday. Then {person} said something I'll never forget.",
     "A man in a hoodie walked into our office. Everyone ignored him.",
     "We were about to lose our biggest client. Then {person} walked in.",
     "I interviewed a candidate who arrived in a torn suit. Here's what he did next.",
     "On my flight, {person} asked to borrow a pen.",
     "Yesterday {person} did something no MBA ever taught me."],
    ["He looked at me and said nothing. Then he handed me his phone. On the screen was my own résumé.",
     "I felt my face go red. I didn't know what to say.",
     "Turns out he was the founder of the company I'd been trying to join for years.",
     "She smiled and said: 'It's not about the job. It's about who you are when nobody's watching.'",
     "The room went silent. You could hear a pin drop.",
     "I walked out of that room a different person.",
     "He had been listening to every word the whole time.",
     "I was speechless. Tears in my eyes."],
    ["Moral: treat everyone like they could be your boss.",
     "Be kind. You never know who's standing in front of you.",
     "Repost if this moved you.",
     "Never judge a book by its cover.",
     "Character is what you do when nobody's looking.",
     "Lead with empathy. Always.",
     "Agree? 👇",
     "That's the day I learned what leadership really is."],
)
P["engagement_bait"] = (
    ["Agree or disagree? 👇",
     "Comment 'GUIDE' and I'll DM you my free template.",
     "Tag someone who needs to see this.",
     "Like if you agree, repost to help others.",
     "What's your biggest {field} mistake? Let's see who's honest.",
     "Unpopular opinion: meetings should be optional. Thoughts?",
     "Drop a 🔥 if you're still working on Friday.",
     "Which is better: remote or office? Vote in the comments.",
     "Type 'YES' if you want part 2.",
     "Comment your favorite emoji and I'll tell you your leadership style.",
     "Be honest: would you take a {pct}% pay cut for a 4-day week?",
     "Hiring managers, what's the one thing you can't stand on a résumé?",
     "Repost this ♻️ to help someone in your network today.",
     "Who else does this? 😅 Tell me I'm not alone."],
    ["I'll go first: I answered every email within a minute for {n} years and it made me miserable.",
     "The comments on this always surprise me.",
     "I read every single reply, so make it good.",
     "Only the top comment gets my free {course} bonus pack.",
     "Save this for later and share it with your team.",
     "This got {k} likes last time. Let's beat it.",
     "Let's get this to more people.",
     "Reply with your answer below."],
    ["Follow me for more {field} content.",
     "♻️ Repost to help your network.",
     "Let me know in the comments!",
     "Thoughts? 👇",
     "Comment below and let's discuss.",
     "Share this with someone who needs it.",
     "Tag a friend. You know who.",
     "Like, comment, share. You know the drill."],
)
P["hustle_guru"] = (
    ["Nobody is coming to save you.",
     "At 5AM while you're sleeping, I'm already winning.",
     "Stop making excuses. Start making money.",
     "{n} habits that made me a millionaire at 27.",
     "The difference between you and them? Discipline.",
     "Your comfort zone is a beautiful place where nothing grows.",
     "You don't need motivation. You need standards.",
     "While you scroll, someone else is building.",
     "Rich people don't take weekends. They take opportunities.",
     "Hard work beats talent when talent doesn't work hard.",
     "Wake up. Grind. Repeat. There is no step four.",
     "Your 9-to-5 is a leash and you're calling it a career.",
     "Nobody cares about your excuses. Not even your future self.",
     "Discipline is choosing what you want most over what you want now."],
    ["Discomfort is the price of admission for the life you want.",
     "Every no is a step closer to a yes. Keep going.",
     "I slept {n} hours a night for {dur} and it was the best decision of my life.",
     "Winners don't complain. They execute.",
     "The gap between where you are and where you want to be is called work.",
     "Pain is temporary. Regret is forever.",
     "Ice baths, cold calls, and zero excuses.",
     "Your competition is out there. Are you?"],
    ["Your future self is watching. Don't let him down.",
     "Winners don't complain. They execute.",
     "The grind never stops.",
     "Are you built for this?",
     "Stay hungry. Stay humble. Stay hard.",
     "No days off.",
     "Make it happen.",
     "Success is a decision."],
)
P["buzzword_salad"] = (
    ["Excited to be leveraging {buzz} solutions to unlock synergies across the {noun}.",
     "As a passionate thought leader in the {field} space, I'm driving {buzz} outcomes.",
     "Driving holistic {noun} through {buzz} innovation.",
     "Proud to announce our {buzz} approach to the {noun}.",
     "Delighted to share our vision for a {buzz}, human-centric {noun}.",
     "Today we're moving the needle on {buzz} {noun}.",
     "Our {buzz} strategy empowers stakeholders to ideate across the {noun}.",
     "We are {buzz} enablers of {buzz} value creation.",
     "Thinking about how to operationalise the {noun} at scale.",
     "Realising synergies through {buzz} alignment in a fast-moving {noun}.",
     "It's all about the {noun}. Let me explain.",
     "The {noun} demands a {buzz} mindset.",
     "Bringing the {buzz} to the {noun}, one paradigm at a time.",
     "Innovation is the {noun} of the future, today."],
    ["By aligning cross-functional stakeholders around a {buzz} value proposition, we are moving the needle.",
     "Our north star is a {buzz} framework that lifts all boats.",
     "It's about creating a culture of {buzz} excellence across the {noun}.",
     "We're pivoting to a customer-obsessed, {buzz} operating model.",
     "The key is to leverage learnings and double down on {buzz} core competencies.",
     "Together we're disrupting the status quo through {buzz} thought leadership.",
     "This unlocks {buzz} scalability without sacrificing agility.",
     "We're breaking down silos and building bridges across the {noun}."],
    ["Let's circle back and ideate on next-gen {noun}.",
     "The future is {buzz}.",
     "Excited for what's next in this {buzz} journey.",
     "Stay tuned for more {buzz} updates.",
     "Together we can move the needle.",
     "Onwards to a {buzz} tomorrow.",
     "Let's connect and unlock value together.",
     "Innovation never sleeps."],
)
P["shameless_plug"] = (
    ["We're hiring! 🚀",
     "Launching my new course: {course}!",
     "My agency just opened {n} spots for {month}.",
     "Check out our new product, link below.",
     "DM me if you want to 10x your {field} results.",
     "Only {n} seats left for my next cohort.",
     "Introducing {course}, built for {audience}.",
     "We help {audience} land clients in {dur}.",
     "Big news: our new {tool} plugin is live. Get it now.",
     "Looking for a {role}? My agency can help.",
     "Book a free strategy call and let's talk about your {field} funnel.",
     "Early-bird pricing ends tonight.",
     "Our waitlist just opened. Join before it closes.",
     "New drop: {course}. Limited time only."],
    ["First {n} buyers get {pct}% off plus a bonus template pack.",
     "We've helped {k} {audience} scale their revenue.",
     "Includes lifetime access, weekly calls, and a private community.",
     "Results not typical, but they're pretty good.",
     "Spots are limited because I personally review every application.",
     "Money-back guarantee, no questions asked.",
     "Everything you need to go from zero to {k} in {dur}.",
     "Perfect for {audience} who are tired of guessing."],
    ["Book a call. Link in bio.",
     "Only {n} spots left.",
     "Apply now.",
     "DM me 'START' to get access.",
     "Link in the comments.",
     "Don't miss out.",
     "Reserve your spot today.",
     "Grab it before midnight."],
)
P["ai_thread_bro"] = (
    ["I asked ChatGPT to run my {field} business for a week. The results will shock you.",
     "{n} AI tools that will replace your job (thread 🧵)",
     "Most people are using AI wrong. Here's the exact prompt I use:",
     "AI just changed everything. Here's what you need to know:",
     "Stop scrolling. These {n} prompts will save you {n} hours a week.",
     "Claude, GPT and Gemini walk into a bar. Here's who wins.",
     "The AI stack every {audience} needs in 2026:",
     "You're missing out if you're not using these {n} free AI tools.",
     "I replaced my entire {field} team with AI. Here's what happened.",
     "Prompt engineering is dead. Here's what replaced it.",
     "Bookmark this. It's the only AI cheat sheet you'll ever need.",
     "AI agents will do your {field} job by next year. Here's the proof.",
     "The {n}-step AI workflow that 10x'd my output:",
     "This one prompt made me a {field} expert overnight."],
    ["1/ Use it for first drafts, not final drafts. 2/ Give it a role. 3/ Ask it to critique itself.",
     "Copy and paste this: 'Act as a world-class {field} strategist and...'",
     "Tool #1 automates your inbox. Tool #2 writes your posts. Tool #3 does your slides.",
     "Here's the exact workflow, step by step (save this):",
     "No coding. No experience. Just this prompt.",
     "Then paste the output into a doc and watch the magic happen.",
     "It took me {mins} minutes. It used to take {dur}.",
     "Most people quit at step 2. Don't."],
    ["Bookmark this. Follow for daily AI tips.",
     "Which one are you trying first?",
     "Save this post. You'll thank me later.",
     "Follow me to stay ahead of AI.",
     "RT to help someone in your circle.",
     "That's a wrap. Thread over 🧵",
     "The future is here. Don't get left behind.",
     "If this helped, share it with someone who needs it."],
)

EMOJI = ["", "", "", "", "🚀 ", "🔥 ", "💡 ", "✅ ", "👇 ", "🙏 ", "📈 ", "⚡ ", "🧵 "]
TAGS = ["", "", "", "", "", "", " #leadership", " #ai", " #growth", " #startup", " #hiring", " #mindset", " #innovation", " #buildinpublic"]


def assemble(cls, held):
    hooks, mids, closers = P[cls]
    sel = (lambda xs: xs[-2:]) if held else (lambda xs: xs[:-2])
    hook = fill(rng.choice(sel(hooks)))
    parts = [hook]
    if rng.random() < 0.75:
        pool = sel(mids)
        parts += [fill(m) for m in rng.sample(pool, min(len(pool), rng.choice([1, 1, 2, 3])))]
    if rng.random() < 0.8:
        parts.append(fill(rng.choice(sel(closers))))
    return parts


def render(parts):
    """Class-independent formatting: the model must not learn 'blank lines = broetry = label X'."""
    r = rng.random()
    if r < 0.40:
        text = "\n\n".join(parts)                       # broetry
    elif r < 0.55:
        text = "\n".join(parts)
    else:
        text = " ".join(parts)                          # plain paragraph
    text = rng.choice(EMOJI) + text + rng.choice(TAGS)
    q = rng.random()
    if q < 0.05:
        text = text.lower()
    elif q < 0.07:
        text = text.upper()
    return text.strip()


def merge_extra():
    """v2: add synth_extra.EXTRA pieces to the TRAIN part of every pool (before the 2 held-out pieces)."""
    from synth_extra import EXTRA
    for cls, (h, m, c) in EXTRA.items():
        oh, om, oc = P[cls]
        P[cls] = (oh[:-2] + h + oh[-2:], om[:-2] + m + om[-2:], oc[:-2] + c + oc[-2:])


def build(per_train, per_val):
    rows = []
    for cls in P:
        for split, k, held in (("train", per_train.get(cls, per_train["default"]) if isinstance(per_train, dict) else per_train, False), ("val", per_val, True)):
            seen = set()
            tries = 0
            while len(seen) < k and tries < k * 30:
                tries += 1
                t = render(assemble(cls, held))
                if t not in seen:
                    seen.add(t); rows.append({"text": t, "label": cls, "split": split})
    rng.shuffle(rows)
    return rows


if __name__ == "__main__":
    import sys
    v2 = "--v2" in sys.argv
    if v2:
        merge_extra()
    out_path = "data/synth_v2.jsonl" if v2 else "data/synth.jsonl"
    rows = build({"default": 640, "genuine": 900} if v2 else 520, 100)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(out_path, len(rows), dict(collections.Counter((r["split"], r["label"]) for r in rows)))
    for r in rows[:5]:
        print("-----", r["label"]); print(r["text"][:220])
