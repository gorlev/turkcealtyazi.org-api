from types import new_class
from flask import Flask
from flask_restful import Resource, Api
import requests, json
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def homepage():
    return "Welcome to TurkceAltyazi.org subtitle finder!"

@app.route("/subtitle", methods=["GET"])
def get():
    return ("Please type the IMDB ID after the /subtitle/(imdbid)")

@app.route("/subtitle/<int:imdbid>", methods = ["GET"])
def get_imdb_id(imdbid):
    params = (
    ('t', '99'),
    ('term', imdbid)
    )

    response = requests.get('https://turkcealtyazi.org/things_.php', params=params)
    global url
    r = response.text
    j = json.loads(r)
    url = j[0]["url"]
    url = "https://turkcealtyazi.org" + url

    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")

    subtitle_data = []
    try:    
        for altyazi in soup.find_all("div", class_="altsonsez1") or soup.find_all("div", class_="altsonsez2"):
            altyazi_medya_adi = altyazi.a.text
            
            new_imdbid = "tt" + str(imdbid)

            #ALTYAZININ UYUMLU SÜRÜMÜNÜ VERİYOR +
            altyazi_uyumluluk = altyazi.find("div", class_="ripdiv").text
            altyazi_uyumluluk = altyazi_uyumluluk[2:len(altyazi_uyumluluk)-1]

            #ALTYAZININ TAM ADI: +
            altyazi_full_name = altyazi_medya_adi + " : " + altyazi_uyumluluk

            #ALTYAZI DİLİ: +
            altyazi_dili = altyazi.find("div", class_ = "aldil").span["class"]
            altyazi_dili = str(altyazi_dili)
            altyazi_dili = altyazi_dili[6:len(altyazi_dili)-2]

            #ALTYAZI ÇEVİRMENİ: +
            altyazi_cevirmeni = altyazi.find("div", class_ = "alcevirmen").text
            temp = altyazi.find("span", class_ = "cps c1")
            if temp != None :
                altyazi_cevirmeni = "Anonim"

            #ALTYAZI FPS DEĞERİ: +
            altyazi_fps = altyazi.find("div", class_="alfps").text

            #ALTYAZI SEZON BÖLÜM BULUCU:
            altyazi_season_episode = altyazi.find("div", class_="alcd").text
            altyazi_season_episode = altyazi_season_episode[1:len(altyazi_season_episode)-1]
            altyazi_season_episode = altyazi_season_episode.replace("\n", " ")

            #ALTYAZI ID BULUCU (altid) +
            altid = altyazi.find("a", class_ = "underline")["id"]

            #İLGİLİ ALTYAZININ SAYFASINA GÖTÜRÜYOR: +
            altid_page = altyazi.find("a", class_ = "underline")["href"]
            altid_page_url = "https://www.turkcealtyazi.org" + altid_page

            #ALTYAZI İNDİRME ID'Sİ BULUCU (idid) +
            altid_page_source = requests.get(altid_page_url).text
            soup2 = BeautifulSoup(altid_page_source, "lxml")

            try:
                idid_step1 = soup2.find("div", class_="sub-container nleft") 
                idid = idid_step1.div.input["value"]
            except AttributeError:
                idid_step1 = soup2.find("div", class_="nblock") 
                idid = idid_step1.input["value"]
                pass

            """#TÜR BULUCU:
            genre_step1 = soup2.find("div", class_ ="newtabs ta-container")
            genre = genre_step1.a.text"""

            if (altyazi_season_episode != "2"): # 2 CD'Sİ OLAN FİLMLERİ GÖRSTERMİYOR.
                subtitle_data.append({"name" : altyazi_medya_adi, "variation": altyazi_uyumluluk,"language" : altyazi_dili, "translator": altyazi_cevirmeni, "fps": altyazi_fps ,"imdb_id": imdbid, "season": altyazi_season_episode, "idid": idid, "altid" : altid, "imddb_id" : new_imdbid})
                subtitles = json.dumps(subtitle_data, indent=4, ensure_ascii=False)
        
        return subtitles
    except UnboundLocalError:
        return {'data': 'Subtitle could not found'}

if __name__ == '__main__':
    app.run(debug=True, port=5001)
