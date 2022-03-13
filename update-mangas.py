#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from typing import Tuple, Optional, Dict, Any, List, Generator, NamedTuple

import requests
from dotenv import load_dotenv

import argparse
import sys

from tabulate import tabulate


def check_arguments_were_passed() -> bool:
    """Check if arguments where passed through command line."""

    if len(sys.argv) > 1:
        return True

    return False


def get_token_and_id() -> Tuple[Optional[str], Optional[str]]:
    """Load environmental variables from file and return them."""

    load_dotenv()
    return os.environ.get("INTEGRATION_TOKEN"), os.environ.get("DATABASE_ID")


def setup_argparse() -> NamedTuple:
    """Declare the argument parser and return its arguments."""

    parser = argparse.ArgumentParser(
        description="Update mangas DB in Notion",
        usage="To see each subcommand usage please execute python update-mangas [all-shonen-jump | update-single | finished] -h.\n",
    )

    subparsers = parser.add_subparsers(dest="command")

    parse_all_shonen_jump = subparsers.add_parser(
        "all-shonen-jump",
        help="Add 1 to the Ultimo capi property to all the Shonen Jump mangas",
        usage="python update-mangas all-shonen-jump [flags]\nPlease when using the -i flag if the name of the manga to be ignored is made up of words separated by spaces, introduce it but separated by hyphens\nEx: One Piece❌  One-Piece✔️",
    )
    parse_all_shonen_jump.add_argument(
        "-i",
        "--ignore",
        help="Don't update the Ultimo capi property in the manga passed as an argument",
    )

    parse_single_manga = subparsers.add_parser(
        "update-single",
        help="Add 1 to the Ultimo capi property to the manga given as an argument",
        usage="python update-mangas single-update [manga-name]\nPlease if the manga name is made up of words separated by spaces, introduce it but separated by hyphens\nEx: One Piece❌  One-Piece✔️",
    )

    parse_single_manga.add_argument(
        "manga_name",
        help="Name of the manga that will have its property updated",
        type=str,
    )

    parse_mark_as_finished = subparsers.add_parser(
        "finished",
        help="Mark as finished the manga passed as a parameter (Therefore it won't be showed in the Notion page)",
        usage="python update-mangas finished [manga-name]]\nPlease if the manga name is made up of words separated by spaces, introduce it but separated by hyphens.\nEx: One Piece❌  One-Piece✔️",
    )

    parse_mark_as_finished.add_argument(
        "manga_name",
        help="The name of the manga that will have its property updated",
        type=str,
    )

    parse_list_manga = subparsers.add_parser(
        "list",
        help="List all the mangas in the database.",
        usage="python update-mangas list",
    )

    args = parser.parse_args()

    return args


def get_shonen_jump_mangas(
    db_id: str, headers: Dict[str, str], ignored_manga: Optional[str] = None
) -> Dict[str, Any]:
    """Query all the shonen jump mangas and return them."""

    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"

    if not ignored_manga:
        query = {
            "filter": {
                "and": [
                    {"property": "Terminada", "checkbox": {"equals": False}},
                    {"property": "Revista", "select": {"equals": "Shonen Jump"}},
                ]
            }
        }

        request = requests.post(db_url, headers=headers, json=query)

        if request.status_code == 200:
            return request.json()["results"]

        print(
            f"An error has occurred while querying {request.status_code}, {request.json()}"
        )

    query = {
        "filter": {
            "and": [
                {"property": "Terminada", "checkbox": {"equals": False}},
                {"property": "Revista", "select": {"equals": "Shonen Jump"}},
                {"property": "Nombre", "title": {"does_not_equal": f"{ignored_manga}"}},
            ]
        }
    }
    request = requests.post(db_url, headers=headers, json=query)

    if request.status_code == 200:
        return request.json()["results"]

    print(
        f"An error has occurred while querying {request.status_code}, {request.json()}"
    )


def update_mangas(headers: Dict[str, str], mangas: Dict[str, Any]) -> None:
    """Update the Ultimo capitulo property."""

    for m in add_chapter(mangas):
        page_url = f"https://api.notion.com/v1/pages/{m['page_id']}"

        properties_to_update = {
            "properties": {"Ultimo capi": {"number": m["updated_chapter"]}}
        }

        request = requests.patch(page_url, headers=headers, json=properties_to_update)

        if request.status_code >= 400:
            print(
                f"An error has occurred while updating {m['manga_name']}\n {request.json()}"
            )

        print(
            f"Last chapter property was successfully updated in manga {m['manga_name']}"
        )


