# JioTV Desktop (Fork)

This repository is an actively maintained fork of the archived JioTV Go project.  
It provides a modern web UI + IPTV-friendly endpoints for streaming JioTV channels using OTP login.

## What this fork includes

- Live TV playback in browser
- OTP login flow
- Playlist export for IPTV (`/playlist.m3u`)
- EPG endpoint (`/epg.xml.gz`)
- Premium provider detection (account-dependent)
- Refreshed frontend UI

## Quick start

```bash
go run main.go serve --host 127.0.0.1 --port 5001
```

Open: `http://127.0.0.1:5001`

## Build

```bash
go mod tidy
go build -o build/jiotv_go .
cd web && npm ci
cd web && npm run build
```

## Run (compiled binary)

Linux/macOS:

```bash
./build/jiotv_go serve --host 127.0.0.1 --port 5001
```

Windows (PowerShell):

```powershell
.\build\jiotv_go.exe serve --host 127.0.0.1 --port 5001
```

## Common commands

```bash
jiotv_go --help
jiotv_go serve --help
jiotv_go login --help
jiotv_go epg --help
jiotv_go background --help
```

## Key routes

- `GET /` - Web UI
- `GET /channels` - Channels JSON
- `GET /playlist.m3u` - M3U playlist
- `GET /epg.xml.gz` - EPG XML (gzipped)
- `GET /premium/providers` - Premium providers for current account

## Testing

Backend:

```bash
go test -v ./...
```

Frontend:

```bash
cd web && npm test -- --watchAll=false --ci
```

## Notes

- This fork is independent from upstream community channels and contributor metadata.
- Use only with an account that already has valid Jio service access.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).  
See [`LICENSE`](./LICENSE).
