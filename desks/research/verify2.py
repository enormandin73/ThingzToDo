t = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
low = t.lower()
for s in ['who we beat and why','unverified / could not confirm','ranked competitive map','distance-to-value-prop','source-quality register','real user complaint','http']:
    print(repr(s), '->', s in low)
print()
import re
print('real user complaint headings:', t.count('Real user complaint'))
print('http hrefs:', len(re.findall(r'https?://', t)))
print('urls total:', len(re.findall(r'https?://[^\s\)<>\"]+', t)))
