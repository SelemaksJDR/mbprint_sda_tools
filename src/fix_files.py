"""
! Ce script modifie le dossier SDAJCE
Ce script effectue des corrections sur les noms des fichiers
Et copie les cartes du cycle 9 sans le watermark
"""

import argparse
import json5
import os

def fix_filenames(root_path: os.path, fix_config_file: os.path, is_quiet: bool) -> None:
    # Ouvre le fichier .jsonc
    with open(fix_config_file, 'r') as file:
        data = json5.load(file)
        if "fix_filenames" not in data:
            print(f"L'élément fix_filenames n'existe pas dans le fichier {fix_config_file}")
            exit(1)
        for element in data["fix_filenames"]:
            source: os.path = element
            target: os.path = data["fix_filenames"][element]
            print(f"Correction : {source} -> {target}")
            # Si il n'y a pas d'action à faire, continue
            if is_quiet is False:
                # Effectue l'action
                continue

def copy_cycle_9_deluxe(root_path: os.path, fix_config_file: os.path, is_quiet: bool):
    with open(fix_config_file, 'r') as file:
        data = json5.load(file)
        if "copy_cycle_9_deluxe" not in data:
            print(f"L'élément copy_cycle_9_deluxe n'existe pas dans le fichier {fix_config_file}")
            exit(1)
        for element in data["copy_cycle_9_deluxe"]:
            source: os.path = element
            target: os.path = data["copy_cycle_9_deluxe"][element]
            print(f"Remplacement : {source} -> {target}")
            # Si il n'y a pas d'action à faire, continue
            if is_quiet is False:
                # Effectue l'action
                continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help='racine du dossier image')
    parser.add_argument("--config", required=True, help='jsonc de configuration')
    parser.add_argument("--quiet", required=False, action='store_true')
    args = parser.parse_args()
    # Chemin vers la racine des images
    root_path = os.path.abspath(args.root)
    print(f"racine des fichiers images : {root_path}")
    # Chemin vers le fichier de configuration
    config_path = os.path.abspath(args.config)
    print(f"Fichier de configuration pour fix_files : {config_path}")
    # Flag qui indique si le script effectue les actions ou log seulement
    is_quiet: bool = args.quiet
    if is_quiet:
        print("Le script n'effectue aucune action, il ne fait que logger ce qu'il ferait sans l'option quiet")

    # Corrige les noms de fichier
    fix_filenames(root_path, config_path, is_quiet)
    # Copie les éléments du dossier Deluxe cycle 9 sans logo FFG dans cycle 9 (incl. A Shadow in the east)
    copy_cycle_9_deluxe(root_path, config_path, is_quiet)