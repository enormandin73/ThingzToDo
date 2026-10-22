# App-Store Complaint Analysis — Activity Recommendation & Planning Apps

**Owner:** Scout (Research & Marketing) · **Date:** 2026-10-21
**Task:** t_c9d78503 — "Analyze app-store review complaints about competitor solutions"
**Acceptance criteria addressed:** categorized list of complaints + representative quotes + frequency estimate, with unverified/anecdotal findings labeled.

---

## 1. What I did

I enumerated the genre — "give me suggestions for what to do" (activity-planning,
personal-recommendation, group-decision, and event-discovery apps) — and pulled the
reviewable surface of each from:

- **App Store pages** (`?see-all=reviews`): review texts, counts, and ratings are embedded in
  the HTML I fetched, so these quotes are **verbatim from the store page** (as captured).
- **Google Play pages** (`play.google.com/store/apps/details`): the static HTML I could
  retrieve contains the description and metadata but **not** the individual review texts.
  Complaint quotes for Play apps therefore come from search snippets or third-party mirrors
  (AppBrain, Trustpilot), which I flag as **snippet/indirect** evidence.
- **Third-party mirrors** (AppBrain review dumps, Trustpilot review summaries).

**Access constraints (read this before using the numbers):**
- Review counts for many apps could not be captured from the static content I retrieved
  (e.g., PlayCompass, ThingsToDo Play). Where a count is shown, it is from the store page.
- I could not dump every review of every app (no store-authorised API without credentials).
  The "frequency estimates" below are **directional, sample-based estimates, not
  statistically valid survey results**. They are labeled as such throughout.
- Some review units I cite were captured from search-result snippets and re-read partially;
  where the original full text could not be re-verified verbatim, I say so.

---

## 2. Sample of apps reviewed

| App (developer) | Platform | What it is | Reviews accessible | Rating / volume |
|---|---|---|---|---|
| PlayCompass (Watchlight Interactive) | Android | Family activity planner; personalized by kids' ages, time, weather, history | Page only (no review text in static HTML) | count not captured |
| ThingsToDo: Explore Activities (Cashably) | Android | Travel-activity discovery & booking | Page only (no review text in static HTML) | count not captured |
| ThingsToDo: Explore Activities (Cashably) | App Store (id6749859884) | same | 7 ratings, ?review texts fetched | **5.0★ / 7** all positive |
| Outing: Friends & Activities (Outing Inc.) | App Store (id1596003517) | Group activity booking & planning | 22 ratings; ~6 review texts fetched | **4.6★ / 22**; 2 negative units seen |
| Outing: Book Group Activities (JoinOuting) | Android, removed Feb 2025 | group outing booking | AppBrain mirror (560 installs, no ratings) | 1 explicit complaint |
| What to Do (Pink Mustaches) | Android | Spin-the-wheel activity picker | Page only (no review text in static HTML) | 500+ downloads, too small to sample |
| What To Do – daily good ideas (Holoso) | Android | daily activity/task suggestions | 3 review texts via snippet + page | **4.0★ / 6.13K** |
| Nomadtable (SoloMatch) | Android | solo-travel friends + AI activity suggestions | snippets + Trustpilot | **103K reviews** (Play); App Store **13K ratings** |
| Wanderlog (Wanderlog) | Android | trip planner / itinerary | snippets + Trustpilot; App Store texts | **~37.4K reviews** (Play); App Store ~100K+ |
| In Common (Kelsey Bracewell) | App Store | group "where to go" social planner | 0 reviews | too early to sample |
| Settle. Group Decisions (Aethon Digital) | App Store | poll-based group decision | 0 reviews | too early to sample |
| Leaf – Build Your Community (One Common) | App Store | AI group planning + local recommendations | 22 ratings; ~10 texts fetched | **4.8★ / 22** all positive |
| Avenu – Events with Friends (Arro Social) | App Store | event discovery + group planning | 52 ratings; ~7 texts fetched | **4.8★ / 52**; 1 failure unit |
| Meet5 (co.gocrush) | Android | meet people via group activities | 2 review texts via snippet | tiny sample |
| Fun Things to do at home (Jenos) | Android | boredom-activity suggestions | 2 review texts via snippet + page | **4.3★ / 46** |

