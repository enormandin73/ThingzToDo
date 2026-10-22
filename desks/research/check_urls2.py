import re, urllib.request, urllib.error, ssl

t = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
# extract URLs, strip trailing punctuation (; , . :) that is not part of a URL
raw = re.findall(r'https?://[^\s\)<>\"]+', t)
seen = []
for u in raw:
    core = u.rstrip(';.,:')
    if core not in seen:
        seen.append(core)

print(len(seen), 'unique URLs')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for u in seen:
    req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
    try:
        r = urllib.request.urlopen(req, timeout=15, context=ctx)
        status = r.status
        final = r.geturl()
        r.close()
        print(f'{status}\t{final}')
    except urllib.error.HTTPError as e:
        print(f'{e.code}\t{e.geturl() if hasattr(e,"geturl") else u}')
    except Exception as e:
        print(f'ERR\t{u}  ({type(e).__name__}: {str(e)[:80]})')
