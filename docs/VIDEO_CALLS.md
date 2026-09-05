# Hive video calls

Hive chat and sent mail now use the backend from /home/mike/projects/zoom-clone.
Hive authorizes the current conversation/mail membership before making a signed
server-to-server request. The clone issues five-minute LiveKit credentials
restricted to a tenant-scoped Hive room. Clone meeting rooms remain separate.

## Local operation

From hive-os-infra:
```sh
python3 scripts/setup-video.py
docker compose up -d --build video-backend video-media
docker exec hive-backend php artisan octane:reload --no-ansi
```

Private settings are in .video/backend.env, .video/livekit.yaml and the Hive
backend .env. Do not commit these files. The media endpoint is
ws://127.0.0.1:17880; TCP media uses 17881 and UDP uses 50100–50120.
These are loopback-only local settings. Other computers/production require a
reachable media hostname, HTTPS/WSS, appropriate ICE/TURN configuration and
explicit network deployment. Do not simply expose the development secrets.

Open a conversation or sent mail, select Video call, then Join call. Other
members open the same item to join; the button detects active rooms every
15 seconds while the page is visible. This version does not send ringing
notifications or external email invitations. Camera/microphone start off;
enable them explicitly. Screen sharing uses the browser picker. Escape,
Close, Leave call and navigation disconnect and stop local tracks.
Message end-to-end encryption does not apply to calls; media uses encrypted transport.

## Verification

- Zoom backend TypeScript build and all nine bridge, meeting-access and OAuth tests passed.
- Bridge test rejects missing, stale, tampered signatures and non-Hive rooms.
- Eight isolated Hive tests passed: room scope isolation, exact signatures,
  disabled service, allowed member, outsiders, drafts and deleted membership.
- Frontend TypeScript and video component ESLint passed.
- Six text/focus/tile contrast checks passed.
- Live signed status and media token issuance verified.
- Signed-in chat and sent-mail dialogs connected to LiveKit; Escape closed chat and returned focus.
- Physical camera/microphone and multi-device media remain user acceptance checks.

Existing unrelated changes in all repositories were preserved. No database
migrations or message/email dispatch is required by this integration.

## Compose ownership

Video services are part of the main hive-os-infra project as video-backend and video-media. The pre-existing hive-video_video-data volume is reused explicitly as an external volume; its name is retained to preserve data. The Zoom backend source remains in its original repository.

## Source and prerequisites

Clone https://github.com/Techiveet/zoom_clone into the sibling `../../zoom-clone` directory (relative to hive-os-infra). Run setup from WSL with Python 3 and Docker Compose v2. Setup creates local secrets only when absent, connects the Hive backend environment, and creates the named volume if needed. It preserves existing video credentials and data. Never commit `.env`, `.video`, or database backups. After changing environment settings, clear cached Laravel configuration before reloading Octane.

The optional `docker-compose.local-monitoring.yml` removes host backend/Reverb port bindings on this workstation, where other services own those ports. Use it only with an existing frontend proxy that reaches those services over the Docker network.