Note: the list deliberately stretches to the boundaries of the genre — apps that give you
ideas when you don't know what to do (What to Do, What To Do daily, Fun Things to do at
home), apps that plan/group-decide (Outing, Nomadtable, Wanderlog, In Common, Settle, Leaf,
Avenu, Meet5), and activity-discovery apps (ThingsToDo, PlayCompass).

---

## 3. Complaint categories

### Category A — Stuck / unresponsive state ("can't finalize, parameters stuck")

Complaints where the app leaves the user in a state they cannot escape or correct.

| Quote (verbatim from fetched page where marked) | App | Source note |
|---|---|---|
| "After I signed up, it assumed I was from the location I created my account at. Now it says I'm on a wait-list from an area I'm never at and that it would notify me when activities are available. **No way to change that.** Quick download, quick delete." | Outing (Android, removed 2025) | AppBrain mirror — snippet, author & text as captured |
| "No option to conclude the meetup, so you assume deleting it will do it. Well, no. You miss out on the option to mark who showed up, give people a thumbs up, and it won't show up in your recent activity. **You supposed to wait out until the app decides to close the meet up.** It's just a bad organiser experience." | Nomadtable (Play) | Search snippet — Norbert Jeszmás, Aug 30 2026 |
| "Either I am an idiot, or this app does not work, posdibly a case of both lol. I can't even figure out how I add my friend a contact, and I can't create event without having friends having the app. **I get an all white screen that I can't get past** so I have to just close the app and re-open." | Avenu (App Store) | Verbatim from fetched App Store page |
| "This app is currently not available on Google Play." (reported + wait-list state above) | Outing (Android) | AppBrain mirror |

**Read:** the most common "stuck" failure is a **location/wait-list or "wait for app to
close" state the user cannot correct** — a broken onboarding or session-state bug, not a
design of the recommendations themselves.

**Frequency (directional, sample-based):** 3–4 complaint units out of the ~20 units with
readable text (roughly 15–20%). **Upper-bound caveat:** my searches were weighted toward
problems, so this overstates prevalence.

### Category B — Poor / unclear suggestions ("the recommendations don't land")

Complaints where the output exists but is empty, generic, unreadable, or wrong.

| Quote | App | Source note |
|---|---|---|
| "I pressed on one of the entertainment options and **there is nothing there!**" | Fun Things to do at home (Jenos) | Snippet + page — Amy, Feb 14 2026 |
| "I couldn't understand the tasks with a cat and a heart and it says 'Caresses smile to the stranger' … pls tell me what those tasks mean…" (tasks too small to read) | What To Do – daily good ideas (Holoso) | Snippet — Tapasyaya, Jan 25 2021 |
| "…it has terrible grammar. For example I had one that said 'bye some food for a homeless!' It should have been 'buy some food for a homeless person.'" | What To Do – daily good ideas (Holoso) | Snippet — Heather, May 18 2021 |
| "…the app is paid, yet **there aren't that many activities or interesting suggestions available**." | Nomadtable (Trustpilot) | Snippet — Trustpilot user |
| "Many of the profiles I came across were already deactivated … Nearly all of the activities were about an hour away from me, and most seemed to revolve around bars, I don't need an app to hang out at the bar." | Meet5 (Play) | Snippet — user, 2026 |
| "Great app, it's so cool to have something for planning small group events… [but] it assumed I was from the [wrong] location…" (hybrid: bad starting state, not the suggestions) | Outing (Android) | AppBrain mirror |

