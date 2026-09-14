import re
import urllib.request
from pathlib import Path

INPUT_FILE = "countries.txt"
OUTPUT_FILE = "playlist.m3u"


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def country_name(code):
    names = {
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

    return names.get(code, code.upper())


def find_country_urls(text):
    pattern = r"https?://iptv-org\.github\.io/iptv/countries/([a-zA-Z]{2})\.m3u"

    matches = re.findall(pattern, text)

    result = []

    for code in matches:
        code = code.lower()
        url = f"https://iptv-org.github.io/iptv/countries/{code}.m3u"

        if url not in result:
            result.append(url)

    return result


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
        print(f"ERREUR {country}: {error}")
        return []

    lines = content.splitlines()
    output = []

    for i, line in enumerate(lines):

        if not line.startswith("#EXTINF:"):
            continue

        info = line

        # Cherche l'URL de la chaîne
        stream_url = None

        for j in range(i + 1, min(i + 5, len(lines))):
            candidate = lines[j].strip()

            if candidate.startswith("http"):
                stream_url = candidate
                break

        if not stream_url:
            continue

        # Supprime l'ancien group-title
        info = re.sub(
            r'group-title="[^"]*"',
            "",
            info
        )

        # Ajoute notre groupe pays
        if info.startswith("#EXTINF:-1"):
            info = info.replace(
                "#EXTINF:-1",
                f'#EXTINF:-1 group-title="{country}"',
                1
            )

        output.append(info)
        output.append(stream_url)

    print(f"  → {len(output) // 2} chaînes trouvées")

    return output


def main():

    print("====================================")
    print("GÉNÉRATION PLAYLIST IPTV")
    print("====================================")

    # Lire countries.txt
    source_file = Path(INPUT_FILE)

    if not source_file.exists():
        print("ERREUR : countries.txt introuvable")
        return

    source = source_file.read_text(
        encoding="utf-8"
    ).strip()

    # Si countries.txt contient le lien vers le Gist
    if source.startswith("http"):

        print("Téléchargement du Gist...")

        try:
            source = download(source)
        except Exception as error:
            print(f"ERREUR Gist : {error}")
            return

    # Trouver les pays
    urls = find_country_urls(source)

    print(f"Pays trouvés : {len(urls)}")

    if not urls:
        print("Aucun lien IPTV-org trouvé.")
        print("Vérifie le contenu de ton Gist.")
        return

    playlist = ["#EXTM3U"]

    for url in urls:
        playlist.extend(
            process_country(url)
        )

    Path(OUTPUT_FILE).write_text(
        "\n".join(playlist) + "\n",
        encoding="utf-8"
    )

    print("====================================")
    print("PLAYLIST TERMINÉE")
    print(f"Pays : {len(urls)}")
    print(f"Chaînes : {(len(playlist) - 1) // 2}")
    print("====================================")


if __name__ == "__main__":
    main()
