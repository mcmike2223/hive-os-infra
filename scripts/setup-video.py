#!/usr/bin/env python3
"""Configure loopback-only Hive video without replacing existing credentials."""
import os
from pathlib import Path
import secrets
import subprocess

infra = Path(__file__).resolve().parents[1]
private = infra / ".video"
hive_env = infra.parent / "hive-os-backend" / ".env"
if not hive_env.is_file():
    raise SystemExit("Configure hive-os-backend/.env first.")
private.mkdir(mode=0o700, exist_ok=True)
os.chmod(private, 0o700)
backend = private / "backend.env"
media = private / "livekit.yaml"
if backend.exists() != media.exists():
    raise SystemExit("Incomplete .video configuration: restore the missing file; existing credentials were preserved.")
if not backend.exists():
    shared, api_secret = secrets.token_hex(32), secrets.token_hex(32)
    values = {
        "PORT": "5001", "NODE_ENV": "production",
        "AUTH_TOKEN_SECRET": secrets.token_hex(32),
        "BILLING_WEBHOOK_SECRET": secrets.token_hex(32),
        "HIVE_VIDEO_SECRET": shared,
        "LIVEKIT_API_KEY": "hivevideo", "LIVEKIT_API_SECRET": api_secret,
        "LIVEKIT_HTTP_URL": "http://hive-video-media:7880",
        "LIVEKIT_WS_URL": "ws://127.0.0.1:17880",
        "ALLOWED_ORIGINS": "http://127.0.0.1:3001,http://localhost:3001",
    }
    with backend.open("x") as f:
        os.chmod(backend, 0o600)
        f.write("".join(f"{key}={value}\n" for key, value in values.items()))
    with media.open("x") as f:
        os.chmod(media, 0o600)
        f.write(f"""port: 7880
bind_addresses: ["0.0.0.0"]
keys:
  hivevideo: {api_secret}
rtc:
  node_ip: 127.0.0.1
  use_external_ip: false
  tcp_port: 17881
  port_range_start: 50100
  port_range_end: 50120
""")
values = dict(line.split("=", 1) for line in backend.read_text().splitlines()
              if "=" in line and not line.startswith("#"))
shared = values.get("HIVE_VIDEO_SECRET", "")
if len(shared) < 32:
    raise SystemExit("Existing HIVE_VIDEO_SECRET must contain at least 32 characters.")
settings = {
    "HIVE_VIDEO_ENABLED": "true",
    "HIVE_VIDEO_BACKEND_URL": "http://hive-video-backend:5001",
    "HIVE_VIDEO_SECRET": shared,
}
lines = hive_env.read_text().splitlines()
updated = [line for line in lines if line.split("=", 1)[0] not in settings]
updated.extend(f"{key}={value}" for key, value in settings.items())
hive_env.write_text("\n".join(updated) + "\n")
subprocess.run(["docker", "volume", "create", "hive-video_video-data"], check=True, stdout=subprocess.DEVNULL)
print("Private video configuration ready; existing video credentials and volume preserved.")
print("Run docker compose up -d --build video-backend video-media, then reload Hive Octane.")
