"""Test set C: written AFTER v2 was trained and after the leakage problem in test B was found, in new
scenarios and wording that were checked with leakage.py against every training template before scoring.
Never used to change data, thresholds or epochs. Same author as the generator, so still only partly independent:
real posts are the real test."""
G, H, F, E, U, B, S, A = ("genuine", "humblebrag", "fake_parable", "engagement_bait", "hustle_guru",
                          "buzzword_salad", "shameless_plug", "ai_thread_bro")
TEST_C = [
    # ---- genuine
    ("The pull request template we added in March cut review rounds from 3 to about 1.5. Not scientific: two teams, six months. The most useful field turned out to be 'what did you deliberately not do?'", G),
    ("Our daughter starts school on Monday and I'm dreading it more than she is. If anyone has advice for the first week, I'm all ears.", G),
    ("Sold the flat and moved to Lisbon in June. Six months on: cheaper rent, worse Wi-Fi, better lunches. The tax paperwork was by far the hardest part.", G),
    ("Correction to my post last week: I said the study had 400 participants. It had 40. Thanks to Amara for catching it. The conclusion is weaker than I made it sound.", G),
    ("Reminder for UK students: the deadline for the maintenance loan application is 22 May. It takes ten minutes if you have your NI number handy.", G),
    ("I've been a nurse for 14 years. Night shifts changed how I think about handovers: say what you're worried about first, not last. It has saved us more than once.", G),
    ("Tried explaining OAuth to my dad with a hotel key card. He got it in two minutes. I've used the analogy in three onboarding sessions since and it holds up.", G),
    ("We're a studio of five with room for one junior illustrator from September. Paid, London or remote, portfolio review only, no test task. Details on our site.", G),
    # ---- humblebrag
    ("Still catching my breath. This week our little podcast reached the top 10 in its category. Never expected it. Grateful to every listener, and to my co-host who carries me.", H),
    ("Sometimes you have to pinch yourself. A year ago I was rewriting my CV at 2am. Today I signed my dream contract. The universe is kind and I'm so thankful.", H),
    ("I don't post about personal wins, but the board voted me CEO today. Still processing. To my team: I'm just the person who holds the umbrella. You did this.", H),
    ("It's an honour to be listed alongside so many people I admire in this year's 30 under 30. I'm not sure how I got here, but I'm thankful for those who took a chance on me.", H),
    ("Just had the surreal experience of being recognised at the airport by a client. Fame is strange. Grateful that my work speaks louder than I do.", H),
    ("So this happened: my article passed 2 million views. I only wrote it because my mum asked me to. Humbled by the response and grateful to everyone who shared.", H),
    ("Delighted (and slightly terrified) to say I've been asked to advise the government on AI policy. I'm sure they've made a mistake, but I'll do my best.", H),
    ("Ten years since I started with nothing but a laptop and a dream. Today we closed our Series C. So proud of the journey and so appreciative of everyone along the way.", H),
    # ---- fake parable
    ("I was about to fire our receptionist for a rude remark. Then I found out she'd been sleeping in her car to afford her mother's care. We changed the policy that week. Lead with curiosity.", F),
    ("A boy selling lemonade on the corner refused my $50 note. 'Sir, I only have change for a five.' I gave him the fifty anyway and he handed me a receipt. Integrity has no age.", F),
    ("In my first job an old engineer fixed a broken machine by listening to it for 30 seconds. He invoiced $10,000: $1 for the fix and $9,999 for knowing where to listen. That's expertise.", F),
    ("The night before my interview my car broke down. A man in overalls fixed it for free. The next day he walked into the interview room as the hiring director. Be kind to everyone.", F),
    ("My grandfather never finished school but he'd say, 'A river cuts through rock not by force but by persistence.' I ran my company by that. We hit $50M.", F),
    ("A candidate asked what happens when the CEO is wrong. Silence. I said, 'He listens.' The candidate smiled: 'Then I'll join.' He became our best hire.", F),
    ("I gave a homeless woman my sandwich. Years later she was the investor who saved my company. Never underestimate the person in front of you.", F),
    ("Our office cleaner asked to attend a strategy meeting. Everyone laughed. He solved the logistics problem in five minutes. He'd run a warehouse for 20 years. Talent hides in plain sight.", F),
    # ---- engagement bait
    ("What's the worst interview question you've ever been asked? I'll start: 'Where do you see yourself in five years?' Your turn in the comments.", E),
    ("Poll time! Is a four-day week realistic in your industry? Yes, no, or 'in my dreams'. Reply below and repost to widen the sample.", E),
    ("Comment 'RESUME' and I'll send you my proven CV template. Like this post first so LinkedIn shows you my message!", E),
    ("Am I the only one who thinks stand-up meetings should be abolished? Let me know I'm not alone. ⬇️", E),
    ("Drop a ☕ if your day doesn't start without coffee. Tag a colleague who needs theirs.", E),
    ("Big news for everyone who wants to grow their network: connect with me and I'll follow back every single one. Like and share so others see it.", E),
    ("Which would you choose: a huge raise or unlimited holiday? Comment your pick, I'll DM my thoughts to the top 10 replies.", E),
    ("Guess the job by the tools: a hammer, a stethoscope and a spreadsheet. Best answer gets a shoutout. Repost to challenge your friends!", E),
    # ---- hustle guru
    ("Nobody cares how tired you are. Your bills don't care, your dreams don't care. Get up and work.", U),
    ("Rich mindset: I wake at 4. Poor mindset: I'll do it tomorrow. Choose your side every morning.", U),
    ("The world rewards output, not intentions. Ship the thing. Sell the thing. Repeat until they know your name.", U),
    ("Sacrifice your weekends now so you can own your weekdays later. Everyone else is busy resting.", U),
    ("You're one decision away from a different life. Stop overthinking, start executing. Discipline builds empires.", U),
    ("Every 'no' is tuition. Every failure is a lesson you paid for. Keep paying until you graduate as a winner.", U),
    ("If it were easy everyone would do it. That's why you should. Grind in silence, let success make the noise.", U),
    ("Your competition doesn't take days off. Neither should your ambition.", U),
    # ---- buzzword salad
    ("Pleased to announce a strategic realignment of our capabilities to deliver exponential, customer-centric outcomes across the value ecosystem.", B),
    ("Leveraging a mission-driven, agile mindset, we are catalysing meaningful transformation at the intersection of technology and human potential.", B),
    ("As we navigate this era of unprecedented change, our north-star vision is to empower stakeholders to co-create scalable, future-proof solutions.", B),
    ("Proud to be part of a team that's reimagining engagement through best-in-class, data-driven, omni-channel synergies.", B),
    ("The key to sustainable growth is operationalising a holistic culture of innovation, accountability and disruptive collaboration.", B),
    ("Excited to embark on a transformative journey of alignment, visibility and end-to-end enablement across our global matrix.", B),
    ("Our purpose-led framework harnesses the power of digital to unlock value, drive impact and deliver on our promise to all stakeholders.", B),
    ("Thought leadership isn't a title, it's a mindset of continuous, insight-driven, cross-functional reinvention.", B),
    # ---- shameless plug
    ("Doors open Friday for my 8-week course on cold outreach. Founding members pay half price. Reply 'IN' and I'll send the link.", S),
    ("We're looking for 3 beta customers for our new invoicing tool. Free for 3 months, then 20% off for life. Sign up at the link in the comments.", S),
    ("My book 'Ship It' is on pre-order! Order by Sunday and get the workshop recording free. Link below.", S),
    ("Need a logo, a site and a launch plan in two weeks? My studio has two slots left. Message me for a quote.", S),
    ("Join my paid community of 2,000 marketers. Weekly teardowns, job board and templates. First week free.", S),
    ("Hiring a sales lead! Great comp, great culture, huge upside. Send me a DM if you want in.", S),
    ("Just launched on Product Hunt! Please upvote us today, it would mean the world. Link in bio.", S),
    ("I'm running a free masterclass on LinkedIn growth on Tuesday at 6pm. Seats are limited. Register through the link.", S),
    # ---- ai thread bro
    ("I asked Claude to plan my whole month of content. 12 minutes. Here are the exact prompts I used (save this):", A),
    ("Everyone's sleeping on this AI trick: give the model a persona and a deadline. Watch the quality jump. Thread below.", A),
    ("9 GPT prompts that replaced my virtual assistant. #7 alone saves 5 hours a week. Copy and paste.", A),
    ("AI just wrote, designed and launched my landing page. No developer. Here's the full workflow, step by step.", A),
    ("If you're still doing research manually in 2026 you're behind. These 6 AI research tools will fix that. 🧵", A),
    ("The only 3 prompts you need to write better emails, faster. Bookmark this, thank me later.", A),
    ("I built an AI agent that answers my inbox. Here's how you can build yours in an afternoon (thread):", A),
    ("New AI tools drop every week. Here are the 5 that actually matter, and the 10 that don't. Follow to stay ahead.", A),
]

if __name__ == "__main__":
    import collections
    print(len(TEST_C), dict(collections.Counter(l for _, l in TEST_C)))
