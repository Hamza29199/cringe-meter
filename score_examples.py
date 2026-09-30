"""Score candidate demo posts on the running local server (python score_examples.py). Read-only."""
import json, sys, urllib.request

GENUINE = [
    "We switched our deploys from Fridays to Tuesdays. Incidents dropped by about a third. The only real cost was some grumbling.",
    "Looking for a part-time bookkeeper for our five-person studio in Leeds. About 6 hours a week, paid, remote is fine. Email us via the site.",
    "Thanks to everyone who came to Thursday's meetup. We ran out of chairs, which is a nice problem. Slides are on the group page.",
    "Debugging tip: if a test only fails on CI, diff the environment variables before you touch the code. Ours was a timezone.",
    "I got the timeline wrong in my last post: the migration took 9 weeks, not 6. Thanks to Sam for spotting it.",
    "Just finished a book on logistics that I expected to be dull. It wasn't. The chapter on container standards is worth the price alone.",
]
CRINGE = [
    "Humbled and honored to announce I've been named a Top 40 Under 40. I'm just a small-town kid who got lucky. 🙏",
    "I fired an intern for being late. Then he handed me his phone. On it was my own résumé. Be kind to everyone.",
    "Agree? Comment 'YES' and I'll DM you my free template. Repost to help a friend. ♻️",
    "Nobody is coming to save you. Wake up at 5AM. Outwork everyone. Discipline beats talent.",
    "Excited to leverage holistic, best-in-class synergies to unlock scalable value across the digital ecosystem.",
    "10 AI tools that will replace your job (thread 🧵). Save this post. Follow for more.",
    "Only 3 spots left in my course! First 50 buyers get 40% off. Link in bio.",
]


def score(text):
    req = urllib.request.Request("http://127.0.0.1:8780/score", data=json.dumps({"text": text}).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for name, posts in (("GENUINE", GENUINE), ("CRINGE", CRINGE)):
        print(f"--- {name}")
        for t in posts:
            r = score(t)
            print(f"{(1 - r['probs']['genuine']) * 100:3.0f}% cringe  {r['top']:16s} {r['ms']:4d}ms | {t[:70]}")
