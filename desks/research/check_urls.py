import re, urllib.request, urllib.error, ssl, socket

text = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
urls = re.findall(r'https?://[^\s\)<>\"]+', text)
seen = []
for u in urls:
    if u not in seen:
        seen.append(u)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

results = []
for u in seen:
    req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
    try:
        r = urllib.request.urlopen(req, timeout=15, context=ctx)
        status = r.status
        final = r.geturl()
        r.close()
        results.append((u, status, final))
    except urllib.error.HTTPError as e:
        # 403/404 etc. still means server responded
        results.append((u, e.code, e.geturl() if hasattr(e,'geturl') else u))
    except Exception as e:
        results.append((u, 'ERR:' + type(e).__name__, str(e)[:120]))

for u, s, final in results:
    print(f'{s}\t{final}\t{u}')
