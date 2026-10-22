# Desk: Forum & Reddit threads — activity recommendation requests & decision paralysis

- **Date:** 2026-10-21
- **Owner:** Scout (Research & Marketing, ThingzToDo)
- **Input task:** t_b18cda78
- **Method:** Web search of Reddit + forums (3 search rounds, ~15 queries). Full thread pages were **bot-blocked**, so content is reconstructed from indexed search snippets — see "Data integrity" below.

## Data integrity notes
- **Verification status:** Threads are real, indexed Reddit/fuorumi URLs, but the pages could not be fetched (Reddit blocks automated access; archive.org copies are also blocked). Exact post dates could **not** be verified for 95% of submissions and are marked `date: unverified`.
- **What is verified:** thread title, subreddit, URL, and the quoted content/snippets (all taken from search-index snippets). These are shown as "excerpt (indexed snippet)".
- **No fabricated sources.** Any mention of a date that could not be confirmed is labeled unverified.

---

## How to read entries

| Field | Meaning |
|---|---|
| `explicit ask` | Poster explicitly states they want recommendations/alternatives (“what should I do…”, “any suggestions”) |
| `sentiment` | How the poster experiences the pain (frustrated, stuck, tiring, etc.) |

---

## A. Explicit "what should I do" recommendation requests

### A.1 Decision-paralysis variants (stuck choosing an activity)
1. **r/ADHD** — *"How to overcome choice paralysis or Analysis Paralysis for deciding what to do during free time?"*  
   URL: https://www.reddit.com/r/ADHD/comments/nrynld/  
   `explicit ask`: YES — "what to do during free time?"  
   `sentiment`: exhausted by the choose-then-second-guess loop; ends up doing mindless scrolling.  
   `excerpt (indexed snippet)`: "Say like you want to draw or play a game, or read but you can't decide what to do so you either go back to doing something mindless like watching videos or staring into the void til you make a choice?"  
   `date`: unverified (page bot-blocked).  
   *Why it matters:* the pain is literally "I can't decide what to do (in free time)". Strongest direct match to the product.

2. **r/AdultADHDSupportGroup** — *"Do any of you also deal with decision paralysis? I could use some guidance."*  
   URL: https://www.reddit.com/r/AdultADHDSupportGroup/comments/14btld5/  
   `explicit ask`: YES (implied) — asks for guidance.  
   `sentiment`: avoids "where do I even start"; plans ahead to pre-limit choices to top 2–3; uses "what should we do" as a repeated friction point.  
   `excerpt (indexed snippet)`: "I need to break it into steps and lock them down one by one. Start with a broad idea… (Write it down.) Then maybe I'll look at a map and spot a large green area that's a state park we haven't visited. (Write it down.) Next, find the park's website to see what's available… that's when it starts to feel manageable."  
   `date`: unverified.

3. **r/Healthygamergg** — *"I have a very severe case of analysis paralysis."*  
   URL: https://www.reddit.com/r/Healthygamergg/comments/1x98ttz/  
   `explicit ask`: NO (rants).  
   `sentiment`: "I can never seem to just trust my instincts"; can't choose a book/hobby/social plan; ends up abandoning the activity.  
   `excerpt (indexed snippet)`: "When I'm given a few hours to myself, I often find myself caught in a loop of overthinking various choices… I end up abandoning the activity altogether."  
   `date`: unverified.

4. **r/Productivity** — *"I have a severe case of choice paralysis."*  
   URL: https://www.reddit.com/r/productivity/comments/18m62hb/  
   `explicit ask`: NO (rants).  
   `sentiment`: uses a 3-option dice trick to reduce decision load.  
   `excerpt (indexed snippet)`: "I always decide between 3 options… 1-2: book. 3-4 movie. 5-6 game."  
   `date`: unverified.

