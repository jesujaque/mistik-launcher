"""Actualiza automaticamente los enlaces de descarga de los emuladores
en los archivos fuente del launcher, usando la ultima release publicada."""

import json
import re
import urllib.request

GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"

EMULATORS = [
    {
        "console": "Wii",
        "emu": "Dolphin",
        "repo": "dolphin-emu/dolphin",
        "files": [
            "mistik-launcher-code.py",
        ],
        "pattern": re.compile(
            r"https://dl\.dolphin-emu\.org/releases/[^/\s]+/dolphin-[^/\s]+-x64\.7z"
        ),
        "build_url": lambda tag: (
            f"https://dl.dolphin-emu.org/releases/{tag}/dolphin-{tag}-x64.7z"
        ),
    },
    {
        "console": "Wii U",
        "emu": "Cemu",
        "repo": "cemu-project/Cemu",
        "files": [
            "mistik-launcher-code.py",
        ],
        "pattern": re.compile(
            r"https://github\.com/cemu-project/Cemu/releases/download/[^/\s]+/cemu-[^/\s]+\.zip"
        ),
        "build_url": lambda tag: (
            f"https://github.com/cemu-project/Cemu/releases/download/{tag}"
            f"/cemu-{tag.lstrip('v')}-windows-x64.zip"
        ),
    },
    {
        "console": "3DS",
        "emu": "Azahar",
        "repo": "azahar-emu/azahar",
        "files": [
            "mistik-launcher-code.py",
        ],
        "pattern": re.compile(
            r"https://github\.com/azahar-emu/azahar/releases/download/[^/\s]+/azahar-[^/\s]+\.zip"
        ),
        "build_url": lambda tag: (
            f"https://github.com/azahar-emu/azahar/releases/download/{tag}"
            f"/{tag}-windows-msvc.zip"
        ),
    },
]


def get_latest_tag(repo: str) -> str:
    """Devuelve el tag de la ultima release; si no hay releases, usa los tags."""
    # 1. Intentar obtener la ultima release
    try:
        url = GITHUB_API.format(repo=repo)
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data.get("tag_name"):
            return data["tag_name"]
    except Exception:
        pass

    # 2. Fallback: si el repo no tiene releases, usar los tags de version
    #    (ej. dolphin-emu/Dolphin usa tags tipo "2509", "2609", ...)
    url = f"https://api.github.com/repos/{repo}/tags?per_page=100"
    with urllib.request.urlopen(url, timeout=15) as response:
        tags = json.loads(response.read().decode("utf-8"))
    version_tags = [t["name"] for t in tags if re.fullmatch(r"\d{4}[a-z]?", t["name"])]
    if not version_tags:
        raise RuntimeError(f"No se encontraron tags de version en {repo}")
    return max(version_tags)


def main() -> None:
    updated = False

    for emulator in EMULATORS:
        try:
            tag = get_latest_tag(emulator["repo"])
            new_url = emulator["build_url"](tag)

            for file_name in emulator["files"]:
                with open(file_name, "r", encoding="utf-8") as file:
                    content = file.read()

                new_content, replacements = emulator["pattern"].subn(new_url, content)

                if replacements > 0 and new_content != content:
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(new_content)
                    print(
                        f"[{emulator['console']}] {emulator['emu']}: "
                        f"enlace actualizado a {new_url}"
                    )
                    updated = True

        except Exception as e:
            print(f"[{emulator['console']}] No se pudo actualizar el enlace: {e}")

    if not updated:
        print("No se realizaron cambios en los enlaces de descarga.")


if __name__ == "__main__":
    main()
