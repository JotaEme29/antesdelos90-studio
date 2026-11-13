"""Conexión con YouTube usando los secretos del repositorio (nunca en archivos)."""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]

def creds():
    miss = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if miss: raise SystemExit(f"Faltan secretos: {', '.join(miss)}")
    return Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                       client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)

def youtube(): return build("youtube", "v3", credentials=creds(), cache_discovery=False)
def analytics(): return build("youtubeAnalytics", "v2", credentials=creds(), cache_discovery=False)
