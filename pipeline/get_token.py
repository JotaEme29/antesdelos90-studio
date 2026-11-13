#!/usr/bin/env python3
"""Ejecútalo UNA vez en tu ordenador para autorizar el canal.

  pip install google-auth-oauthlib
  python pipeline/get_token.py ruta/al/client_secret.json

Se abre el navegador, eliges la cuenta del canal @antesdelos90 y aceptas.
Al terminar imprime los 3 valores que tienes que guardar como secretos en GitHub
(Settings → Secrets and variables → Actions → New repository secret).
No los pegues en ningún chat.
"""
import json, sys
from google_auth_oauthlib.flow import InstalledAppFlow
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from yt import SCOPES

if len(sys.argv) < 2: raise SystemExit(__doc__)
flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
cred = flow.run_local_server(port=0, access_type="offline", prompt="consent")
info = json.load(open(sys.argv[1])); c = info.get("installed") or info.get("web")
print("\nGuarda estos 3 secretos en GitHub:\n")
print("YT_CLIENT_ID     =", c["client_id"])
print("YT_CLIENT_SECRET =", c["client_secret"])
print("YT_REFRESH_TOKEN =", cred.refresh_token)
