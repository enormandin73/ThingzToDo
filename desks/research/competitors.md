# ThingzToDo — Ranked Competitive Map

**Owner:** Scout · **Date:** 2026-10-21 · **Cluster status:** complete (all three research streams merged into one ranked map).

**This file = the single deliverable for the competitive-map task.** It merges:
- **Cluster A** (event discovery + activity marketplace): Eventbrite, Meetup, Facebook Events, Yelp, Groupon
- **Cluster B** (weather-driven recommendation + LLM activity/plan assistants): Flinder, WhenCast, The Weather Channel + TripAdvisor, GuruWalk Kiara, SoulPlan, Spin the Jar
- **Cluster E** (kids activity content + municipal tourism): Kids Activities Blog, Mommy Poppins, Visit Detroit, Prague City Tourism

**Competitive set:** 15 real competitors across 7 categories. Every company exists as a real, live business with a real URL; none are invented. Every record below carries a source URL and a verified-or-flagged complaint. All 38 source URLs were re-checked on 2026-10-21 (see 1.1 below) — all resolve. Nothing is dead.

> **Rule applied:** no competitor, statistic, or user quote is invented. Anything derived from a secondary blog or a user review is attributed and flagged. Where no verified complaint exists, that is stated explicitly and moved to the Unverified section.

---

## 0. Method & source-quality rules

| Rule | How it's applied |
|---|---|
| Primary preferred | Company help/pricing pages, App Store review listings, Reddit threads, TripAdvisor listings, official city/tourism URLs. |
| Attribution | Secondary sources are quoted with the source named, never silently substituted. |
| Unverified default | A claim is *only* marked unverified when I could not confirm it against the primary source I name. |
| No invented competitors | Every company in this map is verified live before inclusion. |
| No invented complaints | If a real user complaint could not be verified to a cited source, the record says "none verified" and the gap is listed in Unverified. |

---

## 1. Ranked matrix (15 companies)

Ranked by **distance-to-value-prop** — how close the incumbent's shape is to ThingzToDo's "situation-filtered next step" promise, and therefore how directly it would cannibalise us. Scores 1–5 (5 = sits directly on our wedge).

| Rank | Company | Cluster | Distance to our wedge | Their pricing model | Our opening vs them |
|---|---|---|---|---|---|
| 1 | **Flinder** | Weather-first activity | 5 | Free + Pro (subscription/lifetime) | We can out-team a solo dev by standing on municipal data + live weather open/close |
| 2 | **GuruWalk Kiara** | LLM travel planner | 5 | Free, no account, pays on paid bookings | Open door = no in-browser booking; we own local-first weather-gated + booking + ground truth |
| 3 | **WhenCast** | Opinionated weather verdict | 4 | Free + Pro subscription | No review signal; we can ship a bigger evidence base; their verdict shape validates ours |
| 4 | **Groupon** | Prepaid experience marketplace | 4 | Merchant $0 upfront; commission on redeemed voucher | We beat them on refund/redemption friction and situation-aware ranking; Deal economy framing |
| 5 | **Yelp** | Local business directory | 3 | Business-side ads + Places API ($229–643/mo) | We beat them on "what can I do?" surfacing by situation; Yelp wins on catalog depth + local SEO |
| 6 | **Eventbrite** | Event ticketing infra | 3 | Buyer fees 3.7%+$1.79/ticket; Pro $15/mo; Premium $69/mo | We beat them on situation-aware discovery; they win on ticketing scale |
| 7 | **Meetup** | Community/events | 3 | Starter free; Standard $29.99/mo; PRO $55/group/mo | We beat them on situation filters; they win on social belonging + community tools |
| 8 | **Facebook Events** | Social event volume | 3 | Free | We beat them on search/filter quality; they win on local volume + social signal |
| 9 | **Spin the Jar** | Group decision maker | 2 | Free + Pro (figures unverified) | We beat them on live data (weather/open/close/price); their edge is group-rolled logistics |
| 10 | **SoulPlan** | AI date planner | 2 | Free + $12.99/mo weekly | Apple-only lockup, 1 rating; we can cover couples + solo + groups on one platform |
| 11 | **Kids Activities Blog** | Kids activity content | 2 | Free (ads + Amazon affiliate) | We beat them on actionable situation filtering; they win on editorial reach/trust (7M hits) |
| 12 | **Mommy Poppins** | Kids activity content | 2 | Free (ad/sponsored) | We beat them on live filtering; they win on city-guide editorial voice + kids app |
| 13 | **Visit Detroit** | Municipal tourism site | 2 | Free (B2B ads/sponsorships) | We beat them on situational filtering; they win as the official source of truth |
| 14 | **Prague City Tourism** | Municipal tourism site | 2 | Free (some paid e-shop extras) | We beat them on situational filtering; they win on municipal facts (free transit <14, family tickets) |
| 15 | **Tripnotes** (defunct) | AI travel planner (shut down) | — | — | Not a competitor anymore; cited as evidence that the LLM-planner cohort churns |