def add_chapter(mangas: List[Dict[str, Any]]) -> Generator[Dict[str, Any], None, None]:
    """Add 1 to the Ultimo capi property and yield a dict with its id, new value and name."""

    for m in mangas:
        yield {
            "page_id": m["id"],
            "updated_chapter": m["properties"]["Ultimo capi"]["number"] + 1,
            "manga_name": m["properties"]["Nombre"]["title"][0]["text"]["content"],
        }


def get_single_manga(
    db_id: str, headers: Dict[str, str], manga_name: str
) -> Dict[str, Any]:
    """Query a single manga from the DB."""

    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"

    query = {"filter": {"property": "Nombre", "title": {"equals": f"{manga_name}"}}}

    request = requests.post(db_url, headers=headers, json=query)

    if request.status_code == 200:
        return request.json()["results"]

    print(f"An error has occurred {request.status_code}, {request.json()}")


def mark_manga_as_finished(manga: Dict[str, Any], headers: Dict[str, str]) -> None:
    """Update the manga property 'Terminada'."""

    page_url = f"https://api.notion.com/v1/pages/{manga['id']}"

    properties_to_update = {"properties": {"Terminada": {"checkbox": True}}}

    request = requests.patch(page_url, headers=headers, json=properties_to_update)

    if request.status_code != 200:
        print(
            f"An error has occurred while updating {manga['Nombre']['title'][0]['text']['content']}\n {request.json()} "
        )

    print(
        f"Terminada property was successfully updated in manga {manga['Nombre']['title'][0]['text']['content']}"
    )


def list_mangas(headers: Dict[str, str], db_id: str) -> None:
    """Display all the mangas in the DB as a table."""

    mangas = [manga for manga in query_all_mangas(headers, db_id)]
    print(f"{ '-' * 55} MANGAS {'-' * 58}")
    print(tabulate(mangas, tablefmt="github"))


def query_all_mangas(
    headers: Dict[str, str], db_id: str
) -> Generator[List[str], None, None]:
    """Query all the mangas of the database and yield them in a List of size 3."""

    db_url = f"https://api.notion.com/v1/databases/{db_id}/query"

    query = {"filter": {"property": "Terminada", "checkbox": {"equals": False}}}

    request = requests.post(db_url, headers=headers, json=query)

    if request.status_code == 200:

        manga_names = [
            m["properties"]["Nombre"]["title"][0]["text"]["content"]
            for m in request.json()["results"]
        ]

        # list of 3 elements
        for i in range(0, len(manga_names), 4):
            yield manga_names[i : i + 4]
    else:
        print(f"An error has occurred while querying all the mangas\n {request.json()}")


# noinspection PyUnresolvedReferences
def main():
    """Execute all the other functions."""

    if not check_arguments_were_passed():
        print(
            "The program must be executed with arguments, run python update_mangas -h to see them"
        )
        argparse.ArgumentParser(
            usage="To see each subcommand usage please execute python update-mangas [all-shonen-jump | update-single | finished | list] -h.\n"
        ).print_help(sys.stderr)
        exit(1)

    token, db_id = get_token_and_id()

    notion_headers = {
        "Authorization": f"Bearer {token}",
        "Content-type": "application/json",
        "Notion-Version": "2022-02-22",
    }

    args = setup_argparse()

    match args.command:
        case "all-shonen-jump":
            if args.ignore:
                swap_hyphen_for_space = args.ignore.replace("-", " ")
                shonen_jump_mangas = get_shonen_jump_mangas(
                    db_id, notion_headers, swap_hyphen_for_space
                )
                update_mangas(notion_headers, shonen_jump_mangas)
            else:
                shonen_jump_mangas = get_shonen_jump_mangas(db_id, notion_headers)
                update_mangas(notion_headers, shonen_jump_mangas)
        case "update-single":
            swap_hyphen_for_space = args.manga_name.replace("-", " ")
            manga = get_single_manga(db_id, notion_headers, swap_hyphen_for_space)
            update_mangas(notion_headers, manga)
        case "finished":
            swap_hyphen_for_space = args.manga_name.replace("-", " ")
            manga = get_single_manga(db_id, notion_headers, swap_hyphen_for_space)[0]
            mark_manga_as_finished(manga, notion_headers)
        case "list":
            list_mangas(notion_headers, db_id)


if __name__ == "__main__":
    main()
