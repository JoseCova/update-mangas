#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from dotenv import load_dotenv
from typing import Tuple, Optional
import os


# maybe change the name of the method
def setup_env() -> Tuple[Optional[str], Optional[str]]:
    """Load environmental variables from file and return them."""
    load_dotenv()
    return os.environ.get("INTEGRATION_TOKEN"), os.environ.get("DATABASE_ID")


def connect_to_database(token: str, db_id: str) -> None:
    """Connect to the database and return its status."""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
        "Notion-Version": "2021-08-16",
    }


def main():
    """Execute all the other functions."""
    token, db_id = setup_env()


if __name__ == "__main__":
    main()
