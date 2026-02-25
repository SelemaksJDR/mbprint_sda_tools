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
import shutil


def get_backs(backs_object) -> dict:
    result: dict = {}
    # Dos des cartes joueurs
    if "player_back" not in backs_object:
        print(f"L'élément player_back n'existe pas dans l'objet backs")
        exit(1)
    result[infos.BACK_PLAYER] = pathlib.Path(backs_object["player_back"]).absolute()
    # Dos des cartes rencontre
    if "encounter_back" not in backs_object:
        print(f"L'élément encounter_back n'existe pas dans l'objet backs")
        exit(1)
    result[infos.BACK_ENCOUNTER] = pathlib.Path(backs_object["encounter_back"]).absolute()
    # Dos des cartes héros
    if "heros_back" not in backs_object:
        print(f"L'élément heros_back n'existe pas dans l'objet backs, utilisation du dos de carte joueurs dans ce cas")
        result[infos.BACK_HEROS] = pathlib.Path(backs_object["player_back"]).absolute()
    else:
        result[infos.BACK_HEROS] = pathlib.Path(backs_object["heros_back"]).absolute()
    return result


def get_cycles_from_workspace(config_folder: pathlib.Path, cycles_object) -> list:
    result: list = []
    for element in cycles_object:
        # Création du chemin vers le cycle
        result.append(pathlib.Path.joinpath(config_folder, f"cycles/{element}.jsonc"))
    return result


def generate_cycle_pdf(cycle_name: str, cards: dict, result_folder: pathlib.Path) -> None:
    print(f"========== Génération du cycle {cycle_name} ==========")
    # génération des images
    cards_with_bleed = cards_generator.generate_images(cards=cards, result_folder=result_folder, backs=backs)
    # Generer le PDF
    pdf_folder: pathlib.Path = pathlib.Path.joinpath(result_folder, pathlib.Path("pdf"))
    pdf_folder.mkdir(parents=True, exist_ok=True)
    pdf_output = pdf_folder / f"{cycle_name}.pdf"
    generepdf.new_pdf_from_images(cards_with_bleed, pdf_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="jsonc de configuration")
    parser.add_argument("--validate", required=False, action="store_true", help="indique si il faut seulement valider")
    args = parser.parse_args()
    # Chemin vers le fichier de configuration
    config_path: pathlib.Path = pathlib.Path.absolute(pathlib.Path(args.config))
    print(f"Fichier de configuration pour generate_cards : {config_path}")

    # Flag qui indique si le script valide seulement les cycles
    validate_only: bool = args.validate
    if validate_only:
        print("Le script valide seulement les cibles")

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
    result_folder: pathlib.Path = pathlib.Path.absolute(pathlib.Path(workspace["result_folder"]))
    # Récupération du chemin vers les dos de carte
    backs_object = workspace["backs"]
    backs: dict = get_backs(backs_object)
    # Détermination des cycles à générer
    cycles_object = config_object["cycles"]
    cycles : list = get_cycles_from_workspace(config_folder, cycles_object)
    # génération des listes de cartes par cycle
    encounters_infos: dict = {}
    cards_in_cycle: dict = {}
    for cycle in cycles:
        cycle_data: dict = None
        with open(cycle, 'r') as file:
            cycle_data = json5.load(file)
            if helper_files.validate_cycle_json(cycle_data) is False:
                continue
        # Génère les cartes avec le bon dos et le bon nombre d'exemplaires
        cards_generated, encounters_generated = cards_generator.generate_cycle(cycle_data, root_pictures=root_pictures, backs=backs, fix_object=fix_config_object)
        cards_in_cycle[cycle_data[infos.CYCLE_NAME]] = (cards_generated)
        encounters_infos.update(encounters_generated)
    print("================================")
    print("========== CONCLUSION ==========")
    print("================================")
    all_is_good: bool = True
    for encounter, status in encounters_infos.items():
        if status is False:
            print(f"[ERREUR] La série {encounter} n'est pas correctement configurée")
            all_is_good = False
    if all_is_good:
        print(f"[OK] Toutes les séries sont correctement configurées")

    if validate_only is False:
        # Supprime le dossier de résultat
        if result_folder.exists():
            shutil.rmtree(result_folder)
        # Génère les cartes de chaque cycle
        for cycle_name, cards in cards_in_cycle.items():
            generate_cycle_pdf(cycle_name, cards, result_folder)
