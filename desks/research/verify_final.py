import re

t = open('/Users/martennormandin/thingztodo/desks/research/competitors.md').read()
print('=== COUNT CHECKS ===')
print('total chars:', len(t))
companies = ['Flinder','WhenCast','The Weather Channel','TripAdvisor','GuruWalk','SoulPlan','Spin the Jar','Kids Activities Blog','Mommy Poppins','Visit Detroit','Prague City Tourism','Eventbrite','Meetup','Facebook Events','Yelp','Groupon']
for c in companies:
    print(c, '->', t.count(c), 'mentions')
print()
print('=== REQUIRED SECTIONS ===')
for s in ['Who we beat and why','unverified / could not confirm','Ranked competitive map']:
    print(repr(s), '->', s in t)
print()
# Verify each ranked entry (1-15) has a URL on the same block
entries = re.split(r'### Rank (\d+) —', t)
print('entries found:', len([e for e in entries if e.strip()]))
for e in entries:
    m = re.match(r'  +(\d+) — .+', e.strip())
    if m:
        rank = m.group(1)
        has_url = 'http' in e
        print(f'Rank {rank}: has_http_url={has_url}')
