import json
import os

STATE_FILE = "app_state.json"

def save_state(liked, playlists):
    with open(STATE_FILE, "w") as f:
        json.dump({
            "liked": list(liked),
            "playlists": playlists
        }, f)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("liked", [])), data.get("playlists", {})
    return set(), {}