import re
import urllib.request
from pathlib import Path

INPUT_FILE = "countries.txt"
OUTPUT_FILE = "playlist.m3u"
EXTRA_FILE = "selection_FranceSD_Belgique_MBC_News_UK.m3u"


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def country_name(code):
    names = {
        "fr": "🇫🇷 France",
        "be": "🇧🇪 Belgique",
        "dz": "🇩🇿 Algérie",
        "ma": "🇲🇦 Maroc",
    }
    return names.get(code, code.upper())


def get_country_urls():
    lines = Path(INPUT_FILE).read_text(
        encoding="utf-8"
    ).splitlines()

    urls = []

    for line in lines:
        line = line.strip()

        if line.startswith("http://") or line.startswith("https://"):
            if "/countries/" in line and line.endswith(".m3u"):
                if line not in urls:
                    urls.append(line)

    return urls


def process_country(url):

    match = re.search(
        r"/countries/([a-zA-Z]{2})\.m3u",
        url
    )

    if not match:
        return []

    code = match.group(1).lower()
    country = country_name(code)

    print(f"Traitement : {country}")

    try:
        content = download(url)
    except Exception as error:
        print(f"ERREUR : {error}")
        return []

    lines = content.splitlines()
    output = []

    for i, line in enumerate(lines):

        if not line.startswith("#EXTINF:"):
            continue

        info = line

        stream_url = None

        for j in range(i + 1, min(i + 5, len(lines))):

            candidate = lines[j].strip()

            if candidate.startswith("http"):
                stream_url = candidate
                break

        if not stream_url:
            continue

        # Supprimer l'ancien group-title
        info = re.sub(
            r'\s*group-title="[^"]*"',
            "",
            info
        )

        # Ajouter le pays
        info = re.sub(
            r'(#EXTINF:[^ ]+)',
            rf'\1 group-title="{country}"',
            info,
            count=1
        )

        output.append(info)
        output.append(stream_url)

    print(
        f"  → {len(output) // 2} chaînes trouvées"
    )

    return output

def process_extra_file(filename):
    path = Path(filename)

    if not path.exists():
        print(f"Fichier supplémentaire introuvable : {filename}")
        return []

    print(f"Ajout du fichier : {filename}")

    lines = path.read_text(
        encoding="utf-8",
        errors="replace"
    ).splitlines()

    output = []

    for line in lines:
        line = line.strip()

        if not line or line == "#EXTM3U":
            continue

        output.append(line)

    count = sum(
        1 for line in output
        if line.startswith("#EXTINF:")
    )

    print(f"  → {count} chaînes supplémentaires")
    return output
def main():

    print("====================================")
    print("GÉNÉRATION PLAYLIST IPTV")
    print("====================================")

    urls = get_country_urls()

    print(f"Pays trouvés : {len(urls)}")

    if not urls:
        print("Aucun pays trouvé.")
        return

    playlist = ["#EXTM3U"]

    for url in urls:
        playlist.extend(
            process_country(url)
        )
    playlist.extend(
        process_extra_file(EXTRA_FILE)
    )
    Path(OUTPUT_FILE).write_text(
        "\n".join(playlist) + "\n",
        encoding="utf-8"
    )

 total = sum(
    1 for line in playlist
    if line.startswith("#EXTINF:")
)

    print("====================================")
    print("PLAYLIST TERMINÉE")
    print(f"Pays : {len(urls)}")
    print(f"Chaînes : {total}")
    print("====================================")


if __name__ == "__main__":
    main()
