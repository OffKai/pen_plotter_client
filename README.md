# pen_plotter_client

Socket.IO daemon that receives SVG jobs from the OffKai Phoenix coordinator and
drives an AxiDraw plotter.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start

Every client needs a routing ID: `room1` through `room5`, or `backroom`
(same slot as `room5`).

```bash
python app.py https://plotter.offkaiexpo.com --plotter-id room1
python app.py https://plotter.offkaiexpo.com --plotter-id backroom
```

The ID can be configured using CLI arguments, environment variables, or TOML:

```bash
PLOTTER_ID=room2 python app.py https://plotter.offkaiexpo.com
python app.py --config plotter.toml
```

Copy `plotter.toml.example` to `plotter.toml` for machine-local configuration:

```toml
[plotter]
id = "room2"
server_url = "https://plotter.offkaiexpo.com"
dry_run = false
```

Precedence is CLI values, an explicitly selected config file, environment
variables, `PLOTTER_CONFIG`, local `plotter.toml`, then the `room1` default.
Supported environment variables are `PLOTTER_ID`, `PLOTTER_SERVER_URL` (or
`COORDINATOR_URL`), `PLOTTER_DRY_RUN`, and `PLOTTER_CONFIG`.

## Test without hardware

`--dry-run` receives and logs SVG jobs without importing or driving AxiDraw:

```bash
python app.py http://localhost:4000 --plotter-id room1 --dry-run
python app.py http://localhost:4000 --plotter-id room2 --dry-run
python app.py http://localhost:4000 --plotter-id backroom --dry-run
```