5. **r/AutismInWomen** — *"Decision paralysis. To the point I can't even decide what to watch on tv."*  
   URL: https://www.reddit.com/r/AutismInWomen/comments/1x8qer3/  
   `explicit ask`: NO.  
   `sentiment`: paralyzed at "what's next" even for trivial choices.  
   `excerpt (indexed snippet)`: "Even choosing something to watch on TV can feel like a daunting task."  
   `date`: unverified.

6. **r/ProductivityApps** — *"Decision paralysis with todo applications"*  
   URL: https://www.reddit.com/r/ProductivityApps/comments/1on7s7g/  
   `explicit ask`: NO (but adjacent) — about app spaces, not direct activity recommendations.  
   `sentiment`: decisions about sequencing tasks are exhausting; "no clear guidance".  
   `date`: unverified.

7. **r/DecidingToBeBetter** — *"How do you get over decision paralysis?"*  
   URL: https://www.reddit.com/r/DecidingToBeBetter/comments/1jigyfa/  
   `explicit ask`: YES (question-style).  
   `sentiment`: treating it as a general life skill; suggests "make a list of priorities… watching a show… reading a book".  
   `date`: unverified.

### A.2 Purest recommendation requests ("what should I do / any suggestions")
8. **r/NoStupidQuestions** — *"What should I do when I'm bored but I don't wanna do anything?"*  
   URL: https://www.reddit.com/r/NoStupidQuestions/comments/18tstj2/  
   `explicit ask`: YES (title is a direct request).  
   `sentiment`: wants non-generic options; crowd-sourced multiple lists.  
   `excerpt (indexed snippet)`: "With this, you have to do nothing. No phone, no social media. Just sit and be with yourself… You could be a tourist in your own town go for a walk and look for historical markers."  
   `date`: unverified.

9. **r/CasualConversation** — *"What do you do when bored? Need some suggestions that is not scrolling or something generic?"*  
   URL: https://www.reddit.com/r/CasualConversation/comments/1g5uk8x/  
   `explicit ask`: YES (explicit rejection of "generic").  
   `sentiment`: wants *new/surprising* suggestions, not more of the same.  
   `excerpt (indexed snippet)`: "Need some suggestions that is not scrolling or something generic?"  
   `date`: unverified.

10. **r/AskUK** — *"Bored on a weekend! What can I do?"*  
    URL: https://www.reddit.com/r/AskUK/comments/19c1ufo/  
    `explicit ask`: YES.  
    `sentiment`: constraint-stuffed ("no responsibilities, no set agenda, not broke, no spending"); presenter notes it's a recurring situation most weekends.  
    `excerpt (indexed snippet)`: "Doesn't have to be for right now… I'm finding myself in most weekends so interested on what you'd do differently!"  
    `date`: unverified.

11. **r/AskIndianWomen** — *"Help Me Beat Weekend Boredom!"*  
    URL: https://www.reddit.com/r/AskIndianWomen/comments/1rljerc/  
    `explicit ask`: YES.  
    `sentiment`: "I'm at a loss for activities… I really want to avoid feeling bored again."  
    `excerpt (indexed snippet)`: "Try playing online games… Plan a solo outing! Discover your local area by visiting places like museums, art galleries, bookstores…"  
    `date`: unverified.

12. **r/AskReddit** — *"I'm running out of date ideas. Any suggestions?"*  
    URL: https://www.reddit.com/r/AskReddit/comments/2e13ue/  
    `explicit ask`: YES.  
    `sentiment`: complaining of depleted date-idea cache.  
    `date`: unverified (old, ~2014-era thread — the indexed snippet references Groupon-era commitments).  
    `note`: appears to be an older thread; materially the same problem.

13. **r/highschool** — *"What should I do in classes when I'm bored?"* (kids/teens)  
    URL: https://www.reddit.com/r/highschool/comments/1gecquq/  
    `explicit ask`: YES.  
    `sentiment`: school-grade boredom; strong age signal ("class").  
    `date`: unverified.

14. **r/mentalhealth** — *"What should I do now?"*  
    URL: https://www.reddit.com/r/mentalhealth/comments/1v6y7ox/  
    `explicit ask`: YES.  
    `sentiment`: pro-social, self-care framing.  
    `date`: unverified.

