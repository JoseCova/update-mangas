#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from typing import Tuple, Optional

import requests
from dotenv import load_dotenv


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
        "Notion-Version": "2021-08-16",
    }

    request = requests.get(db_url, headers=headers)

    if request.status_code == 200:
        return True

    return False


def main():
    """Execute all the other functions."""
    token, db_id = setup_env()

    connect_to_database(token, db_id)


if __name__ == "__main__":
    main()
