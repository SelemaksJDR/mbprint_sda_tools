#!/usr/bin/env python3
"""Generateur de PDF de cartes a partir d'images.

Ce script genere des PDF prets a l'impression pour des jeux de cartes
(compatible MBPrint). Il lit des fichiers de configuration pour determiner
les types de cartes, les quantites, et genere le PDF final avec marges
de coupe (bleed).

Prerequis :
    - Python 3.10+
    - ImageMagick installe et accessible dans le PATH

Auteur : Clint Cheachwood
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

from config import parse_card_ranges, parse_deck_counts, get_base_name
from magick import run_magick


# ---------------------------------------------------------------------------
# Fonctions de creation des cartes
# ---------------------------------------------------------------------------

def find_source_cards(source_dir: Path, pattern: str) -> list[Path]:
    """Recherche des fichiers correspondant a un pattern glob dans un repertoire."""
    return sorted(source_dir.glob(pattern))


def creation_heros(
    file_path: Path,
    source_dir: Path,
    dos_hero_template: Path,
    output_dir: Path,
) -> None:
    """Cree les cartes Heros (_H) et leurs dos a partir des images source."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = get_base_name(file_path)
    card_ranges = parse_card_ranges(file_path)

    if "H" not in card_ranges:
        print("Aucune ligne 'H:' trouvee. Heros ignores.")
        return

    for start, end in card_ranges["H"]:
        for i in range(start, end + 1):
            sources = find_source_cards(source_dir, f"{base_name}{i}*.png")
            if not sources:
                print(f"ERREUR: Aucune image source pour {base_name}{i}", file=sys.stderr)
                continue

            for src in sources:
                # Carte face
                dest_face = output_dir / f"{base_name}{i}_H.png"
                if not dest_face.exists():
                    shutil.copy2(src, dest_face)
                    print(f"Carte heros creee : {dest_face.name}")

                # Carte dos
                dest_dos = output_dir / f"{base_name}{i}_H_dos.png"
                if not dest_dos.exists():
                    shutil.copy2(dos_hero_template, dest_dos)
                    print(f"Dos heros cree : {dest_dos.name}")


def creation_joueur(
    file_path: Path,
    source_dir: Path,
    dos_joueur_template: Path,
    output_dir: Path,
) -> None:
    """Cree les cartes Joueur (_J) en 3 exemplaires avec leurs dos."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = get_base_name(file_path)
    card_ranges = parse_card_ranges(file_path)

    if "J" not in card_ranges:
        print("Aucune ligne 'J:' trouvee. Joueurs ignores.")
        return

    for start, end in card_ranges["J"]:
        for i in range(start, end + 1):
            sources = find_source_cards(source_dir, f"{base_name}{i}-*.png")
            if not sources:
                print(f"AVERTISSEMENT: Aucune image source pour {base_name}{i}")
                continue

            for src in sources:
                for j in range(1, 4):  # 3 exemplaires
                    dest_face = output_dir / f"{base_name}{i}_{j}_J.png"
                    shutil.copy2(src, dest_face)
                    print(f"Carte joueur creee : {dest_face.name}")

                    dest_dos = output_dir / f"{base_name}{i}_{j}_J_dos.png"
                    shutil.copy2(dos_joueur_template, dest_dos)
                    print(f"Dos joueur cree : {dest_dos.name}")


def creation_deck_rencontre(
    file_path: Path,
    deck_file_path: Path,
    source_dir: Path,
    dos_rencontre_template: Path,
    output_dir: Path,
) -> None:
    """Cree les cartes Rencontre (_R) selon les quantites du deck."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = get_base_name(file_path)
    card_ranges = parse_card_ranges(file_path)
    deck_counts = parse_deck_counts(deck_file_path)

    if "E" not in card_ranges:
        print("Aucune ligne 'E:' trouvee. Rencontres ignorees.")
        return

    for start, end in card_ranges["E"]:
        for i in range(start, end + 1):
            card_number = f"{base_name}{i}"
            count = deck_counts.get(card_number)
            if count is None:
                print(f"ERREUR: Nombre d'exemplaires non trouve pour {card_number}", file=sys.stderr)
                continue

            sources = find_source_cards(source_dir, f"{card_number}*.png")
            if not sources:
                print(f"ERREUR: Aucune image source pour {card_number}", file=sys.stderr)
                continue

            src = sources[0]
            for j in range(1, count + 1):
                dest_face = output_dir / f"{card_number}_{j}_R.png"
                shutil.copy2(src, dest_face)
                print(f"Carte rencontre creee : {dest_face.name}")

                dest_dos = output_dir / f"{card_number}_{j}_R_dos.png"
                shutil.copy2(dos_rencontre_template, dest_dos)
                print(f"Dos rencontre cree : {dest_dos.name}")


