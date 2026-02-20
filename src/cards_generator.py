"""
Fonctions de génération des cartes avec le bon dos et le bon nombre d'exemplaires
"""

import helper_files
import infos
import itertools
import pathlib
from from_clint_cheawood.generepdf import convert_image_to_bleed


def add_card(card_front: dict, card_back: dict, root_pictures: pathlib.Path, occurrence: int, fix_object) -> dict:
    result: dict = {}
    # Face A
    exists_a, card_face_a = helper_files.path_exists_with_fix(img_path=pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, card_front)), fix_config_object=fix_object)
    if exists_a is False:
        return False, {}
    result[infos.CARDS_FACE_A] = card_face_a
    # Face B
    exists_b, card_face_b = helper_files.path_exists_with_fix(img_path=pathlib.Path.absolute(pathlib.Path.joinpath(root_pictures, card_back)), fix_config_object=fix_object)
    if exists_b is False:
        return False, {}
    result[infos.CARDS_FACE_B] = card_face_b
    # Nombre d'exemplaires
    result[infos.CARDS_EXEMPLAIRES] = occurrence
    return True, result


def card_list_with_flip_cards_numbered(cards: dict, flip_cards: dict, root_pictures: pathlib.Path, fix_object: dict, back: pathlib.Path = None) -> list:
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
                    is_ok, result_card_front = add_card(card_front=card, card_back=card_back, root_pictures=root_pictures, occurrence=occurrence, fix_object=fix_object)
                    if is_ok is False:
                        continue
                    multiple_result_card.append(result_card_front)
                result.extend(multiple_result_card)
                # On arrête le traitement ici
                continue
            # Cas général, il n'y a qu'un seul dos
            is_ok, result_card = add_card(card_front=card, card_back=flip_cards[card], root_pictures=root_pictures, occurrence=occurrence, fix_object=fix_object)
            if is_ok is False:
                continue
        elif card in facesB:
            # Cette carte n'est pas générée car c'est juste une face B
            continue
        else:
            if back is None:
                print(f"Aucun dos n'a été assigné à la carte {card}")
                continue
            # Cas général, il n'y a qu'un seul dos
            is_ok, result_card = add_card(card_front=card, card_back=back, root_pictures=root_pictures, occurrence=occurrence, fix_object=fix_object)
            if is_ok is False:
                continue
        result.append(result_card)
    return result


def card_list_with_flip_cards(cards: list, flip_cards: dict, root_pictures: pathlib.Path, number_cards: int, fix_object: dict, back: pathlib.Path = None) -> list:
    cards_dict: dict = {card: number for card, number in zip(cards, itertools.repeat(number_cards, len(cards)))}
    return card_list_with_flip_cards_numbered(cards=cards_dict, flip_cards=flip_cards, root_pictures=root_pictures, back=back, fix_object=fix_object)


def generate_heroes(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path, fix_object: dict) -> list:
    result: list = card_list_with_flip_cards(cards= extension[infos.EXTENSION_HEROES], flip_cards=flip_cards, root_pictures=root_pictures, back=back, number_cards=1, fix_object=fix_object)
    return result


def generate_players(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path, fix_object: dict) -> list:
    result: list = card_list_with_flip_cards(cards=extension[infos.EXTENSION_PLAYERS], flip_cards=flip_cards, root_pictures=root_pictures, back=back, number_cards=3, fix_object=fix_object)
    return result


def generate_contracts(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path, fix_object: dict) -> list:
    result: list = card_list_with_flip_cards(cards=extension[infos.EXTENSION_CONTRACTS], flip_cards=flip_cards, root_pictures=root_pictures, back=back, number_cards=4, fix_object=fix_object)
    return result


def generate_encounters(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, back: pathlib.Path, fix_object: dict) -> list | dict:
    result_cards: list = []
    result_encounters: dict = {}
    encounter_series: list = extension[infos.EXTENSION_ENCOUNTERS]
    for serie in encounter_series:
        encounter_name: str = serie[infos.ENCOUNTERS_SERIE_NAME]
        cards_number: int = serie[infos.ENCOUNTERS_SERIE_NUMBER_CARDS]
        cards: dict = serie[infos.ENCOUNTERS_SERIE_CARDS]
        cards_in_serie: list = card_list_with_flip_cards_numbered(cards=cards, flip_cards=flip_cards, root_pictures=root_pictures, back=back, fix_object=fix_object)
        cards_in_serie_occ: int = 0
        for card in cards_in_serie:
            cards_in_serie_occ = cards_in_serie_occ + card[infos.CARDS_EXEMPLAIRES]

        if cards_in_serie_occ != cards_number:
            print(f"[ERREUR] La serie {encounter_name} devrait avoir {cards_number} cartes et {cards_in_serie_occ} se trouvent dans le fichier de configuration.")
            result_encounters[encounter_name] = False
            for card in cards_in_serie:
                print(f"{card[infos.CARDS_EXEMPLAIRES]}x {card[infos.CARDS_FACE_A].name} // {card[infos.CARDS_FACE_B].name}")
            continue
        print(f"[OK] La serie {encounter_name} est ajoutée avec {cards_number} cartes.")
        result_encounters[encounter_name] = True
        result_cards.extend(cards_in_serie)
    return result_cards, result_encounters