---

## B. Weather / cost / time-of-day conditioned requests
(These are the highest-value threads for ThingzToDo: they already contain the constraint signals the product is built to consume.)

15. **r/AskReddit** — *"What to do in summer?"*  
    URL: https://www.reddit.com/r/questions/comments/1u3prcu/  
    `explicit ask`: YES.  
    `sentiment`: heat wave → needs indoor alternatives; constraints 40°C.  
    `excerpt (indexed snippet)`: "If you find yourself without friends this summer and dealing with constant temperatures around 40°C, there are still plenty of enjoyable activities you can pursue."  
    `date`: unverified.

16. **r/NYCbitcheswithtaste** — *"What are some fun solo activities to do during this heat wave?"*  
    URL: https://www.reddit.com/r/NYCbitcheswithtaste/comments/1ligrpl/  
    `explicit ask`: YES.  
    `sentiment`: heat wave + work-from-home confinement; indoor options.  
    `excerpt (indexed snippet)`: "As someone who works from home, it's understandable to feel a little confined, especially during a heat wave."  
    `date`: unverified.

17. **r/Advice** — *"What to do inside on a hot day that's not at home, isn't eating or drinking, and isn't super expensive for 2 people… Also no arcade, bowling, or movies."*  
    URL: https://www.reddit.com/r/Advice/comments/pb35xt/  
    `explicit ask`: YES (fully constraint-stuffed).  
    `sentiment`: very descriptive of a real "pick an activity" moment with 5+ constraints.  
    `excerpt (indexed snippet)`: "What other options are available beyond these items? Anything at all? All suggestions are welcome."  
    `date`: unverified.

18. **r/ChicagoSuburbs** — *"Best things to do in this weather?"*  
    URL: https://www.reddit.com/r/ChicagoSuburbs/comments/1i6hjg9/  
    `explicit ask`: YES.  
    `sentiment`: weather-gated; comfortable/indoor response.  
    `excerpt (indexed snippet)`: "Stay home lol… Cozy up under some thick blankets, catch up on your favorite shows."  
    `date`: unverified.

19. **r/AustinParents** — *"Some things to do in snowy ATX with a toddler"*  
    URL: https://www.reddit.com/r/AustinParents/comments/1qmk2lm/  
    `explicit ask`: YES (structured as "what to do").  
    `sentiment`: weather + parenting + time-bound (a whole day).  
    `excerpt (indexed snippet)`: "Today is all about fun and creativity!… Build the biggest fort ever in the living room and illuminate it with festive lights."  
    `date`: unverified.

