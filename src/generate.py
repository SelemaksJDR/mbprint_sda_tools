"""
Script qui va créer les cartes à partir du fichier de configuration et des dossiers d'image
Pour les différentes cartes, détermination de leur dos et de leur nombre d'exemplaire
"""

import argparse
import cards_generator
import helper_files
import json5
import infos
import os


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


def get_cycles_from_workspace(config_folder: os.path, cycles_object) -> list:
    result: list = []
    for element in cycles_object:
        # Création du chemin vers le cycle
        result.append(os.path.join(config_folder, f"cycles/{element}.jsonc"))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help='jsonc de configuration')
    args = parser.parse_args()
    # Chemin vers le fichier de configuration
    config_path = os.path.abspath(args.config)
    print(f"Fichier de configuration pour generate_cards : {config_path}")

    workspace = None
    config_object = None
    with open(config_path, 'r') as file:
        config_object = json5.load(file)
        helper_files.validate_config_json(config_data=config_object)
    workspace = config_object["workspace"]

    # Récupération de la racine des fichiers images
    root_pictures = workspace["root_pictures"]
    # Récupération du dossier de configuration
    config_folder = workspace["config_folder"]
    # Récupération du chemin vers le dossier de résultat
    folder_result = workspace["folder_result"]
    # Récupération du chemin vers les dos de carte
    backs_object = workspace["backs"]
    backs: dict = get_backs(backs_object)
    # Détermination des cycles à générer
    cycles_object = config_object["cycles"]
    cycles : list = get_cycles_from_workspace(config_folder, cycles_object)
    for cycle in cycles:
        cycle_data: dict = None
        with open(cycle, 'r') as file:
            cycle_data = json5.load(file)
            if helper_files.validate_cycle_json(cycle_data) is False:
                continue
            print(f"Le fichier {cycle} est valide.")
        # Génère les cartes avec le bon dos et le bon nombre d'exemplaires
        cards = cards_generator.generate_cycle(cycle_data, root_pictures=root_pictures, backs=backs)
