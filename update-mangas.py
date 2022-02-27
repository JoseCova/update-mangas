#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from typing import Tuple, Optional, Dict, Any

import requests
from dotenv import load_dotenv


# TODO Meter en una clase a porque se repite mucho la url y los headers, junto con el id

# maybe change the name of the method
def setup_env() -> Tuple[Optional[str], Optional[str]]:
    """Load environmental variables from file and return them."""
    load_dotenv()
    return os.environ.get("INTEGRATION_TOKEN"), os.environ.get("DATABASE_ID")


def connect_to_database(token: str, db_id: str) -> bool:
    """Connect to the database and return its status."""

    db_url = f"https://api.notion.com/v1/databases/{db_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
        "Notion-Version": "2022-02-22",
    }

    request = requests.get(db_url, headers=headers)

    if request.status_code == 200:
        return True

    return False


def get_shonen_jump_mangas(token: str, db_id: str) -> Dict[str, Any]:
    """Query all the shonen jump mangas and return them."""
    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
        "Notion-Version": "2022-02-22",
    }

    query = {
        "filter": {
            "and": [
                {"property": "Terminada", "checkbox": {"equals": False}},
                {"property": "Revista", "select": {"equals": "Shonen Jump"}},
            ]
        }
    }

    mangas = requests.post(db_url, headers=headers, json=query)

    return mangas.json()


def update_shonen_jump_mangas(shonen_jump_mangas) -> None:
    """Update the Ultimo capitulo property."""
    print(shonen_jump_mangas)


def main():
    """Execute all the other functions."""
    token, db_id = setup_env()

    is_connection_ok = connect_to_database(token, db_id)

    # Maybe esto sobra y habrá que borrar
    if not is_connection_ok:
        print("The connection to the database gave an error, exiting the program")
        exit(1)

    shonen_jump_mangas = get_shonen_jump_mangas(token, db_id)
    update_shonen_jump_mangas(shonen_jump_mangas)


if __name__ == "__main__":
    main()
