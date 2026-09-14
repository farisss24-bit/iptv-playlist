import re
import urllib.request
from pathlib import Path

INPUT_FILE = "countries.txt"
OUTPUT_FILE = "playlist.m3u"

COUNTRY_NAMES = {
    "dz": "🇩🇿 Algérie",
    "bh": "🇧🇭 Bahreïn",
    "fr": "🇫🇷 France",
    "be": "🇧🇪 Belgique",
    "de": "🇩🇪 Allemagne",
    "es": "🇪🇸 Espagne",
    "it": "🇮🇹 Italie",
    "pt": "🇵🇹 Portugal",
    "nl": "🇳🇱 Pays-Bas",
    "lu": "🇱🇺 Luxembourg",
    "gb": "🇬🇧 Royaume-Uni",
    "ch": "🇨🇭 Suisse",
    "at": "🇦🇹 Autriche",
    "tr": "🇹🇷 Turquie",
    "ma": "🇲🇦 Maroc",
    "tn": "🇹🇳 Tunisie",
    "ca": "🇨🇦 Canada",
    "us": "🇺🇸 États-Unis",
    "br": "🇧🇷 Brésil",
    "mx": "🇲🇽 Mexique",
    "in": "🇮🇳 Inde",
    "jp": "🇯🇵 Japon",
    "kr": "🇰🇷 Corée du Sud",
    "au": "🇦🇺 Australie",
}

def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def country_from_url(url):
    match = re.search(r"/countries/([a-z]{2})\.m3u", url.lower())

    if not match:
        return None

    code = match.group(1)

    return COUNTRY_NAMES.get(code, code.upper())


def process_playlist(url):
    country = country_from_url(url)

    if not country:
        print(f"Pays non reconnu : {url}")
        return []

    print(f"Traitement : {country}")

    try:
        content = download(url)
    except Exception as e:
        print(f"Erreur téléchargement {url}: {e}")
        return []

    lines = content.splitlines()
    result = []

    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF:"):

            info = line

            # Cherche l'URL qui suit EXTINF
            j = i + 1

            while j < len(lines):
                stream_url = lines[j].strip()

                if stream_url and not stream_url.startswith("#"):
                    break

                j += 1

            if j < len(lines):

                # Ajoute/remplace group-title
                if "group-title=" in info:
                    info = re.sub(
                        r'group-title="[^"]*"',
                        f'group-title="{country}"',
                        info
                    )
                else:
                    info = info.replace(
                        "#EXTINF:-1",
                        f'#EXTINF:-1 group-title="{country}"',
                        1
                    )

                result.append(info)
                result.append(stream_url)

                i = j

        i += 1

    return result


def main():

    urls = []

    # Lecture des liens
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("http"):
                urls.append(line)

    print(f"{len(urls)} playlists trouvées.")

    playlist = ["#EXTM3U"]

    for url in urls:
        channels = process_playlist(url)
        playlist.extend(channels)

    Path(OUTPUT_FILE).write_text(
        "\n".join(playlist) + "\n",
        encoding="utf-8"
    )

    print(f"Playlist créée : {OUTPUT_FILE}")
    print(f"Nombre total de lignes : {len(playlist)}")


if __name__ == "__main__":
    main()
