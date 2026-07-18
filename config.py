import argparse
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    server_url: str
    plotter_id: str
    dry_run: bool


def parse_settings(argv: list[str] | None = None) -> Settings:
    parser = argparse.ArgumentParser(description="Run an OffKai pen plotter client.")
    parser.add_argument("server_url", nargs="?", help="Phoenix coordinator URL")
    parser.add_argument(
        "-i",
        "--plotter-id",
        help="Routing ID (room1 through room5, or backroom)",
    )
    parser.add_argument("-c", "--config", type=Path, help="Path to a TOML config file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Receive and log plots without driving AxiDraw hardware",
    )
    args = parser.parse_args(argv)

    config_path, explicit_config = _config_path(args.config)
    file_values = _load_config(config_path, required=explicit_config)

    plotter_id = (
        args.plotter_id
        or file_values.get("id")
        if explicit_config
        else args.plotter_id or os.getenv("PLOTTER_ID") or file_values.get("id")
    )

    if not plotter_id:
        plotter_id = "room1"
        print(
            "Warning: no plotter ID configured; defaulting to room1.",
            file=sys.stderr,
        )

    server_url = (
        args.server_url
        or file_values.get("server_url")
        if explicit_config
        else args.server_url
        or os.getenv("PLOTTER_SERVER_URL")
        or os.getenv("COORDINATOR_URL")
        or file_values.get("server_url")
    )

    if not server_url:
        parser.error(
            "server URL required as an argument, config value, "
            "PLOTTER_SERVER_URL, or COORDINATOR_URL"
        )

    dry_run = (
        args.dry_run
        or _as_bool(file_values.get("dry_run"))
        if explicit_config
        else args.dry_run
        or _as_bool(os.getenv("PLOTTER_DRY_RUN"))
        or _as_bool(file_values.get("dry_run"))
    )

    return Settings(
        server_url=str(server_url),
        plotter_id=str(plotter_id),
        dry_run=dry_run,
    )


def _config_path(cli_path: Path | None) -> tuple[Path | None, bool]:
    if cli_path:
        return cli_path, True

    if env_path := os.getenv("PLOTTER_CONFIG"):
        return Path(env_path), False

    local_path = Path("plotter.toml")
    return (local_path, False) if local_path.exists() else (None, False)


def _load_config(path: Path | None, required: bool) -> dict[str, Any]:
    if path is None:
        return {}

    if not path.exists():
        if required:
            raise SystemExit(f"Config file not found: {path}")
        return {}

    with path.open("rb") as config_file:
        data = tomllib.load(config_file)

    plotter = data.get("plotter", {})
    if not isinstance(plotter, dict):
        raise SystemExit(f"Invalid [plotter] section in {path}")

    return plotter


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return False
