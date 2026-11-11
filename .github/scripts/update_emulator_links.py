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
        "path_pattern": re.compile(r"emulators/Cemu/Cemu_[^/\s\"]+/Cemu\.exe"),
        "build_path": lambda tag: (
            f"emulators/Cemu/Cemu_{tag.lstrip('v')}/Cemu.exe"
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
            r"https://github\.com/azahar-emu/azahar/releases/download/[^/\s]+/"
            r"azahar-(?:[^/\s]+-windows-msvc|windows-msvc-[^/\s]+)\.zip"
        ),
        "build_url": lambda tag: (
            f"https://github.com/azahar-emu/azahar/releases/download/{tag}"
            f"/azahar-windows-msvc-{tag}.zip"
        ),
        "path_pattern": re.compile(
            r"emulators/Azahar/azahar-[^/\s\"]+/azahar\.exe"
        ),
        "build_path": lambda tag: (
            f"emulators/Azahar/azahar-windows-msvc-{tag}/azahar.exe"
        ),
    },
    {
        "console": "Switch",
        "emu": "Eden",
        "api_url": "https://git.eden-emu.dev/api/v1/repos/eden-emu/eden/releases",
        "files": [
            "mistik-launcher-code.py",
        ],
        "pattern": re.compile(
            r"https://stable\.eden-emu\.dev/[^/\s]+/Eden-Windows-[^/\s]+-amd64-msvc-standard\.zip"
        ),
        "build_url": lambda tag: (
            f"https://stable.eden-emu.dev/{tag}/Eden-Windows-{tag}-amd64-msvc-standard.zip"
        ),
    },
    {
        "console": "Switch (Online)",
        "emu": "Ryujinx Nextendo",
        "api_url": "https://git.nextendo.network/api/v1/repos/NextendoNetwork/Ryujinx-Nextendo/releases",
        "files": [
            "mistik-launcher-code.py",
        ],
        "pattern": re.compile(
            r"https://git\.nextendo\.network/NextendoNetwork/Ryujinx-Nextendo/releases/download/[^/\s]+/Nextendo-[^/\s]+-win-x64\.zip"
        ),
        "build_url": lambda tag: (
            f"https://git.nextendo.network/NextendoNetwork/Ryujinx-Nextendo/releases/download/{tag}/Nextendo-{tag.lstrip('v')}-win-x64.zip"
        ),
    },
]


def get_latest_tag_forgejo(api_url: str) -> str:
    """Devuelve el tag de la ultima release desde APIs compatibles con Forgejo/Gitea."""
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    if isinstance(data, list) and len(data) > 0 and data[0].get("tag_name"):
        return data[0]["tag_name"]
    raise RuntimeError(f"No se pudo obtener el tag de release desde {api_url}")


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
            if "api_url" in emulator:
                tag = get_latest_tag_forgejo(emulator["api_url"])
            else:
                tag = get_latest_tag(emulator["repo"])
            new_url = emulator["build_url"](tag)

            for file_name in emulator["files"]:
                with open(file_name, "r", encoding="utf-8") as file:
                    content = file.read()

                new_content, url_replacements = emulator["pattern"].subn(
                    new_url, content
                )

                path_replacements = 0
                new_path = None
                if "path_pattern" in emulator and "build_path" in emulator:
                    new_path = emulator["build_path"](tag)
                    new_content, path_replacements = emulator["path_pattern"].subn(
                        new_path, new_content
                    )

                if (url_replacements > 0 or path_replacements > 0) and new_content != content:
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(new_content)
                    print(
                        f"[{emulator['console']}] {emulator['emu']}: "
                        f"enlace actualizado a {new_url}"
                    )
                    if path_replacements > 0:
                        print(
                            f"[{emulator['console']}] {emulator['emu']}: "
                            f"ruta actualizada a {new_path}"
                        )
                    updated = True

        except Exception as e:
            print(f"[{emulator['console']}] No se pudo actualizar el enlace: {e}")

    if not updated:
        print("No se realizaron cambios en los enlaces de descarga.")


if __name__ == "__main__":
    main()
