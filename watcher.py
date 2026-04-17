import feedparser, smtplib, os, json
from email.mime.text import MIMEText

YOUR_EMAIL   = os.environ["YOUR_EMAIL"]
APP_PASSWORD = os.environ["APP_PASSWORD"]
NOTIFY_EMAIL = os.environ["NOTIFY_EMAIL"]
SEEN_FILE    = "/data/seen_ids.json"   # /data is a persistent disk on Render

FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvC4D8onUfXzvjTOM-dBfEA",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC1IYaUJRMSqEQnpd1Rsd3aA",
]
KEYWORDS = ["doomsday", "doom", "avengers", "trailer"]

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_email(title, url):
    msg = MIMEText(f"Doomsday trailer detector fired!\n\n{title}\n\n{url}")
    msg["Subject"] = f"MARVEL DROP: {title}"
    msg["From"] = YOUR_EMAIL
    msg["To"] = NOTIFY_EMAIL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(YOUR_EMAIL, APP_PASSWORD)
        s.send_message(msg)
    print(f"Email sent: {title}")

seen = load_seen()
for feed_url in FEEDS:
    for entry in feedparser.parse(feed_url).entries:
        vid_id = entry.get("yt_videoid", entry.id)
        title  = entry.title.lower()
        if vid_id in seen:
            continue
        seen.add(vid_id)
        if any(kw in title for kw in KEYWORDS):
            send_email(entry.title, entry.link)
            print(f"MATCH: {entry.title}")
        else:
            print(f"No match: {entry.title}")

save_seen(seen)