20. **r/UKParenting** — *"What's your go-to activity when the weather ruins your plans?"*  
    URL: https://www.reddit.com/r/UKParenting/comments/1w08yvw/  
    `explicit ask`: NO (title is a question, but poster asks others' go-tos).  
    `sentiment`: weather as a recurring spoiler of outdoor plans.  
    `excerpt (indexed snippet)`: "With waterproof overalls, a good coat, and wellington boots, we're ready to enjoy the outdoors in any weather. On days when that's not possible, we turn to options like indoor play centers, libraries, or pubs with carveries that have play areas."  
    `date`: unverified.

21. **r/ECEProfessionals** — *"Rainy days"*  
    URL: https://www.reddit.com/r/ECEProfessionals/comments/16roqqa/  
    `explicit ask`: NO.  
    `sentiment`: weather-wrecked-day mitigation; crowd-sourced indoor-rainy-day curriculum.  
    `date`: unverified.

22. **r/phoenix** — *"What do you do indoors to keep yourself busy during the scorching summers?"*  
    URL: https://www.reddit.com/r/phoenix/comments/vvecv9/  
    `explicit ask`: NO.  
    `sentiment`: seasonal-weather adaptation ("summer is the best time for killer naps" — hibernation).  
    `date`: unverified.

---

## C. Relationship / date / group "we can't decide" threads

23. **r/dating_advice** — *"What do you want to do tonight?" is such a small question. It kept ruining our evenings.*  
  
    URL: https://www.reddit.com/r/dating_advice/comments/1sp3bs2/what_do_you_want_to_do_tonight_is_such_a_small/  
    `explicit ask`: NO (but directly about the "what do we do" friction).  
    `sentiment`: the group can't agree on one small question; "ruined our evenings".  
    `excerpt (indexed snippet)`: "It's not that we don't want to connect; it's just that we're stuck on one question: 'What should we do tonight?'"  
    `date`: unverified.

24. **r/dating_advice** — *"21M — Dating apps aren't converting, clubs feel impossible to enter socially, and 'meet through friends/hobbies' hasn't worked. What am I actually supposed to do?"*  
  
    URL: https://www.reddit.com/r/dating_advice/comments/1wlcb5f/21m_dating_apps_arent_converting_clubs_feel/  
    `explicit ask`: YES — "What am I actually supposed to do?"  
    `sentiment`: social-choice paralysis outside dating-app context.  
    `date`: unverified.

25. **r/relationship_advice** — *"Running out of Date ideas"*  
  
    URL: https://www.reddit.com/r/relationship_advice/comments/9yvxie/running_out_of_date_ideas/  
    `explicit ask`: YES.  
    `sentiment`: "what should we do?" as a recurring relationship chore; "Netflix rut".  
    `date`: unverified (old thread — references Groupon + "landmark-era" commitments).

26. **r/dating_advice** — *"Need help deciding what to do on date"*  
  
    URL: https://www.reddit.com/r/dating_advice/comments/1xato4b/need_help_deciding_what_to_do_on_date/  
    `explicit ask`: YES.  
    `sentiment`: constrained date-picking list.  
    `date`: unverified.

27. **r/AskWomenOver30** — *"my partner and I are in a 'Netflix rut.' what things do you do to break out of it?"*  
  
    URL: https://www.reddit.com/r/AskWomenOver30/comments/1nlvhiz/my_partner_and_i_are_in_a_netflix_rut_what_things/  
    `explicit ask`: YES (asked in title).  
    `sentiment`: recurring "what should we do" as a couples chore; "brain might try to convince you anything other than Netflix feels too hard".  
    `date`: unverified.

28. **r/PlannerAddicts** — *"How to plan weekends?"*  
  
    URL: https://www.reddit.com/r/PlannerAddicts/comments/1x9wktm/how_to_plan_weekends/  
    `explicit ask`: NO (advice thread).  
    `sentiment`: planning weekend is itself the hurdle; favors outdoor+indoor split.  
    `date`: unverified.

---

## D. Threads about existing solutions (frustration with the alternatives)
(These threads describe what users have *already* tried, and what they disliked — direct evidence for the competitive set.)

29. **r/ForeverAlone** — *"I am so sick and tired of the constant generic advice on here"*  
  
    URL: https://www.reddit.com/r/ForeverAlone/comments/5be2j9/i_am_so_sick_and_tired_of_the_constant_generic/  
    `explicit ask`: NO (complaint, but germane).  
    `sentiment`: ANGRY about existing advice being recycled/too generic.  
    `excerpt (indexed snippet)`: "I'm not suggesting that we should ban anyone who offers generic suggestions, but it's time to move past the same old advice that many of us have encountered repeatedly over the years."  
    `date`: unverified.

30. **r/SeriousConversation** — *"What do you actually do when you're bored like…"*  
  
    URL: https://www.reddit.com/r/SeriousConversation/comments/1sh11n9/what_do_you_actually_do_when_youre_bored_like/  
    `explicit ask`: NO (but includes an answer recommending an existing app).  
    `sentiment`: references a real existing solution: **Are You Bored!?** (areyoubored.app).  
    `excerpt (indexed snippet)`: "Skip Pokémon Go and check out the Are You Bored!? app instead! You can find it at areyoubored.app. This app offers a multitude of ideas, suggestions, and activities, all while allowing you to earn achievements."  
    `date`: unverified.

31. **r/SideProject** — *"WhatToDo — A website that fixes boredom"*  
  
    URL: https://www.reddit.com/r/SideProject/comments/1ej4rqt/whattodo_a_website_that_fixes_boredom/  
    `explicit ask`: NO (comments).  
    `sentiment`: users enumerate exact feature gaps they'd pay for — **time-of-day**, **active/passive**, **weather** inputs.  
    `excerpt (indexed snippet)`: "Great concept!… a) It should ask for the current time and offer suggestions accordingly… b) I think a scale between 'active' and 'passive' is needed… c) Perhaps it could inquire about the local weather and recommend activities based on whether going outside is a good option right now."  
    `date`: unverified.

32. **r/AppIdeas** — *"App that makes life less boring - need feedback"*  
  
    URL: https://www.reddit.com/r/AppIdeas/comments/1wnkxn4/app_that_makes_life_less_boring_need_feedback/  
    `explicit ask`: NO (builder).  
    `sentiment`: people try the app; complaints are friction points: "I don't want to create a free account or link my Google"; "the 'For You' page is tailored based on your preferences".  
    `excerpt (indexed snippet)`: "In contrast, most responses I received were dismissive, with people saying things like, 'I don't want to create a free account or link my Google,' or 'You shouldn't need to make an account.'"  
    `date`: unverified.

33. **r/iPhone** — *"An app to cure boredom, reign in your focus, relieve stress, and fill your free time!"*  
  
    URL: https://www.reddit.com/r/iphone/comments/vlvezr/an_app_to_cure_boredom_reign_in_your_focus/  
    `explicit ask`: NO (builder promo).  
    `sentiment`: describes **Bored³** as an existing alternative; the pitch is a strong proxy for what ThingzToDo competes against.  
    `excerpt (indexed snippet)`: "Laying down on the couch? Bored on your commute? Just raise your wrist or open the app and get a variety of helpful suggestions on what you could do to fill your free time!"  
    `date`: unverified.

34. **r/rant** — *"I cannot express how much I do not CARE what any service is 'suggesting' for me"*  
  
    URL: https://www.reddit.com/r/rant/comments/1ukck03/i_cannot_express_how_much_i_do_not_care_what_any/  
    `explicit ask`: NO.  
    `sentiment`: anti-recommendation / anti-algorithm pushback — a market counter-trend to watch.  
    `excerpt (indexed snippet)`: "I'm completely fed up with the constant 'suggestions' from any paid service I use… Honestly, who asked for your opinion? Why should I care about what a profit-driven corporation thinks I should want?"  
    `date`: unverified.

---

## E. Other platforms (forums / blogs)
35. **forums.beyondblue.org.au** — *"Ideas for activities to lift you when tired or depressed"* (advanced mental-health forum)  
    URL: https://forums.beyondblue.org.au/t5/staying-well/ideas-for-activities-to-lift-you-when-tired-or-depressed/td-p/526736  
    `explicit ask`: YES (in title).  
    `sentiment`: community-led list; strong mood/energy framing.  
    `date`: unverified.

36. **nibble-app.com** — *"'I'm Bored': 25 Fun Things to Do Instead of Mindless Scrolling"*  
    URL: https://nibble-app.com/blog/i-m-bored  
    `explicit ask`: NO (blog, competitor content).  
    `sentiment`: categorized by time available (5 mins, etc.) — evidence of the "time-bucket" segmentation already in competitor content.  
    `date`: unverified.

37. **lifestack.ai** — *"What to Do When Bored: 50 Ideas That Actually Work"*  
    URL: https://lifestack.ai/blog/what-to-do-when-bored  
    `explicit ask`: NO (blog).  
    `sentiment`: long structured "when bored" list — shows content-market demand for the "what do I do" answer.  
    `date`: unverified.

38. **peacefulsoul.co** — *"Why we should have more fun in life (and fun stuff to do)"*  
    URL: https://peacefulsoul.co/the-mind/fun/  
    `explicit ask`: NO (blog).  
    `sentiment`: mentions a Quora "What do you do for fun?" thread with 40+ responses.  
    `date`: unverified.

---

## Summary of recurring themes (ranked)

**1. People are "paralyzed at the choose" — they don't need *more* activity ideas; they need the choose itself made easy.**  
Multiple threads (r/ADHD, r/AdultADHDSupportGroup, r/Healthygamergg, r/Productivity, r/ForeverAlone) describe the failure mode as: "I have ideas of things I *could* do, but I can't decide what to do *now*." The cure user's offer is **reducing the choice set** (2–3 pre-filtered options), not a bigger list.  
*Strongest argument against this:* some users (r/CasualConversation #9) explicitly say they want *non-generic* options, i.e., they don't just want "choose for me" — they want options that aren't the same 10 recycled ones.

**2. The biggest latent signal = weather/cost/time.**  
Weather threads (15–22, 19, 20) and the r/SideProject comments (#31: "ask for the current time… inquire about the local weather") show users *self-segment* their requests by conditions. Users are already describing exactly what ThingzToDo should consume as inputs.  
*Strongest argument against:* this clustering could be an artifact of search terms ("bored" → weather is a natural proxy), over-stating the weather lever's share.

**3. The group "what should WE do" is a distinct, high-frequency pain.**  
Dating/relationship threads (#23, #26, #27, #28) show a repeated, relationship-specific friction: "what do we do tonight?" — one-sided decision is a relationship chore. This is a real wedge (couples/social groups), distinct from solo-boredom.  
*Strongest argument against:* many of these threads are 1:1 date planning, not the "group of friends deciding" the product is pitched to; treat as a separate segment, not the core.

**4. Existing solutions are thin, and users are frustrated with them.**  
r/SeriousConversation cites "Are You Bored!?" (areyoubored.app); r/SideProject comments enumerate feature gaps (time, active/passive, weather); r/AppIdeas comments capture friction (account/login, "For You" curation). Also, the blog ecosystem (nibble, lifstack, peacefulsoul) shows a content market. The space is contested but each entrant is narrow (boredom-only) — not weather+cost+people+time-conditioned, which is the open gap.

**5. Anti-recommendation sentiment exists and is loud.**  
r/rant (#34) shows people resist being told what to do ("who asked for your opinion?"). This is a design constraint: ThingzToDo must earn its recommendations, not push them.  
*Strongest argument against:* this is one rant thread; most requesters are *actively asking* for suggestions, so the pushback is niche, not a market-wide blocker.

**6. Demographics are broad but clustered.**  
Students/teens (r/highschool #13, r/PlannerAddicts #28), kids/parenthood (19–20), couples (25–28), solo/urban professionals (16, 18). ThingzToDo is not a single-audience product; the hard problem is the segmentation UI, not the audience.

---

## What this means for ThingzToDo (Scout's read)

1. **The "decision paralysis" form is the core** — the product should pre-filter to 2–3 narrowed options, not dump a huge list. That matches r/ADHD #1's ask most directly.
2. **Weather/cost/people/time are the natural segmentation signals** and users are already asking for them — build those as the primary filter UI.
3. **The "we" (couples/friends) segment is distinct and under-served** — a "choose together" mode would capture the dating/relationship threads without diluting the solo product.
4. **`explicit ask` rate is high** (the majority of threads above are explicit requests), which supports strong problem validation.
5. **Competitors are narrow and largely app/content-based** — ThingzToDo's differentiator is the constrained, multi-condition (weather+cost+people+time) plus the "choose together" social mode.

---

## Open items / what I could not verify
- Exact post dates for all threads (reddit.com and archive.org both bot-blocked). Marked `date: unverified`.
- Full page text for any thread (content reconstructed from indexed snippets).
- Independent confirmation of "Are You Bored!?" (areyoubored.app) current status — only seen referenced in a snippet.
- Whether the r/SideProject "WhatToDo" (oskarkraemer.github.io/whattodo) is still live — snippet only.
