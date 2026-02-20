"""
Fonctions de génération des cartes avec le bon dos et le bon nombre d'exemplaires
"""

import helper_files
import infos
import itertools
import pathlib


def card_list_with_flip_cards_numbered(cards: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path = None) -> list:
    result: list = []

    facesA: list = [a for a in flip_cards]
    facesB_tmp: list = [flip_cards[a] for a in flip_cards]
    facesB: list = []
    for faceB in facesB_tmp:
        if isinstance(faceB, list):
            facesB.extend(faceB)
        else:
            facesB.append(faceB)


    for card, occurrence in cards.items() :
        result_card: dict = {}
        if card in facesA:
            # cas particulier, une face A a plusieurs dos
            if isinstance(flip_cards[card], list):
                multiple_result_card: list = []
                for card_back in flip_cards[card]:
                    result_card_front: dict = {}
                    result_card_front[infos.CARDS_FACE_A] = pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, card))
                    result_card_front[infos.CARDS_FACE_B] = pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, card_back))
                    result_card_front[infos.CARDS_EXEMPLAIRES] = occurrence
                    multiple_result_card.append(result_card_front)
                result.extend(multiple_result_card)
                # On arrête le traitement ici
                continue
            # Cas général, il n'y a qu'un seul dos
            result_card[infos.CARDS_FACE_A] = pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, card))
            result_card[infos.CARDS_FACE_B] = pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, flip_cards[card]))

            result_card[infos.CARDS_EXEMPLAIRES] = occurrence
        elif card in facesB:
            # Cette carte n'est pas générée car c'est juste une face B
            continue
        else:
            if back is None:
                print(f"Aucun dos n'a été assigné à la carte {card}")
                continue
            result_card[infos.CARDS_FACE_A] = pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, card))
            result_card[infos.CARDS_FACE_B] = pathlib.Path.absolute(pathlib.Path(back))
            result_card[infos.CARDS_EXEMPLAIRES] = occurrence
        result.append(result_card)
    return result


def card_list_with_flip_cards(cards: list, flip_cards: dict, root_pictures: pathlib.Path, number_cards: int, back: pathlib.Path = None) -> list:
    cards_dict: dict = {card: number for card, number in zip(cards, itertools.repeat(number_cards, len(cards)))}
    return card_list_with_flip_cards_numbered(cards=cards_dict, flip_cards=flip_cards, root_pictures=root_pictures, back=back)


def generate_heroes(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path) -> list:
    result: list = card_list_with_flip_cards(cards= extension[infos.EXTENSION_HEROES], flip_cards=flip_cards, root_pictures=root_pictures, back=back, number_cards=1)
    return result


def generate_players(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path) -> list:
    result: list = card_list_with_flip_cards(cards=extension[infos.EXTENSION_PLAYERS], flip_cards=flip_cards, root_pictures=root_pictures, back=back, number_cards=3)
    return result


def generate_contracts(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path) -> list:
    result: list = card_list_with_flip_cards(cards=extension[infos.EXTENSION_CONTRACTS], flip_cards=flip_cards, root_pictures=root_pictures, back=back, number_cards=4)
    return result


def generate_encounters(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path) -> list:
    result: list = []
    encounter_series: list = extension[infos.EXTENSION_ENCOUNTERS]
    for serie in encounter_series:
        encounter_name: str = serie[infos.ENCOUNTERS_SERIE_NAME]
        cards_number: int = serie[infos.ENCOUNTERS_SERIE_NUMBER_CARDS]
        cards: dict = serie[infos.ENCOUNTERS_SERIE_CARDS]
        cards_in_serie: list = card_list_with_flip_cards_numbered(cards=cards, flip_cards=flip_cards, root_pictures=root_pictures, back=back)
        cards_in_serie_occ: int = 0
        for card in cards_in_serie:
            cards_in_serie_occ = cards_in_serie_occ + card[infos.CARDS_EXEMPLAIRES]

        if cards_in_serie_occ != cards_number:
            print(f"[ERREUR] La serie {encounter_name} devrait avoir {cards_number} cartes et {cards_in_serie_occ} se trouvent dans le fichier de configuration.")
            for card in cards_in_serie:
                print(f"{card[infos.CARDS_EXEMPLAIRES]}x {pathlib.Path.split(card[infos.CARDS_FACE_A])[-1]} // {pathlib.Path.split(card[infos.CARDS_FACE_B])[-1]}")
            continue
        print(f"[OK] La serie {encounter_name} est ajoutée avec {cards_number} cartes.")
        result.extend(cards_in_serie)
    return result


def generate_quests(extension: dict, flip_cards: dict, root_pictures: pathlib.Path) -> list:
    result: list = card_list_with_flip_cards(cards=extension[infos.EXTENSION_QUESTS], flip_cards=flip_cards, root_pictures=root_pictures, number_cards=1)
    return result


def generate_cycle(cycle_data: dict, root_pictures: pathlib.Path, backs: dict) -> list:
    print(f"\n========== Génération des cartes : {cycle_data[infos.CYCLE_NAME]} ==========")
    pictures_path: pathlib.Path = pathlib.Path.joinpath(root_pictures, cycle_data[infos.CYCLE_FOLDER])
    print(f"Dossier des images : {pictures_path}")
    result: list = []
    for extension_name in helper_files.get_cycle_extensions(cycle_data=cycle_data):
        extension_data = cycle_data[extension_name]
        flip_cards = extension_data[infos.EXTENSION_FLIP_CARDS]
        heros_cards = generate_heroes(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_HEROS])
        result.extend(heros_cards)
        player_cards = generate_players(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_PLAYER])
        result.extend(player_cards)
        if infos.EXTENSION_CONTRACTS in extension_data:
            contract_cards = generate_contracts(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_PLAYER])
            result.extend(contract_cards)
        encounter_cards = generate_encounters(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_ENCOUNTER])
        result.extend(encounter_cards)
        quest_cards = generate_quests(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path)
        result.extend(quest_cards)
    return result