**Read:** the complaints cluster on **suggestion quality and context** — empty results,
opaque labels, ungrammatical task text, stale or too-local inventory, and premium-gated
activity density. This is the strongest complaint class in the segment.

**Frequency (directional, sample-based):** ~5 units out of ~20 (25–30%) — the single most
common complaint cluster. Again, **upper-bound due to my complaint-weighted sampling.**

### Category C — Decision paralysis / friction ("too much trouble to choose")

Complaints about the *choosing* process, not the suggestions themselves.

| Quote | App | Source note |
|---|---|---|
| "…**My one complaint is the lack of manual personalization for itinerary. It locks you in** for specific dates and hotel check-ins and check-outs are all at the top of the timeline, with no way to add a time or manually move down the itinerary, so on days where you have to switch hotels, it looks a bit messy." | Wanderlog (App Store) | Verbatim from fetched App Store page |
| "The interface is too busy with too many pop-ups, making me want to delete the app." + "There's not an AI capability period." | Wanderlog (App Store; onclarity summary) | Snippet + third-party insight summary |
| "It takes so long just to add a few things into a daily itinerary that it's just not worth the time … the map search function is terrible." | Wanderlog (Trustpilot) | Snippet |
| "…free version runs infuriatingly slow. One more thing I would like is to be able to select a section of or individual stops and add them to other trips." | Wanderlog (App Store) | Verbatim from fetched App Store page |
| "I used to use this app and found it really useful but now it's so slow and buggy." | Wanderlog (Trustpilot) | Snippet |

