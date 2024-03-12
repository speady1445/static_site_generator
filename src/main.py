import shutil
from os import rmdir
from pathlib import Path

PUBLIC_FOLDER = Path("public")
STATIC_FOLDER = Path("static")


def main() -> None:
    copy_static_to_public()


def copy_static_to_public() -> None:
    delete_folder(PUBLIC_FOLDER)
    copy_folder(STATIC_FOLDER, PUBLIC_FOLDER)


def delete_folder(folder: Path) -> None:
    if folder.exists():
        for file in folder.glob("*"):
            if file.is_file():
                print(f"Removing file: '{file}'")
                file.unlink()
            else:
                delete_folder(file)
        print(f"Removing folder: '{folder}'")
        rmdir(folder)
        print()


def copy_folder(source: Path, destination: Path) -> None:
    if not destination.exists():
        destination.mkdir()
    for file in source.glob("*"):
        if file.is_file():
            print(f"Copying file: '{file}' to '{destination}'")
            shutil.copy(file, destination)
        else:
            sub_destination = destination / file.name
            print(f"Creating folder: '{sub_destination}'")
            sub_destination.mkdir()
            print(f"Copying folder: '{file}' to '{sub_destination}'")
            copy_folder(file, sub_destination)


if __name__ == "__main__":
    main()
