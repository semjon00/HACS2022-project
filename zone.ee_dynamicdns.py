#!/usr/bin/python3
import time
import base64
import requests
import json
if __name__ == '__main__': pass

# TODO: ipv6 support

cfg = {}
try:
    cfg = json.loads(open('/home/admin/config.txt', 'r').read())
except:
    cfg['zoneid_username'] = input('ZoneID Username: ')
    cfg['zoneid_api_token'] = input('ZoneID API Token: ')
    cfg['domain'] = input('Domain Name: ')
    open('/home/admin/config.txt', 'w').write(json.dumps(cfg))

ipv4_old, ipv6_old, ipv4_new, ipv6_new = '', '', '', ''
while True:
    try:
        ipv4_new = requests.get('https://v4.ident.me').text
        ipv6_new = requests.get('https://v6.ident.me').text
    except Exception:
        pass
    if ipv4_old == ipv4_new and ipv6_old == ipv6_new:
        time.sleep(20.0)
        continue
    ipv4_old, ipv6_old = ipv4_new, ipv6_new

    session = requests.session()
    authstr = f"{cfg['zoneid_username']}:{cfg['zoneid_api_token']}"
    auth_header = f'Authorization: Basic {base64.b64encode(authstr.encode()).decode()}'
    session.headers = {'Authorization': f'Basic {base64.b64encode(authstr.encode()).decode()}'}
    url_base = f"https://api.zone.eu/v2/dns/{cfg['domain']}"

    records = json.loads(session.get(f"{url_base}/a").text)
    maybe_recordid = [x['id'] for x in records if x['name'] == cfg['domain']]
    if len(maybe_recordid) == 0:
        resp = session.post(f"{url_base}/a", data={
            "destination": ipv4_new,
            "name": cfg['domain']
        })
        print(resp.text)
    else:
        resp = session.put(f"{url_base}/a/{maybe_recordid[0]}", data={
            "destination": ipv4_new,
            "name": cfg['domain']
        })
        print(resp.text)