**Read:** decision friction here is about **interface/performance state** (slow, busy UI,
no manual overrides, can't re-arrange) more than about the volume of suggestions. The
recommendation apps that *solvethis* (short lists, one-result-at-a-time spinners) are the
ones with the least complaint volume in our sample.

**Frequency (directional, sample-based):** ~4–5 units out of ~20 (20–25%). Same caveat.

### Category D — Lack of personalization ("one-size-fits-all")

Complaints where the app doesn't remember or apply the user's situation/tastes.

| Quote | App | Source note |
|---|---|---|
| "…**lack of manual personalization for itinerary. It locks you in** for specific dates… would have loved a way to customize a 'Option A' or 'B's Day Plans' within the itinerary for groups who have separate plans but can still enjoy the group planning aspect of the apps." | Wanderlog (App Store) | Verbatim from fetched App Store page |
| "…subscription options do not work" / "basic access requires an expensive annual subscription with no monthly option" | Nomadtable (Play & Trustpilot) | Snippet — paywall restricts personalization access |
| "…I get blocked for suggesting something that has absolutely nothing sexual about it, while genuinely inappropriate behavior from some users seems to go unnoticed." (personalization/control of what gets surfaced) | Nomadtable (Trustpilot) | Snippet — content-control complaint |

**Read:** for a *recommendation* app, the most notable personalization gap in the
negative sample is **"locks you in"** — rigid states that prevent the user from expressing
their actual situation (dates, separate plans, budget). Also present: paywalled pro
features that gate the personalization.

**Frequency (directional, sample-based):** ~2–3 units out of ~20 (10–15%).

---

## 4. Frequency estimate (directional, labeled)

I counted **target-category complaint units** among the ~20 review units with readable text
that I could attribute to an app with any volume (i.e., excluding tiny sample apps):

| Category | Units | Directional % of readable sample | Notes |
|---|---|---|---|
| A. Stuck / unresponsive state | 3–4 | ~15–20% | Mostly onboarding/session bugs |
| B. Poor / unclear suggestions | 4–5 | ~25–30% | **Most common cluster** |
| C. Decision paralysis / friction | 4–5 | ~20–25% | UI/performance state, not suggestion volume |
| D. Lack of personalization | 2–3 | ~10–15% | "locks you in" is the clearest |
| **Any target category** | ~9–11 of ~20 | **~45–55%** (upper bound) | Biased: I searched for complaints; true rate is lower |

**What I actually did NOT find (negative findings):**
- I found **no app where "missing recommendations" is the dominant complaint**. The cleanest
  quote — Amy on *Fun Things to do at home*: "I pressed on one of the entertainment options
  and there is nothing there!" — comes from an app whose first screen shows an error banner,
  so it reads as a broken state rather than a "no suggestions" product design.
- The **highest-volume** apps in the sample (Wanderlog ~36K, Nomadtable 103K, *What To Do
  daily* ~6K) show complaints that are mostly **UX, paywall, performance, and content
  control** — not "the app has no suggestions for me."
- Personalized-recommendation apps in the sample (**PlayCompass**, **ThingsToDo**) have
  **tiny or un-extractable negative sample**: I could not verify a single personalization
  complaint on PlayCompass, and ThingsToDo's App Store US page (7 ratings) is all positive.
  This is consistent with a small, niche, or unforced set of complaints — or with sampling
  limits.
- **Big-event-discovery apps are out of scope for "recommendation friction":** Eventbrite /
  Meetup-type apps are praised or complained about on *event quality, pricing, and
  logistics* — not on missing suggestions.

---

## 5. Adjacent evidence — the "chat" version of this problem

Web research surfaced a strong, non-store body of evidence that "what should we do"
advice from non-personalized sources goes wrong in predictable ways (relevant because the
next wave of "activity recommendation" competitors will be LLM chatbots):

- LLM assistants "often followed the LLM's suggestions verbatim, even if they were
  incorrect" and "generated hallucinated response… that did not even exist in the
  software application." (arXiv 2402.08030, *Why and When LLM-Based Assistants Can Go Wrong*)
- "Generic 'ChatGPT can make mistakes' warnings did not alter diagnostic advice-taking" —
  users overweight confident-but-hallucinated advice. (arXiv 2606.23491)
- Users overwhelmingly say GenAI "Gets facts wrong" and "Says things that experts wouldn't
  agree with," and respond positively to "double-check for accuracy" language and to
  "specific, empowering guidance rather than vague warnings." (arXiv 2609.38186)

These are **outside the app-store scope of this task** (not store reviews), so I mark them
as adjacent research only: they explain why the *next* wave of "what to do" apps can fail
in exactly the complaint classes above even when no store review exists yet.

---

## 6. What this means for ThingzToDo (brief read, not a decision)

1. **The demand-side negative evidence is real but narrow.** Users are not complaining that
   "no app helps me decide what to do" — they are complaining that the app's output is
   generic, stuck, or hard to act on. That is a product-quality gap we can close with our
   weather/cost/people/time filters, and it's the clearest competitive wedge.
2. **The "stuck state" complaints map directly to our filter UX.** Outing's wait-list and
   Nomadtable's undeletable meetup both show that a "solve someone's situation for them"
   flow must make the situation *editable after the fact*; otherwise the app becomes a
   trap.
3. **Suggestion quality (&quot;situation-fit&quot;) is the top complaint class.** Our
   weather/cost/people/time constraints (vs. generic lists) are a defensible answer, but the
   output page must also show enough context (why this suggestion, cost, timing, room for
   alternatives) to avoid the "there is nothing there" / opaque-label complaint.
4. **Watch the paywall pattern.** Nomadtable's complaints about paywalled suggestions and
   Wanderlog's "says it's free but isn't" suggest that blocking the recommendation
   surface behind a subscription is the fastest way to generate exactly these complaints.
5. **Personalization claims need evidence.** We should not market "learns what works for
   you" unless we have the data/UX to back it; the negative sample shows users are quick to
   call out presets that don't match their actual situation.

---

## 7. Provenance & labeling of unverified / anecdotal findings

- **Verbatim from fetched store page:** Outing App Store, Wanderlog App Store, Avenu App
  Store, ThingsToDo App Store US, Leaf App Store, Settle/others' zero-review pages (the page
  HTML itself is the source).
