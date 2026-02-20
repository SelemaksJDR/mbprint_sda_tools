import infos
import pathlib

def validate_field(json_data: dict, name: str) -> bool:
    if name not in json_data:
        print(f"Le fichier {json_data} ne contient pas le champs {name}")
        return False
    return True


def validate_string_array(json_data: dict, name: str) -> bool:
    if validate_field(json_data=json_data, name=name) is False:
        return False
    if isinstance(json_data[name], list) is False:
        print(f"L'élément {name} n'est pas un tableau")
        return False
    for array_elem in json_data[name]:
        if isinstance(array_elem, str) is False:
            print(f"L'élément {array_elem} n'est pas une string")
            return False
    return True


def validate_extension(extension_data: dict) -> bool:
    # Heros
    if validate_string_array(json_data=extension_data, name=infos.EXTENSION_HEROES) is False:
        return False
    # Joueurs
    if validate_string_array(json_data=extension_data, name=infos.EXTENSION_PLAYERS) is False:
        return False
    # Contrats optionel
    if infos.EXTENSION_CONTRACTS in extension_data:
        if validate_string_array(json_data=extension_data, name=infos.EXTENSION_CONTRACTS) is False:
            return False
    # Quêtes
    if validate_string_array(json_data=extension_data, name=infos.EXTENSION_QUESTS) is False:
        return False
    # flip cards
    if validate_field(json_data=extension_data, name=infos.EXTENSION_FLIP_CARDS) is False:
        return False
    # Rencontres
    if validate_field(json_data=extension_data, name=infos.EXTENSION_ENCOUNTERS) is False:
        return False
    for extension in extension_data[infos.EXTENSION_ENCOUNTERS]:
        if validate_field(json_data=extension, name=infos.ENCOUNTERS_SERIE_NAME) is False:
            return False
        if validate_field(json_data=extension, name=infos.ENCOUNTERS_SERIE_NUMBER_CARDS) is False:
            return False
        if validate_field(json_data=extension, name=infos.ENCOUNTERS_SERIE_CARDS) is False:
            return False
    return True


def get_cycle_extensions(cycle_data: dict) -> list:
    return [elem for elem in cycle_data if ((elem != infos.CYCLE_NAME) and (elem != infos.CYCLE_FOLDER))]


def validate_config_json(config_data: dict) -> bool:
    if validate_field(json_data=config_data, name="workspace") is False:
        print(f"L'élément workspace n'existe pas dans le fichier {config_data}")
        return False
    # Récupération de la racine des fichiers images
    if validate_field(config_data["workspace"], name="root_pictures") is False:
        print(f"L'élément root_pictures n'existe pas dans le workspace")
        return False
    # Récupération du dossier de configuration
    if validate_field(config_data["workspace"], name="config_folder") is False:
        print(f"L'élément config_folder n'existe pas dans le workspace")
        return False
    if validate_field(config_data["workspace"]["config_folder"], name="fix_filenames") is False:
        print(f"L'élément fix_filenames n'existe pas dans le config_folder")
        return False
    # Récupération du chemin vers le dossier de résultat
    if validate_field(config_data["workspace"], name="result_folder") is False:
        print(f"L'élément result_folder n'existe pas dans le workspace")
        return False
    # Récupération du chemin vers les dos de carte
    if validate_field(config_data["workspace"], name="backs") is False:
        print(f"L'élément backs n'existe pas dans le workspace")
        return False
    # cycles
    if validate_field(json_data=config_data, name="cycles") is False:
        print(f"L'élément cycles n'existe pas dans le fichier {config_data}")
        return False
    return True


def validate_cycle_json(cycle_data: dict) -> bool:
    if validate_field(json_data=cycle_data, name=infos.CYCLE_NAME) is False:
        return False
    if validate_field(json_data=cycle_data, name=infos.CYCLE_FOLDER) is False:
        return False
    # Check les différentes extensions
    for extension in get_cycle_extensions(cycle_data):
        if validate_extension(extension_data=cycle_data[extension]) is False:
            print(f"Erreur dans l'extension {extension}")
            return False
    return True


# flag
IS_FIRST: bool = True

def path_exists_with_fix(img_path: pathlib.Path, fix_config_object: dict) -> bool | pathlib.Path:
    if pathlib.Path.exists(img_path) is False:
        # Recherche dans le fichier de fix
        for error_name, fixed_name in fix_config_object.items():
            error_path = img_path.parent / pathlib.Path(pathlib.Path(error_name).name)
            fixed_path = img_path.parent / pathlib.Path(pathlib.Path(fixed_name).name)
            if img_path.name == fixed_path.name:
                if pathlib.Path.exists(error_path) is True:
                    global IS_FIRST
                    if IS_FIRST is True:
                        IS_FIRST = False
                        print(f"[ATTENTION] Le fichier fix_config.jsonc est nécessaire pour trouver certains chemins. Vous devriez utiliser le script fix_files.py")
                    return True, error_path
                print(f"[ERREUR] Le fichier {img_path.name} n'est pas présent dans le dossier {img_path.parent} et n'a pas d'autre nom")
                return False, img_path
    return True, img_path

