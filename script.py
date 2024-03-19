import requests
import re
import json

BASE_URL = 'http://www.comuni-italiani.it/'

regioni_dict = {
        "Abruzzo": "13",
        "Basilicata": "17",
        "Calabria": "18",
        "Campania": "15",
        "Emilia-Romagna": "08",
        "Friuli-Venezia Giulia": "06",
        "Lazio": "12",
        "Liguria": "07",
        "Lombardia": "03",
        "Marche": "11",
        "Molise": "14",
        "Piemonte": "01",
        "Puglia": "16",
        "Sardegna": "20",
        "Sicilia": "19",
        "Toscana": "09",
        "Trentino-Alto Adige": "04",
        "Umbria": "10",
        "Valle d'Aosta": "02",
        "Veneto": "05"
        }

def get_climate_info(prov_code, comune_code):
    cleaned_prov_code = prov_code.replace('index.html', '')
    comune_code = comune_code.replace('index', 'clima')
    resp = requests.get(BASE_URL + cleaned_prov_code + comune_code)
    name_pattern = r"<title>(.*?):Clima"
    name = resp.text.split('Clima')[0]
    name = name.replace('<html><head><title>', '').replace(':', '').strip()
    text = resp.text.split('Clima e Dati Geografici')[2]
    text = text.split('Accensione Impianti Termici')[0]
    pattern_tr = r"<tr>(.*?)</tr>"
    trs = re.findall(pattern_tr, text)
    data = {}
    for tr in trs:
        pattern_td = r"<td\b[^>]*>(.*?)</td>"
        tds = re.findall(pattern_td, tr, re.DOTALL)
        if len(tds) == 2:
            try:
                data[tds[0]] = int(tds[1])
            except:
                try:
                    data[tds[0]] = float(tds[1])
                except:
                    data[tds[0]] = tds[1]
    return name, data

def get_data_comuni(prov_code):
    resp = requests.get(BASE_URL + prov_code)
    resp_text = resp.text
    resp_text = resp_text.split('Lista comuni della provincia')[1]
    resp_text = resp_text.split('Per segnalare')[0]
    pattern = r"<a href=\"(.*?)\">"
    matches = re.findall(pattern, resp_text)
    comuni_links = [_ for _ in matches if 'index.html' in _]
    result = {}
    for link in comuni_links:
        name, climate_data = get_climate_info(prov_code, link)
        result[name] = climate_data
    return result

def generate_info(regione):
    code = regioni_dict[regione]
    resp = requests.get(BASE_URL + code)
    resp_text = resp.text.encode('utf8')
    province = resp_text.decode('utf8').split('Lista Province della Regione')[1]
    province = province.split('Informazioni Base')[0]
    pattern = r"href=\"(.*?)\</a>"
    matches = re.findall(pattern, province)
    prov_links = [_.split('">') for _ in matches]
    result = {}
    for link in prov_links:
        prov_code = link[0].replace('../', '')
        prov_name = link[1]
        result[prov_name] = get_data_comuni(prov_code)
    with open(f"{regione.lower().replace(' ', '_')}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print('Done')

generate_info("Campania")