def creation_deck_quete(
    file_path: Path,
    source_dir: Path,
    output_dir: Path,
) -> None:
    """Cree les cartes Quete (_Q) en un seul exemplaire, sans dos."""
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = get_base_name(file_path)
    card_ranges = parse_card_ranges(file_path)

    if "Q" not in card_ranges:
        print("Aucune ligne 'Q:' trouvee. Quetes ignorees.")
        return

    for start, end in card_ranges["Q"]:
        for i in range(start, end + 1):
            card_number = f"{base_name}{i}"
            sources = find_source_cards(source_dir, f"{card_number}*.png")
            if not sources:
                print(f"AVERTISSEMENT: Aucune image source pour {card_number}")
                continue

            for src in sources:
                dest_name = src.stem + "_Q.png"
                dest = output_dir / dest_name
                shutil.copy2(src, dest)
                print(f"Carte quete copiee : {dest.name}")


# ---------------------------------------------------------------------------
# Traitement d'image : bleed (marge de coupe)
# ---------------------------------------------------------------------------

def convert_image_to_bleed(
    input_file: Path,
    output_dir: Path,
    prefix: str = "bleed",
    pad: int = 36,
) -> Path | None:
    """Ajoute une marge de coupe (bleed) autour d'une image.

    Technique : miroir horizontal + vertical autour de l'image originale,
    puis recadrage pour obtenir un debord de `pad` pixels.

    Retourne le chemin du fichier genere, ou None en cas d'erreur.
    """
    if not input_file.exists():
        print(f"ERREUR: Le fichier '{input_file}' n'existe pas.", file=sys.stderr)
        return None

    print(f"Creation de la marge de coupe ({pad}px) pour '{input_file.name}'")

    try:
        from magick import get_image_dimensions
        width, height = get_image_dimensions(input_file)
    except RuntimeError as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        return None

    # Fichiers temporaires
    flopped = output_dir / "_flopped.png"
    middle_row = output_dir / "_middle-row.png"
    flipped_row = output_dir / "_flipped-row.png"
    combined = output_dir / "_combined.png"
    output_file = output_dir / f"{prefix}-{input_file.name}"

    try:
        # Miroir horizontal
        run_magick(str(input_file), "-flop", str(flopped))
        # Ligne horizontale : flopped | original | flopped
        run_magick(str(flopped), str(input_file), str(flopped), "+append", str(middle_row))
        # Miroir vertical de la ligne
        run_magick(str(middle_row), "-flip", str(flipped_row))
        # Assemblage vertical : flipped | middle | flipped
        run_magick(str(flipped_row), str(middle_row), str(flipped_row), "-append", str(combined))
        # Recadrage
        shave_w = width - pad
        shave_h = height - pad
        run_magick(str(combined), "-shave", f"{shave_w}x{shave_h}", str(output_file))
    except RuntimeError as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        return None
    finally:
        # Nettoyage des temporaires
        for tmp in (flopped, middle_row, flipped_row, combined):
            tmp.unlink(missing_ok=True)

    return output_file


# ---------------------------------------------------------------------------
# Generation du PDF
# ---------------------------------------------------------------------------

