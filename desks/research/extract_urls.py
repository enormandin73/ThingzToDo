import re, urllib.request, ssl, socket

text = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
urls = re.findall(r'https?://[^\s\)<>\"]+', text)
seen = []
for u in urls:
    if u not in seen:
        seen.append(u)

print(len(seen), 'unique URLs')
for i, u in enumerate(seen, 1):
    print(i, u)
