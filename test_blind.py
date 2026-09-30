"""BLIND test set B. Written before v2's data changes and NOT scored until v2 training finished, so no
template, threshold or epoch was tuned against it. Still written by the same author as the generator,
so it is only a partly independent test: real posts are the real test."""
G, H, F, E, U, B, S, A = ("genuine", "humblebrag", "fake_parable", "engagement_bait", "hustle_guru",
                          "buzzword_salad", "shameless_plug", "ai_thread_bro")
TEST_B = [
    # ---- genuine (deliberately diverse: gratitude, job search, teaching, health, small talk, technical, bad news)
    ("Our nonprofit's food drive collected 3,214 kg last weekend, about double last year. Thanks to the volunteers from the two local schools, and to Mr. Okafor for lending us the van.", G),
    ("I got laid off on Tuesday. 7 years, the whole product org. I'm going to take a week, then start looking at data roles in logistics. If you know a team that needs someone who can clean ugly data, I'd love an intro.", G),
    ("Teaching tip that worked for my Year 9 class: I stopped grading homework and started grading corrections to it. Completion went from 60% to nearly everyone, and the questions got better.", G),
    ("Ran my first half marathon on Sunday. 2:14. Not fast, but I walked at km 16 and still finished. Thanks to everyone who dragged me out at 6am all winter.", G),
    ("Postgres tip: EXPLAIN (ANALYZE, BUFFERS) shows you which part of the plan hit disk. We found one sequential scan that accounted for 80% of a 3-second query. The fix was an index on two columns, in that order.", G),
    ("Reminder that our office will be closed on Monday for the public holiday. Support tickets will be answered Tuesday morning. Urgent issues: use the phone line in the footer.", G),
    ("Has anyone else found that async standups quietly turn into status reports? We tried a weekly written 'what changed my mind' note instead. Two months in, people actually read it.", G),
    ("My mum was in hospital for a week and I learned how little most companies' bereavement and carer policies say. Ours changed after I asked. Sharing the template in case it's useful.", G),
    # ---- humblebrag
    ("Woke up this morning to the news that our team's paper won Best Paper at the conference. Honestly stunned. I just do the work I love, and somehow it keeps being noticed. So thankful for this journey.", H),
    ("Just a casual reminder that four years ago I was sleeping on a friend's couch. Today I was invited to ring the closing bell. Life has a funny way. Deeply humbled and grateful for every single one of you.", H),
    ("Big things happening. I can't say much yet, but I'll just say that the last 6 months have been the most incredible of my career. Feeling blessed and so grateful to those who believed in me.", H),
    ("I usually avoid talking about awards, but this one is special. Named to the 2026 list of Women to Watch in Tech. To everyone who ever doubted me: thank you for the motivation. 🙏", H),
    ("Honoured to have been asked by three different universities to give guest lectures this fall. Still so surprised anyone wants to hear from me. Grateful. Humbled. Ready to learn.", H),
    ("Life update: I became a partner today. I don't say this to brag, I say it because 10 years ago no one would have bet on me. To my mentors: I owe you everything.", H),
    ("I'm thrilled to share that my startup was just featured in Forbes. What a ride! I'm still that same kid who fixed neighbours' computers. Thank you to my incredible community.", H),
    ("Quietly proud to announce I passed the bar on the first attempt, top 5% of my cohort. It's been an unforgettable journey and I'm so appreciative of my family and friends.", H),
    # ---- fake parable
    ("My father-in-law never said much. When I told him I was quitting my job to start a company, he handed me an envelope. Inside was a photo of his first shop, and a note: 'Fear is just excitement without the breathing.' I cried in the car.", F),
    ("A new hire spilled coffee on our CEO's laptop. Everyone froze. The CEO laughed and said, 'Great. Now I finally have an excuse to buy a new one.' That's the day I understood what culture is.", F),
    ("I sat next to an elderly woman on a 6-hour flight who knitted the whole time. As we landed, she said, 'Stitch by stitch, dear. Everything is stitch by stitch.' I've never forgotten it. She sold her yarn company for $200M.", F),
    ("The cleaner at my first office used to say good morning to everyone by name. When our company went under, he was the only one who checked on me. Turns out he owned three buildings. Kindness pays off.", F),
    ("An intern once corrected me in front of the whole team. My first instinct was to be angry. I thanked her instead. She now runs our product org. Never punish honesty.", F),
    ("My 8-year-old came home with a C and shrugged. 'It's okay, Dad. I tried my best.' I've never felt smaller. Success is not a grade.", F),
    ("I rejected a candidate because his shoes were scuffed. Two years later, he became my biggest client. He never mentioned it. Judge less. Listen more.", F),
    ("A stranger returned my daughter's toy in the rain and refused any thanks. 'Someone did it for me once,' he said. I think about him every day when I hire.", F),
    # ---- engagement bait
    ("Which is harder: managing up or managing down? Vote below and I'll share the results next week!", E),
    ("Everyone talks about work-life balance, but nobody talks about this: does your boss reply to emails on Sunday? Yes or no. Let's see the numbers. 👇", E),
    ("Comment 'PLAYBOOK' and I'll send you the full sales playbook in your DMs. Repost to help a friend get their next role. ♻️", E),
    ("If you agree that recruiters should always share the salary range, give this a like. If you disagree, tell me why in the comments.", E),
    ("Tag your favourite manager below. Let's spread some positivity today! 💙", E),
    ("Only real ones remember the days of dial-up. Drop a 🙋 if you do.", E),
    ("Do you check email first thing in the morning? Be honest, no judgement. Comment 1 for yes, 2 for no.", E),
    ("I'm going to ask the question nobody asks: what is your one non-negotiable at work? Share your answer and follow for more career content.", E),
    # ---- hustle guru
    ("The alarm goes off at 4:45. Not because I want to. Because I said I would. That's the whole difference between people who talk about their goals and people who reach them.", U),
    ("No one remembers who slept in. They remember who showed up when it was cold, dark and inconvenient. Be the one who shows up.", U),
    ("You don't have a time problem. You have a priorities problem. Everyone gets 24 hours. Winners simply refuse to waste them.", U),
    ("Success is rented, and the rent is due every day. Pay it with sweat, early mornings and saying no to everything that doesn't matter.", U),
    ("They'll call you obsessed until you win. Then they'll call you lucky. Keep working.", U),
    ("Comfort is the silent killer of ambition. Cold plunge, cold call, cold coffee. Get uncomfortable or get left behind.", U),
    ("While they were on holiday, I was building. While they were complaining, I was closing. Same 24 hours, different outcomes.", U),
    ("Stop waiting for motivation. Motivation is a mood. Discipline is a decision. Decide.", U),
    # ---- buzzword salad
    ("Delighted to share that our team has successfully operationalised a bold, scalable framework for the seamless orchestration of cross-functional synergies in the digital-first value chain.", B),
    ("The future belongs to organisations that can harness agility, unlock human potential and re-imagine stakeholder engagement through a data-driven, purpose-led transformation lens.", B),
    ("In today's disruptive landscape, thought leadership is about leveraging holistic insights to catalyse meaningful, outcome-focused change at scale.", B),
    ("Thrilled to step into my new role as Lead, Strategic Value Enablement, where I will champion best-in-class, innovation-driven solutions across the enterprise ecosystem.", B),
    ("It's time to double down on our core competencies while pivoting towards a frictionless, insight-led, customer-obsessed operating paradigm.", B),
    ("We are proud to partner with forward-thinking leaders to deliver mission-critical, end-to-end transformation and unlock exponential value for all stakeholders.", B),
    ("Synergising cross-functional capabilities to accelerate our journey towards a resilient, future-ready, digitally-enabled organisation. #transformation", B),
    ("Innovation is a journey, not a destination. Empowering teams to think outside the box and leverage disruptive technologies to move the needle.", B),
    # ---- shameless plug
    ("My agency has 3 openings for June. We do LinkedIn ghostwriting for B2B founders. First month is 30% off if you book this week. Message me.", S),
    ("Launching tomorrow: The Notion Operating System for Solo Founders. 40 templates, 6 hours of video, lifetime updates. Early-bird price ends at midnight.", S),
    ("Hiring! We're a fast-growing startup looking for a growth marketer who wants to 10x their career. Amazing team, equity, unlimited PTO. DM me your CV.", S),
    ("Just released my new ebook 'Close More Deals in 30 Days'. Grab your copy at the link in my bio. Bonus: free call for the first 20 buyers.", S),
    ("Struggling to get leads? We book 25 qualified meetings a month for SaaS companies or you don't pay. Apply for a free audit today.", S),
    ("New episode of my podcast is out! This week: how I built a 7-figure agency. Listen on Spotify, Apple and YouTube, and don't forget to subscribe.", S),
    ("Our webinar 'AI for Sales Teams' is next Thursday. Free to attend, limited seats. Register now via the link below.", S),
    ("I'm opening 5 spots in my coaching program this quarter. If you're serious about leadership, book a discovery call. Serious applicants only.", S),
    # ---- ai thread bro
    ("I spent 100 hours testing every AI tool so you don't have to. Here are the only 5 you need. Save this post. 🧵", A),
    ("ChatGPT is not a search engine. Here's the 4-step prompt framework that gets you 10x better answers (steal it):", A),
    ("AI won't take your job. Someone using AI will. Here are 8 tools that will make you that someone. Thread 👇", A),
    ("Anthropic, OpenAI and Google are fighting. The real winners are people who know these 6 prompts. Copy them.", A),
    ("Nobody is talking about this AI workflow that saves 15 hours a week. Here it is, step by step. Bookmark this.", A),
    ("I built a full website in 10 minutes using only AI. No code. Here's exactly how (with prompts):", A),
    ("Stop writing emails manually. These 7 AI tools will do it for you. Number 4 blew my mind. 🤯", A),
    ("The AI cheat sheet I wish I'd had a year ago: 12 prompts for marketing, sales and hiring. Retweet to save it.", A),
]

if __name__ == "__main__":
    import collections
    print(len(TEST_B), dict(collections.Counter(l for _, l in TEST_B)))
