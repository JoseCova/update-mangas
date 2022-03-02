#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from typing import Tuple, Optional, Dict, Any, List, Generator

import requests
from dotenv import load_dotenv

import argparse
import sys


# TODO Meter en una clase a porque se repite mucho la url y los headers, junto con el id


# maybe change the name of the method
def setup_env() -> Tuple[Optional[str], Optional[str]]:
    """Load environmental variables from file and return them."""
    load_dotenv()
    return os.environ.get("INTEGRATION_TOKEN"), os.environ.get("DATABASE_ID")


def get_shonen_jump_mangas(db_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Query all the shonen jump mangas and return them."""

    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"

    query = {
        "filter": {
            "and": [
                {"property": "Terminada", "checkbox": {"equals": False}},
                {"property": "Revista", "select": {"equals": "Shonen Jump"}},
            ]
        }
    }

    mangas = requests.post(db_url, headers=headers, json=query)

    return mangas.json()["results"]


def add_chapter(mangas: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
    """Add 1 to the Ultimo capi property and yield a dict with its id, new value and name."""

    # Cuando toque actualizar 1 mirar si es arr o no y hacer el rollo
    for m in mangas:
        yield {
            "page_id": m["id"],
            "updated_chapter": m["properties"]["Ultimo capi"]["number"] + 1,
            "manga_name": m["properties"]["Nombre"]["title"][0]["text"]["content"],
        }


def update_shonen_jump_mangas(
    headers: Dict[str, str], shonen_jump_mangas: Dict[str, Any]
) -> None:
    """Update the Ultimo capitulo property."""

    for sjm in add_chapter(shonen_jump_mangas):
        page_url = f"https://api.notion.com/v1/pages/{sjm['page_id']}"

        properties_to_update = {
            "properties": {"Ultimo capi": {"number": sjm["updated_chapter"]}}
        }

        request = requests.patch(page_url, headers=headers, json=properties_to_update)

        if request.status_code == 400 or request.status_code == 429:
            print(
                f"An error has occurred while updating {sjm['manga_name']}, {request.message}"
            )

        print(
            f"Last chapter property was successfully updated in manga {sjm['manga_name']}"
        )


# TODO cambiar docstring
def main():
    """Execute all the other functions."""

    parser = argparse.ArgumentParser(
        description="Update mangas DB in Notion",
        usage="To see each subcommand usage please execute python update-mangas [all-shonen-jump | update-single] -h\n",
    )
    subparsers = parser.add_subparsers()

    parse_all_shonen_jump = subparsers.add_parser(
        "all-shonen-jump",
        help="Add 1 to the Ultimo capi property to all the Shonen Jump mangas",
    )
    parse_all_shonen_jump.add_argument(
        "-i",
        "--ignore",
        help="Dont update the Ultimo capi property in the manga passed as an argument",
    )

    parse_single_manga = subparsers.add_parser(
        "single-update",
        help="Add 1 to the Ultimo capi property to the manga given as an argument",
        usage="e",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print(
            "The program must be executed with arguments, run python update_mangas -h to see them"
        )
        parser.print_help(sys.stderr)
        exit(1)

    token, db_id = setup_env()

    notion_headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
        "Notion-Version": "2022-02-22",
    }

    # shonen_jump_mangas = get_shonen_jump_mangas(db_id, notion_headers)

    # update_shonen_jump_mangas(notion_headers, shonen_jump_mangas)


if __name__ == "__main__":
    main()