def generate_quests(extension: dict, flip_cards: dict, root_pictures: pathlib.Path, fix_object: dict) -> list:
    result: list = card_list_with_flip_cards(cards=extension[infos.EXTENSION_QUESTS], flip_cards=flip_cards, root_pictures=root_pictures, number_cards=1, fix_object=fix_object)
    return result


def generate_cycle(cycle_data: dict, root_pictures: pathlib.Path, backs: dict, fix_object: dict) -> list:
    print(f"\n========== Génération des cartes : {cycle_data[infos.CYCLE_NAME]} ==========")
    pictures_path: pathlib.Path = pathlib.Path.joinpath(root_pictures, cycle_data[infos.CYCLE_FOLDER])
    print(f"Dossier des images : {pictures_path}")
    result: list = []
    encounters_result: dict = {}
    for extension_name in helper_files.get_cycle_extensions(cycle_data=cycle_data):
        extension_data = cycle_data[extension_name]
        flip_cards = extension_data[infos.EXTENSION_FLIP_CARDS]
        heros_cards = generate_heroes(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_HEROS], fix_object=fix_object)
        result.extend(heros_cards)
        player_cards = generate_players(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_PLAYER], fix_object=fix_object)
        result.extend(player_cards)
        if infos.EXTENSION_CONTRACTS in extension_data:
            contract_cards = generate_contracts(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_PLAYER], fix_object=fix_object)
            result.extend(contract_cards)
        encounter_cards, encounters_infos = generate_encounters(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, back=backs[infos.BACK_ENCOUNTER], fix_object=fix_object)
        result.extend(encounter_cards)
        encounters_result.update(encounters_infos)
        quest_cards = generate_quests(extension=extension_data, flip_cards=flip_cards, root_pictures=pictures_path, fix_object=fix_object)
        result.extend(quest_cards)
    return result, encounters_result


def get_and_create_bleed_img(card: pathlib.Path, cards_folder: pathlib.Path):
        dest_img_name = f"converted-{card.name}"
        dest_img = cards_folder / dest_img_name
        # Si l'image n'existe pas déjà, elle est créée
        dest_img = convert_image_to_bleed(input_file=card, output_dir=cards_folder, prefix="converted")
        return True, pathlib.Path.absolute(dest_img)


def generate_images(cards: list, result_folder: pathlib.Path, backs) -> list:
    cards_folder: pathlib.Path = pathlib.Path.joinpath(result_folder, pathlib.Path("cards"))
    cards_folder.mkdir(parents=True, exist_ok=True)
    cards_with_bleed: list = []

    backs_path = [pathlib.Path.absolute(pathlib.Path(back)) for _, back in backs.items()]
    backs_with_bleed: dict = {}

    for back in backs_path:
        back_exists, back_img = get_and_create_bleed_img(card=back, cards_folder=cards_folder)
        if back_exists is False:
            continue
        backs_with_bleed[back] = back_img

    for card in cards:
        # Récupère les images
        front_exists, front_img = get_and_create_bleed_img(card=card[infos.CARDS_FACE_A], cards_folder=cards_folder)
        if front_exists is False:
            continue
        if card[infos.CARDS_FACE_B] not in backs_with_bleed.keys():
            back_exists, back_img = get_and_create_bleed_img(card=card[infos.CARDS_FACE_B], cards_folder=cards_folder)
            if back_exists is False:
                continue
        else:
            back_img = backs_with_bleed[card[infos.CARDS_FACE_B]]

        # Ajoute les images à la liste à créer
        for _ in range(0, card[infos.CARDS_EXEMPLAIRES]):
            # Front
            cards_with_bleed.append(front_img)
            # Back
            cards_with_bleed.append(back_img)
    return cards_with_bleed

