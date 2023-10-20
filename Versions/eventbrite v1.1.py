import scraper_helper
import requests
import scraper_helper
import pandas as pd
import json
from scrapy import Selector
import time


def get_headers():
    headers = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate, br
    Accept-Language: en-US,en;q=0.9
    Cache-Control: max-age=0
    Connection: keep-alive
    Cookie: mgrefby=; G=v%3D2%26i%3D15cd4a5d-6d83-4490-90d4-dad6be92b22a%26a%3Dfe9%26s%3Df118a6056997bf258b921d39bd67b4a2a4d77114; eblang=lo%3Den_CA%26la%3Den-ca; AS=f80ac7a4-9c07-4e45-b980-fc48e126a138; mgref=typeins; client_timezone="%22Asia/Karachi%22"; csrftoken=310c6d34f4a711ecaaafcf1f378c03a3; _gid=GA1.2.666656704.1656175950; ebGAClientId=108199645.1656175950; _gcl_au=1.1.1151388565.1656175950; SERVERID=djc89; _fbp=fb.1.1656175951738.2050084596; _scid=9971f2f7-f7f5-48ad-abba-180503c1c98d; _sctr=1|1656140400000; hubspotutk=148da554ffa0d5a8e64fef78c845f442; __hssrc=1; _pin_unauth=dWlkPVltSTFZVEF6Tm1VdFkyWTBOQzAwT0RVekxUZzRZVEF0TVRVMlkyRTROalE1TURZMg; SS=AE3DLHS5SKjnOlsBC6D0tfEc829qgJp0Mg; _gat=1; _hp2_id.1404198904=%7B%22userId%22%3A%228956934493665454%22%2C%22pageviewId%22%3A%223033733034593047%22%2C%22sessionId%22%3A%222700249402826399%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; SP=AGQgbbm9MgppV7znKih9w0y40GHzBCeGPgKPkpvb3cpP6g1XFGm1ug8UE7HHxmF7_7k0RQq9XmstpKWdcFbU8w9sciXVxVSbRbjsyBWp1ViIfnbCNqkjBdduz-oxb-cEQPcXVOSeO6kd6RJGPR8dKGaQYxoNfYFPkYzCuZk2BZ5uF0t6xSL-pXRuZU-sIE5Am3WCP81z8FKvuqeN9tkpKaTlrENK8EOzryoosVIrw_0WiePHUjZiv8I; _hp2_ses_props.1404198904=%7B%22ts%22%3A1656250162115%2C%22d%22%3A%22www.eventbrite.ca%22%2C%22h%22%3A%22%2Fd%2Fcanada--ontario%2Fmusic--events%2F%22%2C%22q%22%3A%22%3Fpage%3D1%22%7D; _ga_TQVES5V6SH=GS1.1.1656250163.2.0.1656250163.0; _ga=GA1.1.108199645.1656175950; __hstc=58577909.148da554ffa0d5a8e64fef78c845f442.1656175954948.1656175954948.1656250164395.2; __hssc=58577909.1.1656250164395
    Host: www.eventbrite.ca
    sec-ch-ua: ".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Windows"
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: cross-site
    Sec-Fetch-User: ?1
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"""
    headers = scraper_helper.get_dict(headers,strip_cookie=False)
    return headers


def json_cleaner(raw_js):
    raw_js = scraper_helper.cleanup(raw_js)
    a = raw_js.find('window.__SERVER_DATA__')
    raw_js = raw_js[a:].replace('window.__SERVER_DATA__ =','')
    b = raw_js.find('; window.__REACT_QUERY_STATE')
    raw_js = raw_js[:b]
    js = json.loads(raw_js)
    return js
sess = requests.Session()





if __name__ == '__main__':
    while True:
        old_id_file = open('old_ids.csv','a')
        old_ids = pd.read_csv('old_ids.csv',names=['id'])['id'].to_list()
        req = sess.get('https://www.eventbrite.ca/d/canada--ontario/music--events/?page=1',headers=get_headers())
        print(req.status_code)
        resp = Selector(text=req.text)
        raw_text = resp.xpath('//script[contains(text(),"window.__SERVER_DATA__")]/text()').get()
        js = json_cleaner(raw_text)
        main_data = []
        for row in js['search_data']['events']['results']:
            if row['id'] not in old_ids:
                data = {}
                data['name'] = row['name']
                data['timezone'] = row['timezone']
                data['id'] = row['id']
                data['start_date'] = row['start_date']
                data['start_time'] = row['start_time']
                data['end_date'] = row['end_date']
                data['end_time'] = row['end_time']
                data['summary'] = row['summary']
                data['end_time'] = row['end_time']
                data['city'] = row['primary_venue']['address']['city']
                data['country'] = row['primary_venue']['address']['country']
                data['region'] = row['primary_venue']['address']['region']
                data['localized_address_display'] = row['primary_venue']['address']['localized_address_display']
                data['postal_code'] = row['primary_venue']['address']['postal_code']
                data['street_address'] = row['primary_venue']['address']['address_1']
                data['latitude'] = row['primary_venue']['address']['latitude']
                data['longitude'] = row['primary_venue']['address']['longitude']
                data['images'] = row['image']['url']
                main_data.append(data)
                old_id_file.write(f'{row["id"]}\n')
        old_id_file.close()
        if len(main_data) > 0:
            pd.DataFrame(main_data).to_csv('eventbrite.csv',index=False,mode='a')
        print('sleep for 2 minutes')
        time.sleep(120)
        