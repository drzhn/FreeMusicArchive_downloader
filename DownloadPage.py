import requests
from lxml import html
from lxml import etree
import os
from time import sleep

def get_num_pages(url):
    r = requests.get(url)
    text = r.content.decode()
    tree = html.fromstring(text)
    pages_info = tree.xpath('//div[@class = "pagination-full"]//a/text()')[-2]
    return int(pages_info)


def check_license(url):
    r = requests.get(url)
    text = r.content.decode()
    tree = html.fromstring(text)
    license_info = tree.xpath('//div[@class = "colr-sml-toppad"]//a/text()')
    # print(license_info)
    for item in license_info:
        if ("License" in item):
            if ("NonCommercial" in item):
                return False, item
            else:
                return True, item
    return False, ""


def get_audios_from_page(url, params):
    r = requests.get(url, params)
    text = r.content.decode()
    tree = html.fromstring(text)
    length = len(tree.xpath('//div[@class = "playtxt"]'))
    ret = []
    for i in range(length):
        track_info = tree.xpath('//div[@class = "playtxt"]')[i]
        # print(etree.tostring(track_info).decode())
        artist = track_info.xpath('.//span[@class = "ptxt-artist"]/a/text()')[0]
        try:
            album = track_info.xpath('.//span[@class = "ptxt-album"]/a/text()')[0]
        except:
            album = "-"
        track = track_info.xpath('.//span[@class = "ptxt-track"]/a/text()')[0]
        track_url = track_info.xpath('.//span[@class = "ptxt-track"]/a/@href')[0]
        download_link = tree.xpath('//span[@class = "playicn"]/a/@href')[i * 2]
        ret.append(
            {"artist": artist, "album": album, "track": track, "track_url": track_url, "download_link": download_link})
        # print(artist)
        # print(album)
        # print(track)
        # print(track_url)
        # print(download_link)
    return ret


def download_genre(url, num_start, num_end):
    tracks = []
    for i in range(num_start, num_end):
        params = {'sort': 'track_date_published', 'page': str(i)}
        tracks += get_audios_from_page(url, params)
        print(i, " page done")
    print(str(len(tracks))+" files in common")
    file_info = open("info.txt", "w")
    i = 0
    for track in tracks:
        license_info = check_license(track["track_url"])
        if (license_info[0] == True):
            filename = str(i + 1) + ". " + track["artist"] + " - " + track["track"]
            try:
                file_info.write(filename + " " + license_info[1] + "\n")
            except:
                file_info.write(str(i + 1) + ". <unnown>" + track["track_url"] + " " + license_info[1] + "\n")
            r = requests.get(track["download_link"])
            f = open("audios/" + filename + ".mp3", "wb")
            f.write(r.content)
            f.close()
            i += 1
            print(i, " file done")
        sleep(0.5)

if not os.path.isdir("audios"):
    os.mkdir("audios")
url = "http://freemusicarchive.org/genre/Ambient_Electronic/"
num = get_num_pages(url)
print(num, " pages")
download_genre(url, 1,num+1)


# check_license("http://freemusicarchive.org/music/David_Hilowitz/~/David_Hilowitz_-_Film_Cue_018_-_Rima_Banya_Theme")
# check_license("http://freemusicarchive.org/music/Kai_Engel/Irsens_Tale/Kai_Engel_-_Irsens_Tale_-_04_Moonlight_Reprise")
# get_num_pages(url)
