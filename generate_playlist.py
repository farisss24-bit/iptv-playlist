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
    "se": "🇸🇪 Suède",
    "no": "🇳🇴 Norvège",
    "dk": "🇩🇰 Danemark",
    "fi": "🇫🇮 Finlande",
    "pl": "🇵🇱 Pologne",
    "cz": "🇨🇿 Tchéquie",
    "gr": "🇬🇷 Grèce",
    "ro": "🇷🇴 Roumanie",
    "bg": "🇧🇬 Bulgarie",
    "hr": "🇭🇷 Croatie",
    "rs": "🇷🇸 Serbie",
    "ua": "🇺🇦 Ukraine",
    "ru": "🇷🇺 Russie",
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


def extract_country_urls(text):
    pattern = r"https://iptv-org\.github\.io/iptv/countries/[a-z]{2}\.m3u"

    return re.findall(pattern, text.lower())


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
            j = i + 1

            while j < len(lines):
                stream_url = lines[j].strip()

                if stream_url and not stream_url.startswith("#"):
                    break

                j += 1

            if j < len(lines):

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

    # Lire countries.txt
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        source = f.read()

    print("Lecture de la source...")

    # Le fichier contient le lien vers le Gist
    if source.startswith("http"):

        print("Téléchargement du Gist...")

        try:
            source = download(source)
        except Exception as e:
            print(f"Impossible de télécharger le Gist : {e}")
            return

    # Récupérer automatiquement tous les liens pays
    urls = extract_country_urls(source)

    # Supprimer les doublons tout en gardant l'ordre
    urls = list(dict.fromkeys(urls))

    print(f"{len(urls)} pays trouvés.")

    playlist = ["#EXTM3U"]

    for url in urls:
        channels = process_playlist(url)
        playlist.extend(channels)

    Path(OUTPUT_FILE).write_text(
        "\n".join(playlist) + "\n",
        encoding="utf-8"
    )

    print("================================")
    print("Playlist créée avec succès !")
    print(f"Pays : {len(urls)}")
    print(f"Lignes : {len(playlist)}")
    print("================================")


if __name__ == "__main__":
    main()