def new_pdf_from_images(image_files: list[Path], output_pdf: Path) -> None:
    """Genere un PDF a partir d'une liste ordonnee d'images.

    Dimensions de carte : 69mm x 94mm a 330 DPI (format MBPrint).
    """
    if not image_files:
        print("AVERTISSEMENT: Aucun fichier image fourni. PDF non genere.")
        return

    print(f"Generation du PDF : '{output_pdf}'")

    # Supprimer le PDF existant
    if output_pdf.exists():
        output_pdf.unlink()
        print(f"PDF existant supprime : '{output_pdf}'")

    # Dimensions en pixels a 330 DPI
    mm_to_pixels = 12.9921  # 1 mm a 330 DPI
    card_w = int(69 * mm_to_pixels)
    card_h = int(94 * mm_to_pixels)

    args = [str(f) for f in image_files]
    args += [
        "-units", "PixelsPerCentimeter",
        "-density", "129.921x129.921",
        "-page", f"{card_w}x{card_h}",
        "-resize", f"{card_w}x{card_h}",
        "-gravity", "center",
        "-extent", f"{card_w}x{card_h}",
        str(output_pdf),
    ]

    try:
        run_magick(*args)
        print(f"PDF genere avec succes : '{output_pdf}'")
    except RuntimeError as e:
        print(f"ERREUR: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Orchestration finale
# ---------------------------------------------------------------------------

def process_images(
    source_dir: Path,
    source_pdf_dir: Path,
    output_dir: Path,
    prefix: str = "bleed",
) -> None:
    """Traite toutes les images par suffixe, applique le bleed, genere le PDF."""
    if not source_dir.exists():
        print(f"ERREUR: Le repertoire '{source_dir}' n'existe pas.", file=sys.stderr)
        return

    # Nom du deck (deux niveaux au-dessus)
    deck_name = source_dir.parent.parent.name
    new_output_dir = output_dir / deck_name
    new_output_dir.mkdir(parents=True, exist_ok=True)

    # Recuperer tous les fichiers image du repertoire PDF source
    image_files = sorted(
        f for f in source_pdf_dir.iterdir()
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg")
    )

    suffixes = ("_H", "_J", "_R", "_Q")
    all_ordered_files: list[Path] = []

    for suffix in suffixes:
        filtered = [f for f in image_files if suffix in f.stem]

        # Regrouper par paire face/dos
        pairs: dict[str, dict[str, Path | None]] = {}
        for f in filtered:
            base = re.sub(r"_dos$", "", f.stem)
            base = re.sub(rf"{re.escape(suffix)}$", "", base)
            if base not in pairs:
                pairs[base] = {"face": None, "dos": None}
            if f.stem.endswith("_dos"):
                pairs[base]["dos"] = f
            else:
                pairs[base]["face"] = f

        # Trier et traiter
        for key in sorted(pairs.keys()):
            pair = pairs[key]
            for role in ("face", "dos"):
                src_file = pair[role]
                if src_file is None:
                    continue
                print(f"Traitement : {src_file.name}")
                bleed_file = convert_image_to_bleed(src_file, new_output_dir, prefix)
                if bleed_file and bleed_file.exists():
                    final_name = new_output_dir / f"{src_file.stem}.png"
                    bleed_file.rename(final_name)
                    all_ordered_files.append(final_name)

    # Generer le PDF
    pdf_output = new_output_dir / f"{deck_name}.pdf"
    new_pdf_from_images(all_ordered_files, pdf_output)


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genere un PDF de cartes pret a l'impression (MBPrint)."
    )
    parser.add_argument(
        "--source-dir", required=True, type=Path,
        help="Repertoire contenant les images originales.",
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path,
        help="Repertoire de sortie pour les fichiers generes.",
    )
    parser.add_argument(
        "--file-path", required=True, type=Path,
        help="Fichier de configuration des plages de cartes (PREFIX.txt).",
    )
    parser.add_argument(
        "--deck-file-path", required=True, type=Path,
        help="Fichier de configuration du nombre d'exemplaires (PREFIX-Deck.txt).",
    )
    parser.add_argument(
        "--dos-hero-template", required=True, type=Path,
        help="Image du dos pour les cartes Heros.",
    )
    parser.add_argument(
        "--dos-joueur-template", required=True, type=Path,
        help="Image du dos pour les cartes Joueur.",
    )
    parser.add_argument(
        "--dos-rencontre-template", required=True, type=Path,
        help="Image du dos pour les cartes Rencontre.",
    )
    parser.add_argument(
        "--source-pdf-dir", required=True, type=Path,
        help="Repertoire contenant les images pour le PDF.",
    )

    args = parser.parse_args()

    # Etape 1 : Generation des cartes et de leurs dos
    print("=" * 60)
    print("ETAPE 1 : Generation des cartes")
    print("=" * 60)

    creation_heros(args.file_path, args.source_dir, args.dos_hero_template, args.output_dir)
    creation_joueur(args.file_path, args.source_dir, args.dos_joueur_template, args.output_dir)
    creation_deck_rencontre(
        args.file_path, args.deck_file_path, args.source_dir,
        args.dos_rencontre_template, args.output_dir,
    )
    creation_deck_quete(args.file_path, args.source_dir, args.output_dir)

    # Etape 2 : Traitement bleed + generation PDF
    print("=" * 60)
    print("ETAPE 2 : Bleed et generation du PDF")
    print("=" * 60)

    process_images(args.source_dir, args.source_pdf_dir, args.output_dir)

