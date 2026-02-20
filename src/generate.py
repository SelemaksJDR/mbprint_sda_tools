"""
Script qui va créer les cartes à partir du fichier de configuration et des dossiers d'image
Pour les différentes cartes, détermination de leur dos et de leur nombre d'exemplaire
"""

import argparse
import cards_generator
import helper_files
import json5
import infos
import pathlib
from from_clint_cheawood import generepdf


def get_backs(backs_object) -> dict:
    result: dict = {}
    # Dos des cartes joueurs
    if "player_back" not in backs_object:
        print(f"L'élément player_back n'existe pas dans l'objet backs")
        exit(1)
    result[infos.BACK_PLAYER] = backs_object["player_back"]
    # Dos des cartes rencontre
    if "encounter_back" not in backs_object:
        print(f"L'élément encounter_back n'existe pas dans l'objet backs")
        exit(1)
    result[infos.BACK_ENCOUNTER] = backs_object["encounter_back"]
    # Dos des cartes héros
    if "heros_back" not in backs_object:
        print(f"L'élément heros_back n'existe pas dans l'objet backs, utilisation du dos de carte joueurs dans ce cas")
        result[infos.BACK_HEROS] = backs_object["player_back"]
    else:
        result[infos.BACK_HEROS] = backs_object["heros_back"]
    return result


def get_cycles_from_workspace(config_folder: pathlib.Path, cycles_object) -> list:
    result: list = []
    for element in cycles_object:
        # Création du chemin vers le cycle
        result.append(pathlib.Path.joinpath(config_folder, f"cycles/{element}.jsonc"))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help='jsonc de configuration')
    args = parser.parse_args()
    # Chemin vers le fichier de configuration
    config_path: pathlib.Path = pathlib.Path.absolute(pathlib.Path(args.config))
    print(f"Fichier de configuration pour generate_cards : {config_path}")

    workspace = None
    config_object = None
    with open(config_path, 'r') as file:
        config_object = json5.load(file)
        helper_files.validate_config_json(config_data=config_object)
    workspace = config_object["workspace"]

    # Récupération de la racine des fichiers images
    root_pictures: pathlib.Path = pathlib.Path.absolute(pathlib.Path(workspace["root_pictures"]))
    # Récupération du dossier de configuration
    config_folder: pathlib.Path = pathlib.Path.absolute(pathlib.Path(workspace["config_folder"]))
    # Récupération du dossier de fix des filenames
    fix_filenames_folder: pathlib.Path = config_folder.joinpath(pathlib.Path(workspace["fix_filenames"]))
    fix_config_object: dict = {}
    with open(fix_filenames_folder, 'r') as file:
        fix_config_object = json5.load(file)
        fix_config_object = fix_config_object["fix_filenames"]
    # Récupération du chemin vers le dossier de résultat
    result_folder: pathlib.Path = pathlib.Path(workspace["result_folder"])
    # Récupération du chemin vers les dos de carte
    backs_object = workspace["backs"]
    backs: dict = get_backs(backs_object)
    # Détermination des cycles à générer
    cycles_object = config_object["cycles"]
    cycles : list = get_cycles_from_workspace(config_folder, cycles_object)
    # génération des listes de cartes par cycle
    cards: list = []
    for cycle in cycles:
        cycle_data: dict = None
        with open(cycle, 'r') as file:
            cycle_data = json5.load(file)
            if helper_files.validate_cycle_json(cycle_data) is False:
                continue
        # Génère les cartes avec le bon dos et le bon nombre d'exemplaires
        cards.extend(cards_generator.generate_cycle(cycle_data, root_pictures=root_pictures, backs=backs))
    # génération des images
    cards_with_bleed = cards_generator.generate_images(cards=cards, result_folder=result_folder, fix_config_object=fix_config_object, backs=backs)
    # Generer le PDF
    pdf_folder: pathlib.Path = pathlib.Path.joinpath(result_folder, pathlib.Path("pdf"))
    pdf_folder.mkdir(parents=True, exist_ok=True)
    pdf_output = pdf_folder / f"0_FINAL.pdf"
    generepdf.new_pdf_from_images(cards_with_bleed, pdf_output)
