import re, urllib.request, ssl

t = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
raw = re.findall(r'https?://[^\s\)<>\"]+', t)
seen = []
for u in raw:
    core = u.rstrip(';.,:')
    if core not in seen:
        seen.append(core)

print('Unique URLs in final document:', len(seen))
bad = 0
for u in seen:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, method='HEAD', headers={'User-Agent':'Mozilla/5.0'}), timeout=12, context=ssl.create_default_context())
        st = r.status; r.close()
        tag = 'OK' if 200<=st<400 else 'FAIL'
        if st>=400 or st>=500: bad+=1
        print(f'{st}\t{u}')
    except Exception as e:
        st = 'ERR:'+type(e).__name__
        bad+=1
        print(f'{st}\t{u}  ({str(e)[:60]})')
print('Total failing (>=400):', bad)
