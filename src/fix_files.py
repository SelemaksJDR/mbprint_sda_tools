"""
! Ce script modifie le dossier SDAJCE
Ce script effectue des corrections sur les noms des fichiers
Et copie les cartes du cycle 9 sans le watermark
"""

import argparse
import json5
import pathlib
import shutil


def fix_erratas(root_path: pathlib.Path, fix_config_file: pathlib.Path, is_quiet: bool) -> None:
    with open(fix_config_file, 'r') as file:
        data = json5.load(file)
        if "erratas" not in data:
            print(f"L'élément erratas n'existe pas dans le fichier {fix_config_file}")
            exit(1)
        for element in data["erratas"]:
            card_with_error: pathlib.Path = root_path / element
            card_with_fix: pathlib.Path = root_path / data["erratas"][element]
            print(f"Suffixage de {card_with_error} en {card_with_error.with_suffix(f".error{card_with_error.suffix}")}")
            print(f"Corrige l'errata : {card_with_error} -> {card_with_fix}")
            # Si il n'y a pas d'action à faire, continue
            if is_quiet is False:
                # Effectue l'action
                if card_with_error.exists() and card_with_fix.exists():
                    previous_name = card_with_error
                    card_with_error.rename(card_with_error.with_suffix(f".error{card_with_error.suffix}"))
                    shutil.copy2(card_with_fix, previous_name)


def fix_filenames(root_path: pathlib.Path, fix_config_file: pathlib.Path, is_quiet: bool) -> None:
    # Ouvre le fichier .jsonc
    with open(fix_config_file, 'r') as file:
        data = json5.load(file)
        if "fix_filenames" not in data:
            print(f"L'élément fix_filenames n'existe pas dans le fichier {fix_config_file}")
            exit(1)
        for element in data["fix_filenames"]:
            source: pathlib.Path = root_path / pathlib.Path(element)
            target: pathlib.Path = root_path / pathlib.Path(data["fix_filenames"][element])
            print(f"Correction : {source} -> {target}")
            # Si il n'y a pas d'action à faire, continue
            if is_quiet is False:
                # Effectue l'action
                if source.exists():
                    source.rename(source.parent / target.name)
                elif target.exists():
                    print(f"{source} a déjà été remplacé par {target}")


def copy_cycle_9_deluxe(root_path: pathlib.Path, fix_config_file: pathlib.Path, is_quiet: bool):
    with open(fix_config_file, 'r') as file:
        data = json5.load(file)
        if "copy_cycle_9_deluxe" not in data:
            print(f"L'élément copy_cycle_9_deluxe n'existe pas dans le fichier {fix_config_file}")
            exit(1)
        for element in data["copy_cycle_9_deluxe"]:
            source: pathlib.Path = root_path / element
            target: pathlib.Path = root_path / data["copy_cycle_9_deluxe"][element]
            print(f"Remplacement : {source} -> {target}")
            # Si il n'y a pas d'action à faire, continue
            if is_quiet is False:
                # Effectue l'action
                if source.exists() and target.exists():
                    shutil.copy2(source, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help='racine du dossier image')
    parser.add_argument("--config", required=True, help='jsonc de configuration')
    parser.add_argument("--quiet", required=False, action='store_true')
    args = parser.parse_args()
    # Chemin vers la racine des images
    root_path = pathlib.Path(args.root).absolute()
    print(f"racine des fichiers images : {root_path}")
    # Chemin vers le fichier de configuration
    config_path = pathlib.Path(args.config).absolute()
    print(f"Fichier de configuration pour fix_files : {config_path}")
    # Flag qui indique si le script effectue les actions ou log seulement
    is_quiet: bool = args.quiet
    if is_quiet:
        print("Le script n'effectue aucune action, il ne fait que logger ce qu'il ferait sans l'option quiet")

    # Corrige les noms de fichier
    fix_filenames(root_path, config_path, is_quiet)
    # Corrige les erratas
    fix_erratas(root_path, config_path, is_quiet)
    # Copie les éléments du dossier Deluxe cycle 9 sans logo FFG dans cycle 9 (incl. A Shadow in the east)
    copy_cycle_9_deluxe(root_path, config_path, is_quiet)