"""
Fonctions de génération des cartes avec le bon dos et le bon nombre d'exemplaires
"""

import helper_files
import infos
import os

def generate_heroes(extension: dict, root_pictures: os.path, back: os.path) -> list:
    result: list = []
    heroes: list = extension[infos.EXTENSION_HEROES]
    for hero in heroes:
        result.append({infos.CARDS_FACE_A: os.path.join(root_pictures, hero), \
                        infos.CARDS_FACE_B: back, \
                        infos.CARDS_EXEMPLAIRES: 1})
    return result


def generate_players(extension: dict, root_pictures: os.path, back: os.path) -> list:
    result: list = []
    players: list = extension[infos.EXTENSION_PLAYERS]
    for player in players:
        # chaque carte est en fois 3
        result.append({infos.CARDS_FACE_A: os.path.join(root_pictures, player), \
                        infos.CARDS_FACE_B: back, \
                        infos.CARDS_EXEMPLAIRES: 3})
    return result


def generate_contracts(extension: dict, root_pictures: os.path, back: os.path) -> list:
    result: list = []
    contracts: list = extension[infos.EXTENSION_CONTRACTS]
    for contract in contracts:
        # chaque carte est en fois 4
        result.append({infos.CARDS_FACE_A: os.path.join(root_pictures, contract), \
                        infos.CARDS_FACE_B: back, \
                        infos.CARDS_EXEMPLAIRES: 4})
    return result


def generate_encounters(extension: dict, root_pictures: os.path, back: os.path) -> list:
    result: list = []
    encounter_series: list = extension[infos.EXTENSION_ENCOUNTERS]
    for serie in encounter_series:
        encounter_name: str = serie[infos.ENCOUNTERS_SERIE_NAME]
        cards_number: int = serie[infos.ENCOUNTERS_SERIE_NUMBER_CARDS]
        cards: dict = serie[infos.ENCOUNTERS_SERIE_CARDS]
        for card_name in cards:
            # chaque carte a un nombre d'exemplaire spécifique
            result.append({infos.CARDS_FACE_A: os.path.join(root_pictures, card_name), \
                            infos.CARDS_FACE_B: back, \
                            infos.CARDS_EXEMPLAIRES: cards[card_name]})
        return result


def generate_quests(extension: dict, root_pictures: os.path) -> list:
    result: list = []
    quests: list = extension[infos.EXTENSION_QUESTS]
    for quest in quests:
        # chaque carte est en fois 1
        result.append({infos.CARDS_FACE_A: os.path.join(root_pictures, quest), \
                        infos.CARDS_FACE_B: os.path.join(root_pictures, quest), \
                        infos.CARDS_EXEMPLAIRES: 1})
    return result


def display_decklist(list_cards: list) -> None:
    for card in list_cards:
        print(f"{card[infos.CARDS_EXEMPLAIRES]}x {card[infos.CARDS_FACE_A]} // {card[infos.CARDS_FACE_B]}")


def generate_cycle(cycle_data: dict, root_pictures: os.path, backs: dict) -> list:
    print(f"Génération des cartes : {cycle_data[infos.CYCLE_NAME]}")
    pictures_path: os.path = os.path.join(root_pictures, cycle_data[infos.CYCLE_FOLDER])
    print(f"Dossier des images : {pictures_path}")
    result: list = []
    for extension_name in helper_files.get_cycle_extensions(cycle_data=cycle_data):
        extension_data = cycle_data[extension_name]
        heros_cards = generate_heroes(extension=extension_data, root_pictures=pictures_path, back=backs[infos.BACK_HEROS])
        result.extend(heros_cards)
        player_cards = generate_players(extension=extension_data, root_pictures=pictures_path, back=backs[infos.BACK_PLAYER])
        result.extend(player_cards)
        contract_cards = generate_contracts(extension=extension_data, root_pictures=pictures_path, back=backs[infos.BACK_PLAYER])
        result.extend(contract_cards)
        encounter_cards = generate_encounters(extension=extension_data, root_pictures=pictures_path, back=backs[infos.BACK_ENCOUNTER])
        result.extend(encounter_cards)
        quest_cards = generate_quests(extension=extension_data, root_pictures=pictures_path)
        result.extend(quest_cards)
        display_decklist(list_cards=result)