import feedparser, os, requests
import resend

resend.api_key    = os.environ["RESEND_API_KEY"]
NOTIFY_EMAIL      = os.environ["NOTIFY_EMAIL"]
FOUND_FLAG        = os.environ.get("FOUND_FLAG", "0")
RENDER_API_KEY    = os.environ["RENDER_API_KEY"]
RENDER_SERVICE_ID = os.environ["RENDER_SERVICE_ID"]

FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvC4D8onUfXzvjTOM-dBfEA",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC1IYaUJRMSqEQnpd1Rsd3aA",
]
KEYWORDS = ["doomsday", "doom", "avengers", "trailer"]

# Kill switch — already found it, stop all future runs
if FOUND_FLAG == "1":
    print("FOUND_FLAG is 1 — trailer already found. Exiting.")
    exit(0)

def set_flag_to_1():
    """Updates FOUND_FLAG=1 on Render via API so future runs are paused."""
    url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/env-vars"
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    # Fetch current env vars first
    current = requests.get(url, headers=headers).json()
    # Update FOUND_FLAG to 1
    updated = [
        {"key": v["key"], "value": "1" if v["key"] == "FOUND_FLAG" else v["value"]}
        for v in current
    ]
    requests.put(url, headers=headers, json=updated)
    print("FOUND_FLAG set to 1 on Render.")

def send_email(title, url):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": NOTIFY_EMAIL,
        "subject": f"MARVEL DROP: {title}",
        "text": f"Doomsday trailer detector fired!\n\n{title}\n\n{url}"
    })
    print(f"Email sent: {title}")

for feed_url in FEEDS:
    for entry in feedparser.parse(feed_url).entries:
        title = entry.title.lower()
        if any(kw in title for kw in KEYWORDS):
            print(f"MATCH: {entry.title}")
            send_email(entry.title, entry.link)
            set_flag_to_1()
            exit(0)

print("No match found this run.")