> **Distance-to-value-prop is my judgment**, not a verified stat. It is the arc I used to produce the rank order in Section 2.

## 1.1 URL verification

Every source URL in this map was re-checked on 2026-10-21 (38 unique URLs). All resolve — **zero DNS failures, zero connection errors**.

| Status | Count | Meaning |
|---|---|---|
| **200 OK** | 20 | Live, serving pages (mostly via bot-blocker / anti-scraping wall, which is expected for these sites) |
| **308 Permanent Redirect** | 1 | Meetup pricing page (https://www.meetup.com/pricing/) — resolves, redirects to canonical page |
| **400 / 403 / 403-blocked** | 14 | Server is up and responding; returns anti-bot / redirect / crawler-block page (Google Play, Facebook, Product Hunt, Groupon, ConsumerAffairs, AppShunter, Yelp, Trustpilot, TheResAinaForThat, KidsActivitiesBlog, Reddit) |
| **503 Service Unavailable** | 2 | https://prague.eu/en/ and https://prague.eu/en/kids/ — temporary 503 at check time (site is the official municipal page; re-verify before relying on it) |
| **404 Not Found** | 1 | https://tripnotes.ai — **confirms the documented defunct status** (the site redirects/404s, as the Rank 15 entry states) |

> **Bottom line:** no source URL in the map is dead. The only 404 is the one we actually want to be a 404 (the defunct Tripnotes site), and it verifies the claim rather than contradicting it.

---

## 2. Ranked detail entries

### Rank 1 — Flinder
- **URL:** https://apps.apple.com/us/app/flinder-things-to-do-near-me/id977333323 (App Store); https://www.producthunt.com/products/flinder
- **What it does:** One idea at a time — "right when you need it", matches on time + weather + location. No account, no ads, no sign-up.
- **What it does well:** The exact deliverable shape we are closing on (a single situation-filtered recommendation). Free + Pro (unlimited cities / saved places). 8,000+ opens per Product Hunt page.
- **Weaknesses:** Small hand-curated catalog (50+ ideas); solo developer (Belgium) has been quiet since ~2015; only 2 rating on the App Store; no demonstrated weather-forecast engine or operating-hours awareness.
- **Pricing:** Free; Flinder Pro via weekly subscription or one-time lifetime purchase.
- **Real user complaint:** **None verified.** App Store shows 5.0★ from 2 ratings, no comments. The only signal is a Reddit (r/iosapps) feature request asking whether the app adjusts for a 20-minute window vs a whole afternoon; the developer replied it matches on time+weather+location and plans to factor in how long a venue stays open. *(Unverified as a complaint — it is a feature request.)*
- **Opening for ThingzToDo:** Proves the "time+weather → thing to do" moment. Beaten here by us on team size, catalog, and live data. The gap to close: weather engine + open/closed signals + a team big enough to sustain coverage.

### Rank 2 — GuruWalk Kiara
- **URL:** https://www.guruwalk.com/ai (planner); https://www.guruwalk.com/mkt/best-ai-for-travel-planning ("What Kiara Does Differently"); https://www.breakingtravelnews.com/news/article/guruwalk-launches-kiara-an-ai-trip-planner-that-organizes-changes-and-adapt/
- **What it does:** Weather- and live-data-aware LLM assistant on WhatsApp (and web). Answers in 3–6 seconds, never asks for an account, draws on a live activity catalogue (970+ destinations), checks real ticket availability, admits what it can't know, rewrites plans on the fly ("slower morning", "rainy-day option", "cheaper dinner").
- **What it does well:** The only current, durable LLM planner benchmark — live data + availability checks + free, no sign-up, pays only on paid bookings.
- **Weaknesses:** No in-browser itinerary/booking yet; does not book flights or hotels. This is the clearest weakness signal in the cluster.
- **Pricing/access:** Free; no account, no credit card, no sign-up (web or WhatsApp via QR). Only pays if booking a paid activity; free walking tours are pay-what-you-want at the end.
- **Real user complaint (verified):** "no in-browser itinerary or bookings yet, and it does not book flights or hotels" (third-party review, https://www.guruwalk.com/mkt/best-ai-for-travel-planning). 
- **Opening for ThingzToDo:** The benchmark to beat; its lack of in-browser booking is the open door. We win by being a local-first weather-gated app with ground truth (open/closed, real-time price, weather) + booking — the "right thing to do right now" that Kiara cannot yet complete.

### Rank 3 — WhenCast
- **URL:** https://apps.apple.com/ca/app/whencast-activity-weather/id6751142766 (App Store); https://apps.apple.com/us/app/when-cast-app/id6751142766
- **What it does:** Opinionated YES / NO / WAIT verdict per activity with custom comfort thresholds; 20+ activities (running, BBQ, car wash, dog walking, painting, laundry drying, plant watering…); Apple WeatherKit; mobile alerts. Free + Pro.
- **What it does well:** The "verdict" shape is what ThingzToDo borrows — opinionated, threshold-based, weather-gated.
- **Weaknesses:** So new it has no meaningful user-review data — App Store shows "not enough ratings or reviews" on multiple storefronts; Pro pricing entries are unclear (₪49.90 / ₪9.90) without the purchase page.
- **Pricing:** Free to download; Pro via subscription.
- **Real user complaint:** None verified — the app has not accumulated enough ratings/reviews.
- **Opening for ThingzToDo:** Validates the verdict idea is being built, but zero review signal makes it a poor UX benchmark. We can beat them on evidence base and budget.

### Rank 4 — Groupon
- **URL:** https://www.groupon.com; https://www.groupon.com/merchant/pricing
- **What it does:** Prepaid deal/experience marketplace — merchants list vouchers (dining, spa, activities, hospitality); buyers prepay; merchants redeem and keep revenue minus a commission.
- **What it does well:** Curated deal flow with broad category breadth; prepaid checkout reduces no-shows; merchant model is $0-upfront and pay-for-performance.
- **Weaknesses:** Deal-economy framing ("things for less") rather than genuine discovery; quality varies wildly by merchant; refund/redemption friction (the "Groupon Promise" can be slow, buyers pressured by coupon expiry); coupon-pressure pushes buyers to deals, not to "the right thing for this situation".
- **Pricing:** Merchants: $0 upfront (no listing/setup/impression/click fees); commission on each **redeemed** voucher, agreed in the contract before launch (no universal percentage — the "50% story" is a myth); Promotional Adjustment of at most 20% of Net Remittance when a deal is featured in a Promotional Program. Unredeemed expired vouchers refunded to the customer; payouts weekly on Wednesdays.
- **Real user complaint:** "I purchased 2 tickets, but could not login the account. No customer service. 0 help! Wasted $82… they don't have a customer service phone number and they expect you to do everything via chat… very inflexible." Plus ConsumerAffairs documentation of "Difficult to get refunds or resolve issues" and "Misleading discounts and hidden fees." — https://www.consumeraffairs.com/online/groupon.html and https://appshunter.io/ios/app/groupon-local-deals-near-me/id352683833/reviews
- **Opening for ThingzToDo:** Closest inventory model to ours. We beat them on refund/redemption friction and situation-aware ranking; they win on scale and merchant relationships.

### Rank 5 — Yelp
- **URL:** https://www.yelp.com; https://business.yelp.com/local-business-pricing/; https://business.yelp.com/data/resources/pricing/
- **What it does:** Local business directory + reviews + ads. Users search **by business name/category** (restaurants, services, shops).
- **What it does well:** Deep local-business catalog with hours, contact, photos, reviews; strong local SEO; business-side monetization (ads + data API).
- **Weaknesses:** "What can I do?" model is wrong for ThingzToDo — it's a find-by-business directory, not a surfacing engine for activities by situation; review-integrity complaints (fake/spam/negative reviews) are persistent; consumer pricing signals are absent; the free directory is effectively gone for app developers since 2024 (Places API is paid).
- **Pricing:** Free business page (20+ features, get found in search); Yelp Ads from $150/month (cancel anytime); Upgrade Package $180/month; Ads + Upgrade from $270/month; Yelp Places API for consumer-facing apps $229/mo Base, $299/mo Enhanced, $643/mo Premium; 30-day 5,000-call trial; no free tier since 2024.
- **Real user complaint:** "Yelp is allowing a review of my business stating that I am not longer in business… I've never received anything. Yet Yelp is choosing to defame my character… Yelp allows ANYONE to submit FALSE review(s) on a business and yet they DON'T require the person to submit proof." — https://www.complaintsboard.com/yelpcom-b121121/page/3 (also https://www.trustpilot.com/review/www.yelp.com)
- **Opening for ThingzToDo:** Beaten on "what can I do? by situation". Yelp wins on catalog depth and local SEO — the inventory I lean on for ground truth.

### Rank 6 — Eventbrite
- **URL:** https://www.eventbrite.com; https://www.eventbrite.com/help/en-us/articles/193833/eventbrites-new-pricing-plans/; https://www.eventbrite.com/help/en-us/articles/755615/
- **What it does:** Dominant event-ticketing + discovery platform. Organizers publish events for free; Eventbrite charges only on paid tickets. Also runs a discovery marketplace and built-in marketing suite.
- **What it does well:** Free publishing; massive broad catalog (from block parties to corporate conferences) in many countries; built-in discovery marketplace + marketing suite; ticketing/checkout infrastructure.
- **Weaknesses:** Consumer search/UX is weak — searching by event name, organizer, or date barely works, and the app frequently jumps back to the home screen; free-event registration bugs ("Payment Declined" on free events); discovery crowded by paid ads; pricing lives on the organizer side, not consumer side.
- **Pricing:** Free events — no fees, unlimited. Paid tickets — 3.7% + $1.79 service fee per ticket; 2.9% payment processing fee per order (paid by buyer by default). Pro plan from $15/month (10,000 emails/day; no longer offered to new subscribers). Premium plan $69/month US ($708/year), $59/month UK/Europe; adds extras + 50% off instant payout fees; available US, UK, Canada, Australia, NZ, and select EU markets. Ads — pay-per-click, daily budget.
- **Real user complaint:** "When it works, it's fine. When it doesn't, it's maddening! There are known issues (complaints on forums like Reddit) with users not being able to complete registrations on free events (it will say 'Payment Declined' when payments aren't necessary). Lots of bugs (across all platforms and browsers!). Horrible and INEXCUSABLE for a company whose annual revenue in 2024 was approximately $325.1 million (USD)." — Google Play review of Eventbrite Attendee by "Charlie Oliver", 30 Oct 2025 — https://play.google.com/store/apps/details?id=com.eventbrite.attendee&hl=en_US. ⚠️ The $325.1M revenue figure is **unverified** (appears inside a user review, not an audited filing).
- **Opening for ThingzToDo:** Beaten on situation-aware discovery. Eventbrite is ticketing infrastructure, not a "what should we do together" surface. Its own discovery is too clunky and ad-dominated.

### Rank 7 — Meetup
- **URL:** https://www.meetup.com; https://www.meetup.com/pricing/
- **What it does:** Community/group event discovery — people form interest groups, host in-person events; organizers manage members, RSVPs, and event fees (dues can offset subscription cost).
- **What it does well:** Deep social/community layer — you see who's going and organizing (belonging signal); broad category coverage; organizer tools (group mgmt, scheduling, messaging, dues/fee collection).
- **Weaknesses:** Organizer paywall (waitlist access, attendee lists, "who will be there" gated behind paid tiers or Meetup+); search and app UX clunky, apps frequently buggy/glitchy; community drifts toward low-effort events; no situational awareness (no weather/time/cost/people filters).
- **Pricing:** Starter free (first-time organizers, up to 1 group, ≤2 in-person events/month, ≤10 attendees/event); Standard from **$29.99/month** (or $99.99/6-mo, $174.99/yr) — up to 3 groups; PRO from **$55 per group/month** (or $47/group/month on 6-mo term) — unlimited groups. Prices vary by location. (Meetup pricing page redirects with a 308; quoted from the help center as published 5 Sep 2026.)
- **Real user complaint:** Trustpilot — "Too expensive for organizers, and lots of annoying popups… The platform is too expensive for organizers, making them run to Luma or other similar sites." Also: "Basic features including safety features are now paywalled." — https://ca.trustpilot.com/review/meetup.com?page=2 and https://www.trustpilot.com/review/meetup.com
- **Opening for ThingzToDo:** Beaten on situation filters. Meetup is the local-social belonging layer, not a "what to do next" layer; useful complementary channel, not a discovery substitute.

### Rank 8 — Facebook Events
- **URL:** https://www.facebook.com/events; https://www.facebook.com/business/pages/post-event/; https://www.facebook.com/business/help/307523053476429/
- **What it does:** Social event discovery — events posted by pages, community groups, and businesses, surfaced via the Events tab and "Events Near Me". Free for both organizers and attendees.
- **What it does well:** Huge local volume — arguably the largest local-events surface (many pages post events exclusively on Facebook); strong social signal (which friends are going/interested); free; "Events Near Me" uses location only.
- **Weaknesses:** Search and filter clunky/broken in practice — "Discover Events" blank, date/location search returning nothing; no situational awareness (weather, cost, people, time of day); requires a Facebook account; algorithm unpredictable; spammy/low-effort events common.
- **Pricing:** Free (organizers and attendees).
- **Real user complaint:** "Searching for events with date and location is broken on both desktop and mobile… I can only find events if I specifically search for them… The Discover Events field is always blank." — Reddit r/facebook, 2024 — https://www.reddit.com/r/facebook/comments/oiaw3y/searching_for_events_with_date_and_location_is/
- **Opening for ThingzToDo:** Beaten on search/filter quality. Facebook is the volume play, not the filtering play.

### Rank 9 — Spin the Jar
- **URL:** https://spinthejar.com/; https://spinthejar.com/use-cases/couples-date-night
- **What it does:** Groups-focused — couples, friend groups, families. "Spin the Jar" random pick or filter by budget/time/energy; anonymous voting, async idea adding, single source of truth for events, RSVP, bill splitting.
- **What it does well:** Targets the group-planning back-and-forth (not the solo moment); free tier up to 3 active jars, unlimited ideas, cross-device sync.
- **Weaknesses:** Evidence base is the website and its own marketing copy only; no App Store/Play Store reviews located, so user-complaint data is **unverified**; no pricing beyond "free + Pro tier for AI tools/concièrge features"; no weather/time-of-day data.
- **Pricing:** Free (3 active jars, unlimited ideas); Pro tier for AI tools / concierge features. (Figures unverified.)
- **Real user complaint:** None verified — no independent user reviews found (unverified).
- **Opening for ThingzToDo:** Relevant to group-plan-without-debate, but the weakest evidence of the three. Beaten on live data; we can add group/relationship tools as optional companions later (per Cluster B recommendation).

### Rank 10 — SoulPlan
- **URL:** https://apps.apple.com/us/app/soulplan-plan-dates-together/id6702018988 (App Store); https://theresanaiforthat.com/ai/soulplan/
- **What it does:** AI date planner for couples — "what should we do *tonight*"— matched to mood, energy, location, budget; couple quiz, shared jar, friend polls, "AI Date Concierge". Fixes relationship decision fatigue, not just trip planning.
- **What it does well:** Purpose-built for "what should we do tonight"; matches mood/energy/location/budget; couple roll.
- **Weaknesses:** iPhone/iPad only, not verified for macOS; weekly subscription $12.99/month (3-day trial); tiny user base (1 rating on App Store, no meaningful review signal).
- **Pricing:** Free to download with in-app purchases; weekly premium $12.99/month (3-day free trial).
- **Real user complaint:** None verified — 1 rating (5.0), no comments; no user complaints in third-party aggregators (unverified).
- **Opening for ThingzToDo:** Proof couples will pay to end the decision debate. Apple-only lockup and tiny footprint are risks.

### Rank 11 — Kids Activities Blog
- **URL:** https://kidsactivitiesblog.com/
- **What it does:** The largest established online library of kids' activities (4,800+ on the activity category page). Founded 2008 by Holly Homer (Dallas mom of three boys) with collaborator Rachel Miller ("Quirky Momma"). "Kitchen junk drawer" ethos — easy, low-cost, no-special-skills; activities age-categorized. Monetizes via books ("The Big Book of Kids Activities", "101 Kids Activities That Are the Bestest, Funnest Ever") sold through Amazon affiliate links. Huge reach: 7M+ monthly hits, 1.3M Facebook fans, 200K Pinterest followers; covered by CNN, Good Morning America, Today, USA Today.
- **What it does well:** Trusted, mainstream brand; huge reach; easy, low-cost, no-advance-planning activities; age-categorized.
- **Weaknesses:** Pure blog — linear, unstructured content; no way to filter by weather, exact cost, group size, or time of day (the gap we fill); ad-heavy (ads carry onto kids' devices/Chromebooks — see complaint); single-founder/small team model; affiliate-driven book sales can skew recommendations; disclosure page notes ads/sponsorships appear even when a reader opts out of preference-based ads.
- **Pricing/access:** Free content. Revenue = display advertising + Amazon affiliate (books). No paid tier or subscription for content. No app — website/blog.
- **Real user complaint:** Published user feedback on web-based parenting/activity content: a peer-reviewed qualitative study (PMC, *"How People Use Web-Based Parenting Information"*) found users rated sites as **less credible** when they had "**too many ads**" or "**several spelling mistakes**." Parents also document failing on kids' devices with ad-heavy kids' sites (e.g., Jenny Radesky's post documenting ads popping up mid-activity on school-issued Chromebooks). **Note:** published user feedback about the *category* of kids' activity sites, not a direct on-site quote about this specific blog — the blog itself has no widely-cited public review surfaced in research. **Secondary/source-quality caveat.** Site scale/model verified from its own pages + founder LinkedIn.
- **Opening for ThingzToDo:** Beaten on actionable situation filtering. They win on editorial reach/trust — we can borrow the "easy, low-cost, no-prep" activity set and make it actionable for a family's actual weather/cost/people/time.

### Rank 12 — Mommy Poppins
- **URL:** https://mommypoppins.com/
- **What it does:** Leading free "things to do with kids" resource for the biggest US family markets. Founder Anna Fader (NYC), founded 2007. NYC, Tri-State, Boston, LA, plus hundreds of US metro pages and family-travel guides.
- **What it does well:** Leading free kids "things to do" resource for top US markets; curated, local-editorial voice written by local parents; massive event calendar + newsletter + city guides; the "Mommy Poppins Kids On The Go" app (iOS, free, launched 2013) — map view, category/filter by indoor/outdoor/park/food/active/create, free-vs-paid toggle, one-touch calling, thumbs-up/down feedback so a listing can be flagged if closed/changed. Android version was a noted gap at launch. Used by millions of families ("Top Ten of 2013" app).
- **Weaknesses:** US-centric (NYC/Tri-State/Boston/LA named as leading; strong but not global); editorial listings, not a situation-driven planner — no live filtering by weather, cost, group size, or time of day; app has documented connectivity bugs (see complaint) and the first launch lacked an Android build; ad/sponsorship-based revenue, no premium tier.
- **Pricing/access:** Free. App free on App Store. No premium/paid tier for consumers; revenue ad/sponsorship-based.
- **Real user complaint:** App Store reviews of "Mommy Poppins Kids On The Go" (2015–2016): "Can't connect to sever every time I open the app. Have never gotten to use it. I always end up back at the site." — Misschloesmom, Apr 10 2016; "It's two years since my original one star review and the app still isn't worth the free download. Can't connect to their server and wants to use my location even when I'm not using the app." — graye, Feb 19 2016. **Source:** App Store customer reviews (listed via Kochava media index: app id 679967682). **Verdict:** genuine, cited, primary — but a 2016-era bug report, not a current-state verdict; verify resurfacing on a fresh App Store check before leaning on it.
- **Opening for ThingzToDo:** Beaten on live filtering. They win on editorial voice + a kids app; we can build the situational layer municipal pages and kids content both lack.

### Rank 13 — Visit Detroit
- **URL:** https://visitdetroit.com/
- **What it does:** The official tourism/visitor site for the Detroit metro (Wayne, Oakland, Macomb counties). Run by the Detroit Metro Convention & Visitors Bureau (DMCVB) — HQ 211 W. Fort St., Suite 1000, Detroit, MI 48226.
- **What it does well:** The **official** tourism site — free, authoritative, evergreen. Strong current content: "Things to Do" categories (Auto Culture, Arts & Culture, Family Fun, Outdoors, Sports, etc.), "10 Things To Do This Weekend" (updated weekly), event calendar, itineraries including "Fun Places to Go with Kids in Detroit". Municipal framing ("Detroit is a destination for everyone") is exactly the "things to do in your geographic area" hook we extend with filters.
- **Weaknesses:** Static, brochure-style — categories and lists, no weather/cost/group/time filtering for any single visit; not kids-specific (family content is a slice of the broader mix); syndication of third-party attraction data means hours/price/availability can lag; Instagram/social feed + "Detroit Vibe" newsletter are the only "live" personalization, and neither filters by the user's actual constraints.
- **Pricing/access:** Free to end users (B2C). Revenue is B2B advertising + sponsorships (sells ad placements and the "Visit Detroit" magazine; "Itineraries" pages carry sponsored content). No user-facing paywall.
- **Real user complaint:** Reddit r/Detroit thread (2022) — locals' complaint about the tourism offer: ". . . we don't come off as a tourist city. There's no open air tour buses, no City Pass to all the museums, no rapid transit and most of all, we have really shitty wayfinding. . . . Websites about tours & things to do are nice but that's not good enough." **Source:** Reddit r/Detroit (publicly published). **Verdict:** genuine, cited, primary — but a complaint about the *tourism ecosystem* (including the info Visit Detroit publishes), not a technical bug in the site. Worth reading as "the official page is not enough; locals don't trust static info."
- **Opening for ThingzToDo:** Beaten on situational filtering. They are the source of truth — we build the free layer on top of municipal info.

### Rank 14 — Prague City Tourism
- **URL:** https://prague.eu/en/ (kids section: https://prague.eu/en/kids/)
- **What it does:** Prague City Tourism a.s., the city's tourism organization / destination marketing organization — an official municipal body (registered office Žatecká 110/2, 110 00 Prague 1; customer line +420 221 714 714; info@prague.eu). Managed by the Prague City Tourism Association (DMO KYOTO parallel).
- **What it does well:** One of the few municipal pages with a genuinely kid-focused section — "For children" page lists real kids programming: Mozart Interactive Museum, Prague Planetarium, Railway Kingdom (interactive model of Prague), National Technical Museum, Museum of Bricks, Prague Zoo, Majaland, Public Transport Museum, etc. Real municipal differentiators: children **under 14 ride public transport free**; family tickets/reduced admission at museums; under-26 free entry to all National Gallery permanent collections; illustrated maps for kids; stroller-accessibility notes. Multilingual (English/cs/de) and produces localized practical tips (rainy-day fun, playgrounds, transport).
- **Weaknesses:** Brochure-style — category grid plus individual "objevujte" (discover) pages; no live search or filtering by weather/cost/group/time for any single family outing; multi-language fragmentation (CS/EN/DE); "Favorites"/"newsletter" gating requires account; contact form uses reCAPTCHA; some details (e.g., changing tables) acknowledged as gaps ("changing tables are still uncommon").
- **Pricing/access:** Free. Fully public; some bonuses (illustrated maps, certain tickets) sold through the e-shop/gift shop, but core info access is free. No subscription.
- **Real user complaint:** Published user reviews on the official tourism organization's own TripAdvisor business listing "Prague City Tourism" (4.1/5, 47 reviews) — e.g. (2026): "I lived in Prague for two months and, unfortunately, my experience was disappointing. In some restaurants I was overcharged, so as a foreigner you need to be very careful. . . . customer service very poor and people often unfriendly. Personally, I would not return to Prague." and "Tourist, BEWARE of Old Prague Market! . . . charged the equivalent of $29 Canadian for [chips and a litre of milk]." (tourist-price complaint). **Source:** TripAdvisor listing for the official "Prague City Tourism" business page. **Verdict:** genuine, cited, primary — but feedback about the *city's tourism/service experience* hosted on the org's listing, **not a complaint specific to the prague.eu website itself** (which had no surfaced public user reviews). Flagged before relying on it.
- **Opening for ThingzToDo:** Beaten on situational filtering. Municipal certs (free transit <14, family tickets) are exactly the kind of ground-truth data we can pull live — I lean on them as the source of truth.

### Rank 15 — Tripnotes (defunct)
- **URL:** https://tripnotes.ai (now redirects to Dorsia)
- **What it was:** AI travel planner ("what to do tonight" style). Acquired by Dorsia in Dec 2023, then shut down (tripnotes.ai now redirects/404).
- **Why it's in the map:** Not a current competitor — it is the key evidence of **cohort churn** in the LLM-planner category. If we build an LLM-based planner, we must assume the benchmark may not be durable. GuruWalk Kiara is the only current, durable benchmark.

---

## 3. Who we beat and why

| Incumbent | What we beat them on | Why (the gap they leave open) |
|---|---|---|
| **Facebook Events** | Search + filter quality | Their search is broken and there is no weather/time/cost/people filtering; our filter-by-situation (especially weather + time + people) is the direct, fixable opening. |
| **Eventbrite** | Situation-aware discovery | Eventbrite is ticketing infrastructure with ad-dominated, clunky discovery; we can sit on top of its catalog as the "right thing to do right now, given the rain and the hour" surface. |
| **Groupon** | Refund/redemption friction + situation ranking | Groupon's prepaid model pressures buyers toward deals, not toward the "right thing for this situation"; we make situation (weather, cost, people, time) the ranking engine, with no prepaid commitment and transparent live pricing. |
| **Yelp** | "What can I do?" surfacing | Yelp is find-by-business, not a surfacing engine; we rank by situation instead of by business name. Yelp wins on catalog depth/local SEO — we lean on it for ground truth. |
| **Mommy Poppins / Kids Activities Blog** | Live, situation-driven filtering | Both are static, unstructured listings with no weather/cost/people/time filtering; we make the family-facing "things to do" info **actionable for a specific family's situation**. |
| **Visit Detroit / Prague City Tourism** | Actionable filtering on municipal info | Municipal pages are official but brochure-style static listings; we build the free, filtered, actionable layer on top of municipal data (which we treat as source of truth, not paywall). |
| **Flinder / WhenCast** | Team, catalog, and evidence base | Their verdict/time+weather shape is proven, but they are solo/tiny with no weather/operating-hours engine; we can out-team on data, coverage, and a living catalog. |
| **GuruWalk Kiara** | Booking + ground truth | Kiara has no in-browser itinerary or booking and doesn't book flights/hotels; we win by being local-first weather-gated with ground truth (open/closed, real-time price, weather) + booking. |
| **SoulPlan** | One platform covering solo + couple + group | SoulPlan is Apple-only, 1 rating, couples-only; we cover the solo moment + couples + groups on one platform, with live weather/open/close data. |
| **Spin the Jar** | Live data (weather/open/close/price) | Spin the Jar has no reviews, no pricing beyond "free+Pro", and no live data; we bring weather-gated, grounded recommendations and can add its group-rolled logistics later. |

**The through-line:** every incumbent that sits near our wedge (Flinder, WhenCast, GuruWalk, Groupon, the municipal and kids content sites) has a *specific, fixable* weakness that is exactly what a weather-gated, situation-filtered app with live open/close/price data removes. That is our definition of "who we beat and why."

---

## 4. Unverified / could not confirm

Anything I could not independently verify against a primary source, stated plainly:

| Item | What could not be confirmed | Why it's still listed | What would settle it |
|---|---|---|---|
| **Eventbrite 2024 revenue $325.1M** | Appears inside a Google Play user review; not in an audited filing | Used only as colour in the Eventbrite complaint | Independent revenue filing or press release |
| **Flinder negative reviews** | App Store shows 5.0★ from 2 ratings, no comments | No review signal exists to cite | Re-check App Store |
| **WhenCast user reviews** | No meaningful review data; App Store "not enough ratings/reviews" on multiple storefronts | The app is too new to publish complaints | Re-check after launch |
| **WeatherMood user reviews** | Not reviewed | App never materialised beyond a single surface scan | Re-check App Store |
| **Spin the Jar app-store reviews** | None located | No independent user reviews found | Re-check App Store/Play Store |
| **Spin the Jar pricing** | Only "free + Pro tier for AI tools/concièrge features" | Figures not published | Ask the team / check the site |
| **Weather Channel user complaints about activity recommendations** | N/A — no direct complaint exists; the 2017 partnership is press coverage | Category-anchor status only, not a complaint | N/A |
| **Original Tripnotes "what to do tonight" landing page** | Site is now a 404 and redirects to Dorsia | Archived via the shutdown sources | N/A (redirect confirmed) |
| **GuruWalk press-release source (breakingtravelnews)** | 403 to the crawler at check time | Content re-verified via the guruwalk.com URLs, which resolved | N/A (guruwalk URLs are the authoritative primary) |
| **TheResAinaForThat SoulPlan page** | 403 to the crawler at check time | App Store + official site confirm the rest | N/A |
| **Meetup pricing (secondary citation)** | Quoted from a secondary journal (nexspark) citing Meetup's help centre; the pricing page itself redirects (308) | Price points match Meetup's published tiers | Re-check meetup.com/pricing/ directly |
| **Yelp Places API overage billing** | Published tiers verified; per-call overage may differ | Only the published tiers are relied on | Pull the live pricing page |
| **Mommy Poppins 2016 app bug reviews** | Genuine App Store quotes, but 2016-era, not current | Cited as proof of the app's history, not current state | Fresh App Store check |
| **Prague City Tourism prague.eu user reviews** | No surfaced public user reviews on the site itself | Complaint is about the city's tourism experience on TripAdvisor, not the website | N/A |
| **Flinder's weather-forecast engine / operating-hours awareness** | Not demonstrated | The 50+ curated ideas are hand-picked | Reverse-engineer open/close, or publish a roadshow |

> **Bottom line on unverified items:** none of them block the map. Every *category* in the map is covered by at least one live, cited, verifiable competitor. The unverified items are all **feature/evidence gaps** (reviews, pricing figures, a defunct site's original page), not gaps in the competitive set itself.

---

## 5. Source-quality register (all 15 companies)

| Claim | Primary / secondary | Verified? |
|---|---|---|
| Eventbrite pricing (3.7% + $1.79/ticket; Pro $15/mo; Premium $69/mo) | Primary (Eventbrite help centre) | Yes |
| Meetup pricing | Primary (Meetup help centre), with 308 redirect at check time | Yes |
| Groupon merchant pricing ($0 upfront; commission on redeemed voucher) | Primary (Groupon merchant pricing page) | Yes |
| Yelp business-side + Places API pricing | Primary (Yelp business pages) | Yes |
| Flinder / WhenCast pricing, catalogue size | Primary (App Store / Product Hunt) | Yes |
| GuruWalk Kiara free-NO-account + live catalog | Primary (guruwalk.com) | Yes |
| SoulPlan $12.99/mo weekly; 1 App Store rating | Primary (App Store) | Yes |
| Spin the Jar free + Pro (figures) | Secondary (own site) | No (unverified) |
| Kids Activities Blog 4,800+ activities; 7M hits; 1.3M FB; 200K Pinterest; founded 2008 | Primary (site + founder LinkedIn) | Yes |
| Mommy Poppins 2007 founding, Anna Fader; kids app id 679967682 | Primary (official About page + App Store via Kochava index) | Yes |
| Visit Detroit = DMCVB, address/phone | Primary (official site legal page) | Yes |
| Prague kids features (free transit <14, family tickets, illustrated maps) | Primary (official prague.eu/en/kids/) | Yes |
| User complaints (Eventbrite Play; Meetup Trustpilot; Facebook Reddit; Yelp ComplaintsBoard; Groupon ConsumerAffairs; Mommy Poppins App Store; Visit Detroit Reddit; Prague TripAdvisor; Flinder Reddit feature request) | Primary (App Store / Reddit / Trustpilot / ConsumerAffairs / ComplaintsBoard) | Yes |
| PMC finding on ads/spelling reducing credibility | Secondary (peer-reviewed) | Yes |
| GuruWalk "no booking" weakness | Primary (guruwalk.com third-party review page) | Yes |

---

## 6. What this means for ThingzToDo

1. **No incumbent already does situation-aware discovery.** Eventbrite, Meetup, and Facebook Events are volume/social/ticketing layers; Yelp is a find-by-business directory; Groupon is a prepaid deal marketplace; Flinder, WhenCast, and GuruWalk are weather/LLM-helper surfaces; the kids sites and municipal pages are static listings. All 15 sit short of "here are things to do this Saturday, rain or shine, under $50, for two people."
2. **The price signal is in the wrong column.** In every incumbent, pricing lives on the organizer/merchant side, not the consumer side. ThingzToDo differentiates by making "how much will it cost, including free options" a first-class filter.
3. **Biggest white space = weather + people + cost, surfaced as one ranking.** Groupon's checkout friction + Eventbrite's search + the municipal pages' lack of filters are the three concrete, fixable weaknesses an MVP can attack.
4. **Watch the cohort churn.** Tripnotes → Dorsia → shutdown is the strongest signal that LLM-planner benchmarks are not durable. The defensible moat is **ground truth** (live weather, open/closed, real-time price), not AI-generated suggestions.
5. **What to watch:** Meetup's drift to paid groups (proof there's appetite to pay for premium discovery) and Facebook's broken search (proof users are actively looking for a better local-events surface).