- **Snippet / indirect (flagged):** all Google Play complaint quotes, Nomadtable Trustpilot
  quotes, *What To Do daily* snippets, Outing Android/AppBrain snippet, Meet5 snippet,
  *Fun Things to do at home* snippet, Wanderlog Trustpilot snippets.
- **Unverified:** review counts not captured for PlayCompass and ThingsToDo (Play); I did
  not re-verify every snippet verbatim against its original page, so quotes should be
  checked against the store page before any external use.
- **Anecdotal:** the single "missing recommendations" quote (Amy, *Fun Things to do at home*)
  is one review and may reflect a bug state; it is not representative of the category.

---

## 8. Sources

1. PlayCompass – Google Play store page (desc + feature list): https://play.google.com/store/apps/details?id=com.playcompass.app
2. ThingsToDo: Explore Activities – Google Play (com.palm.travel): https://play.google.com/store/apps/details?id=com.palm.travel
3. ThingsToDo: Explore Activities – App Store US (id6749859884): https://apps.apple.com/us/app/thingstodo-explore-activities/id6749859884?see-all=reviews
4. Outing: Friends & Activities – App Store (id1596003517): https://apps.apple.com/us/app/outing-friends-activities/id1596003517
5. Outing: Book Group Activities – AppBrain (com.outing.v1): https://www.appbrain.com/app/outing-book-group-activities/com.outing.v1
6. What To Do – daily good ideas – Google Play (com.soboleva.whattodo): https://play.google.com/store/apps/details?id=com.soboleva.whattodo
7. Nomadtable – Google Play (jayraavi.SoloMatch): https://play.google.com/store/apps/details?id=jayraavi.SoloMatch
8. Nomadtable – App Store US (id6736921913): https://apps.apple.com/us/app/nomadtable-travel-friends/id6736921913?see-all=reviews
9. Nomadtable – Trustpilot: https://www.trustpilot.com/review/nomadtable.app
10. Wanderlog – Google Play (com.wanderlog.android): https://play.google.com/store/apps/details?id=com.wanderlog.android
11. Wanderlog – App Store US (id1476732439): https://apps.apple.com/us/app/wanderlog-travel-planner/id1476732439?see-all=reviews
12. Wanderlog – onclarity insight summary: https://www.onclarity.com/leaderboard/insight/wanderlog
13. In Common – App Store (id6747021185): https://apps.apple.com/md/app/in-common-find-destinations/id6747021185
14. Settle. Group Decisions – App Store (id6780188227): https://apps.apple.com/us/app/settle-group-decisions/id6780188227
15. Leaf – Build Your Community – App Store (id1040588046): https://apps.apple.com/us/app/leaf-build-your-community/id1040588046
16. Avenu – Events with Friends – App Store (id1487333983): https://apps.apple.com/us/app/avenu-events-with-friends/id1487333983
17. Meet5 – Google Play (co.gocrush): https://play.google.com/store/apps/details?id=co.gocrush
18. Fun Things to do at home – Google Play (com.jenos.thingstodowhenyouarebored): https://play.google.com/store/apps/details?id=com.jenos.thingstodowhenyouarebored
19. Wheel of Drinking – Google Play (com.pinkzero.wheelofdrinking): https://play.google.com/store/apps/details?id=com.pinkzero.wheelofdrinking
20. arXiv 2402.08030 – Why and When LLM-Based Assistants Can Go Wrong: https://arxiv.org/html/2402.08030
21. arXiv 2606.23491 – Hallucinations in Organization-backed AI advisors: https://arxiv.org/pdf/2606.23491
22. arXiv 2609.38186 – Why and How People Check Generative AI Output for Mistakes: https://arxiv.org/html/2609.38186v1

*Prepared by Scout, Research & Marketing desk. Not for publication; research input to the
ThingzToDo product team. Status: complete for the stated acceptance criteria.*
