#!/usr/bin/env python3
"""Remplacement de texte et ajout de filigrane sur les images de cartes.

Ce script traite les images PNG d'un dossier pour :
    1. Supprimer une zone de texte predefinie (remplacement par le fond)
    2. Ajouter le texte "Not For Sale" en bas de l'image
    3. Enregistrer les images modifiees dans un dossier de destination

Les cartes dont le prefixe se termine par 'A' ou 'B' sont copiees sans modification.

Prerequis :
    - Python 3.10+
    - Pillow (pip install Pillow)
    - ImageMagick installe et accessible dans le PATH

Auteur : Clint Cheachwood
"""

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image

from from_clint_cheawood.magick import run_magick


def supprimer_texte_et_remplacer_par_fond(
    chemin_source: Path,
    chemin_sortie: Path,
    x_debut: int = 250,
    y_debut: int = 1020,
    largeur: int = 252,
    hauteur: int = 10,
    y_source: int = 1040,
) -> bool:
    """Supprime une zone de texte en la remplacant par des pixels echantillonnes.

    La zone a supprimer est definie par (x_debut, y_debut, largeur, hauteur).
    Les pixels de remplacement sont pris a partir de (x_debut, y_source).
    L'operation est appliquee deux fois (deux bandes consecutives).

    Retourne True en cas de succes, False sinon.
    """
    if not chemin_source.exists():
        print(f"ERREUR: Fichier source introuvable : {chemin_source}", file=sys.stderr)
        return False

    try:
        img = Image.open(chemin_source)
        pixels = img.load()
        img_w, img_h = img.size

        print(f"Remplacement du texte dans : {chemin_source.name} ({img_w}x{img_h})")

        # Verifier les bornes
        if (x_debut + largeur > img_w
                or y_debut + 2 * hauteur > img_h
                or y_source + hauteur > img_h):
            print(f"ERREUR: Coordonnees hors limites pour {chemin_source.name}", file=sys.stderr)
            return False

        largeur_source = min(largeur, 300)
        hauteur_source = min(hauteur, img_h - y_source)

        # Premiere passe : remplacer la zone (y_debut -> y_debut + hauteur)
        for y in range(y_debut, y_debut + hauteur):
            for x in range(x_debut, x_debut + largeur):
                dx = x - x_debut
                dy = y - y_debut
                if dx < largeur_source and dy < hauteur_source:
                    xs = x_debut + dx  # Utilise x_debut=0 dans le PS1 original -> ajuste
                    ys = y_source + dy
                    if 0 <= xs < img_w and 0 <= ys < img_h:
                        pixels[x, y] = pixels[xs, ys]

        # Deuxieme passe : remplacer la zone suivante
        y_debut2 = y_debut + hauteur
        for y in range(y_debut2, y_debut2 + hauteur):
            for x in range(x_debut, x_debut + largeur):
                dx = x - x_debut
                dy = y - y_debut2
                if dx < largeur_source and dy < hauteur_source:
                    xs = x_debut + dx
                    ys = y_source + dy
                    if 0 <= xs < img_w and 0 <= ys < img_h:
                        pixels[x, y] = pixels[xs, ys]

        img.save(str(chemin_sortie), format="PNG")
        print(f"Texte supprime : {chemin_sortie.name}")
        return True

    except Exception as e:
        print(f"ERREUR lors du traitement de {chemin_source.name} : {e}", file=sys.stderr)
        return False


def ajouter_texte_fan_made(
    source: Path,
    destination: Path,
    texte: str = "Not For Sale",
    x: int = 350,
    y: int = 1035,
    taille_police: int = 14,
    nom_police: str = "Times-New-Roman-Bold",
    couleur: str = "white",
) -> bool:
    """Ajoute un texte sur une image via ImageMagick.

    Retourne True en cas de succes, False sinon.
    """
    if not source.exists():
        print(f"ERREUR: Fichier source introuvable : {source}", file=sys.stderr)
        return False

    try:
        run_magick(
            str(source),
            "-font", nom_police,
            "-pointsize", str(taille_police),
            "-fill", couleur,
            "-annotate", f"+{x}+{y}", texte,
            str(destination),
        )
        print(f"Texte '{texte}' ajoute : {destination.name}")
        return True
    except RuntimeError as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remplace le texte et ajoute un filigrane sur les images de cartes."
    )
    parser.add_argument(
        "--source", required=True, type=Path,
        help="Dossier contenant les images PNG a traiter.",
    )
    parser.add_argument(
        "--destination", required=True, type=Path,
        help="Dossier de destination pour les images modifiees.",
    )
    parser.add_argument(
        "--texte", default="Not For Sale",
        help="Texte a ajouter sur les images (defaut: 'Not For Sale').",
    )

    args = parser.parse_args()
    source_dir: Path = args.source
    dest_dir: Path = args.destination
    texte: str = args.texte

    if not source_dir.is_dir():
        print(f"ERREUR: Le dossier source '{source_dir}' n'existe pas.", file=sys.stderr)
        sys.exit(1)

    dest_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(source_dir.glob("*.png"))
    if not images:
        print(f"AVERTISSEMENT: Aucune image PNG dans '{source_dir}'.")
        sys.exit(0)

    print(f"Traitement de {len(images)} images depuis : {source_dir}")

    for img_path in images:
        # Extraire le prefixe (avant le premier '-')
        prefixe = img_path.stem.split("-")[0] if "-" in img_path.stem else img_path.stem
        dernier_char = prefixe[-1].upper() if prefixe else ""

        if dernier_char in ("A", "B"):
            # Copier sans modification
            print(f"Image ignoree (A/B) : {img_path.name}")
            shutil.copy2(img_path, dest_dir / img_path.name)
        else:
            # Supprimer le texte puis ajouter le filigrane
            tmp_path = dest_dir / f"{img_path.stem}_sans_texte.png"
            final_path = dest_dir / img_path.name

            if supprimer_texte_et_remplacer_par_fond(img_path, tmp_path):
                ajouter_texte_fan_made(tmp_path, final_path, texte=texte)
                tmp_path.unlink(missing_ok=True)

    print(f"\nTraitement termine. Resultats dans : {dest_dir}")


if __name__ == "__main__":
    main()
