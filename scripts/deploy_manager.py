#!/usr/bin/env python3
"""
CLI equivalent of the /deploy-manager Slack command.
Triggers a deployment via the GODP (group.One Deploy Proxy) API.

REQUIREMENTS
    Python 3.8+ and the requests library:
        pip install requests

AUTH TOKEN
    A GODP auth token is required. Supply it in one of three ways (checked in order):
      1. --token flag:              python scripts/deploy_manager.py --token <token> ...
      2. Environment variable:      export TBTT_GODP_AUTH_TOKEN=<token>
      3. Interactive prompt:        the script will ask if neither of the above is set

    Never commit the token to git.

USAGE
    # All flags (non-interactive):
    python scripts/deploy_manager.py --app wpm-wprocket --env sandbox1 --commit <sha>

    # Interactive mode — omit any flag and the script prompts with a numbered list:
    python scripts/deploy_manager.py

    # With inline token:
    python scripts/deploy_manager.py --app wpm-wprocket --env sandbox2 --commit <sha> --token <token>

FLAGS
    --app      App identifier, e.g. wpm-wprocket (see full list below)
    --env      Target environment, e.g. sandbox1  (see full list below)
    --commit   Full 40-character GitHub commit SHA
    --token    GODP auth token (overrides TBTT_GODP_AUTH_TOKEN env var)

AVAILABLE APPS
    wpm-imagify-app, wpm-rucss, wpm-saas-director, wpm-monies,
    wpm-rocketcdn-app, wpm-wprocket, wpm-imagify-website, wpm-rocketcdn-website,
    wpm-backwpup-website, wpm-task-ai, wpm-wpmediame, wpm-rucss-backend,
    wpm-licenses-app, rocket-radar, wp-media-hub, wp-ai-builder

AVAILABLE ENVIRONMENTS
    staging, next, test, test1, mirror,
    sandbox1, sandbox2, sandbox3, sandbox4, sandbox5

OUTPUT
    Prints the JSON response from the GODP API on success and exits with code 0.
    Prints the error to stderr and exits with code 1 on failure.
"""
import argparse
import json
import os
import sys

import requests

GODP_DEPLOY_URL = "https://godp.wp-media.me/v1/deploy"

APPS_CONFIG = {
    "appList": {
        "Imagify App":          "wpm-imagify-app",
        "SaaS RUCSS":           "wpm-rucss",
        "SaaS Director":        "wpm-saas-director",
        "Monies":               "wpm-monies",
        "RocketCDN App":        "wpm-rocketcdn-app",
        "wp-rocket.me":         "wpm-wprocket",
        "Imagify Website":      "wpm-imagify-website",
        "RocketCDN Website":    "wpm-rocketcdn-website",
        "BackWPup Website":     "wpm-backwpup-website",
        "Task AI":              "wpm-task-ai",
        "wp-media.me":          "wpm-wpmediame",
        "RUCSS Backend":        "wpm-rucss-backend",
        "Licenses App":         "wpm-licenses-app",
        "Rocket Radar":         "rocket-radar",
        "WP Media Hub":         "wp-media-hub",
        "WordPress AI Builder": "wp-ai-builder",
    },
    "envList": {
        "staging":  "staging",
        "next":     "next",
        "test":     "test",
        "test1":    "test1",
        "mirror":   "mirror",
        "sandbox 1": "sandbox1",
        "sandbox 2": "sandbox2",
        "sandbox 3": "sandbox3",
        "sandbox 4": "sandbox4",
        "sandbox 5": "sandbox5",
    },
}


def pick_from_list(label, options: dict) -> str:
    """Prompt the user to pick a value from a labelled dict {display: value}."""
    items = list(options.items())
    print(f"\nAvailable {label}:")
    for i, (name, _) in enumerate(items, 1):
        print(f"  {i:2}. {name}")
    while True:
        raw = input(f"Select {label} (number): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(items):
            return items[int(raw) - 1][1]
        print(f"  Please enter a number between 1 and {len(items)}.")


def resolve_token(args_token: str | None) -> str:
    token = args_token or os.environ.get("TBTT_GODP_AUTH_TOKEN", "")
    if not token:
        token = input("GODP auth token (TBTT_GODP_AUTH_TOKEN): ").strip()
    if not token:
        print("Error: GODP auth token is required.", file=sys.stderr)
        sys.exit(1)
    return token


def deploy(app: str, env: str, commit: str, token: str) -> None:
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"application": app, "environment": env, "ref": commit}

    print(f"\nDeploying {app} @ {commit[:12]}... to {env}")
    try:
        response = requests.post(GODP_DEPLOY_URL, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        print(f"Error: request failed — {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        body = response.json()
    except ValueError:
        body = response.text

    if not response.ok:
        print(f"Error: GODP returned HTTP {response.status_code}", file=sys.stderr)
        print(json.dumps(body, indent=2) if isinstance(body, dict) else body, file=sys.stderr)
        sys.exit(1)

    print(json.dumps(body, indent=2) if isinstance(body, dict) else body)


def main():
    parser = argparse.ArgumentParser(description="Trigger a deployment via GODP.")
    parser.add_argument("--app", help="App identifier (e.g. wpm-wprocket)")
    parser.add_argument("--env", help="Target environment (e.g. sandbox1)")
    parser.add_argument("--commit", help="Full GitHub commit SHA")
    parser.add_argument("--token", help="GODP auth token (overrides TBTT_GODP_AUTH_TOKEN env var)")
    args = parser.parse_args()

    app_list = APPS_CONFIG["appList"]
    env_list = APPS_CONFIG["envList"]

    app = args.app
    if not app:
        app = pick_from_list("app", app_list)
    elif app not in app_list.values():
        # Accept a display name too
        if app in app_list:
            app = app_list[app]
        else:
            print(f"Error: unknown app '{app}'. Valid values: {', '.join(app_list.values())}", file=sys.stderr)
            sys.exit(1)

    env = args.env
    if not env:
        env = pick_from_list("environment", env_list)
    elif env not in env_list.values():
        if env in env_list:
            env = env_list[env]
        else:
            print(f"Error: unknown env '{env}'. Valid values: {', '.join(env_list.values())}", file=sys.stderr)
            sys.exit(1)

    commit = args.commit
    if not commit:
        commit = input("\nGitHub commit SHA: ").strip()
    if not commit:
        print("Error: commit SHA is required.", file=sys.stderr)
        sys.exit(1)

    token = resolve_token(args.token)

    deploy(app, env, commit, token)


if __name__ == "__main__":
    main()
