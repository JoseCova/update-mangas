#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from dotenv import load_dotenv
import os


def setup_env():
    """Load environmental variables from file and return them."""
    load_dotenv()
    return os.environ.get("INTEGRATION_TOKEN"), os.environ.get("DATABASE_ID")


def main():
    """Execute all the other functions."""
    token, db_id = setup_env()
    print(token, db_id)


if __name__ == "__main__":
    main()
