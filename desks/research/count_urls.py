import re
t = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
raw = re.findall(r'https?://[^\s\)<>\"]+', t)
seen = []
for u in raw:
    core = u.rstrip(';.,:')
    if core not in seen: seen.append(core)
print('count:', len(seen))
punct_trail = [u for u in raw if u != u.rstrip(';.,:')]
print('trailing-punct artifacts:', len(punct_trail))
for u in punct_trail:
    print(repr(u))
