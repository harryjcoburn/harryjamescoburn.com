#!/usr/bin/env python3
"""Content for the gated PDF packs on the AI page, and the HTML that renders them.

    python3 tools/packs.py            writes tools/_print/packs/*.html
    node tools/render_packs.mjs       renders them to assets/downloads/packs/*.pdf

Facts about Harry's builds must match what he has confirmed (see source/ai.html). Methods and
templates are general advice and are labelled as starting points, not results."""
from html import escape
from pathlib import Path

from brand import mark as brand_mark

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "_print" / "packs"
MARK = '<svg class="mark" viewBox="0 0 70 32" aria-hidden="true">' + brand_mark("currentColor", "none") + "</svg>"

# Published file names carry a short suffix so the PDFs aren't trivially guessable from the page.
PACKS = {
    "prompts": {"file": "hjc-sales-agent-prompts-7k2q.pdf", "title": "The Sales Agent Prompt Pack",
                "kicker": "Seven production prompts, one for each layer of the engine"},
    "workflows": {"file": "hjc-agent-workflows-p9x4.pdf", "title": "Sales Agent Workflows",
                  "kicker": "Three end-to-end builds, step by step"},
    "skills": {"file": "hjc-claude-skills-for-sales-m3v8.pdf", "title": "Claude Skills for Sales",
               "kicker": "Five ready-to-use skills, with the full SKILL.md files"},
}

# ---------------------------------------------------------------- prompts

PROMPTS = [
 {"n": "01", "layer": "Strategy", "title": "Find your real ICP from wins and losses",
  "use": "Before you write a pitch, hire a rep or build an outbound list. Run it again every quarter.",
  "inputs": "Your last 20 closed-won and 20 closed-lost deals as a CSV: company size, industry, country, deal value, discount, days to close, roles involved, lead source, reason won or lost, and usage after 90 days if you have it.",
  "prompt": """<role>
You are a go-to-market analyst. You find patterns in deal data, and you say plainly
when the data is too thin to support a conclusion.
</role>

<context>
Company: [company]. We sell [product] to [market].
The deals below are our last [20] closed-won and [20] closed-lost.
</context>

<task>
1. Clean the data. List any deal with missing fields and leave it out of the counts.
2. Rank the wins by fit: fastest to close, highest value, least discount, and
   strongest usage after 90 days. Show the top quarter.
3. Compare the top quarter with the losses and the bottom quarter. For each
   attribute, say what is different and how many deals support it.
4. Write our ideal customer profile in five lines: who they are, the problem they
   have, the trigger that makes them buy now, who signs, and who we say no to.
5. Give three signals we can find in public data to spot more companies like the
   top quarter, where to find each one, and how to test it.
6. List three questions this data cannot answer, and who in the team could.
</task>

<rules>
- Use only the data provided. Quote the number of deals behind every claim.
- If fewer than five deals support a pattern, label it "weak".
- Do not name a single large customer as the pattern.
</rules>

<output>
Markdown: a table of the top quarter, the five-line ICP, a signals table
(signal | where to find it | how to test it), then the open questions.
</output>

<data>
[paste deals as CSV]
</data>""",
  "check": "Read ten of the deals yourself. If its profile would not have picked your three best customers, it is wrong. Ask the rep who closed them.",
  "fails": ["Mistakes the lead source for fit (all good deals came from referrals, so it says \"referrals\").", "Builds the profile around one big logo.", "Fills gaps with general knowledge about your industry instead of your data."]},
 {"n": "02", "layer": "Win", "title": "Write the first reply to every inbound lead",
  "use": "As the writing step in an inbound agent, after enrichment and scoring. See the Inbound Agent workflow for the full build.",
  "inputs": "The form fields, the enrichment record (size, funding, tech, recent news, each with a source), the fit score and reason from your scoring step, and five real replies your best rep sent, each with the lead it was for.",
  "prompt": """<role>
You write the first reply to inbound leads for [company]. You write like our best
rep: short, specific and useful. You never invent facts about the lead.
</role>

<inputs>
<lead>[form fields]</lead>
<enrichment>[company facts, each with a source]</enrichment>
<fit score="[1-5]">[one-line reason from the scoring step]</fit>
<examples>[five replies our best rep sent, each with its lead]</examples>
</inputs>

<task>
1. Find the single most likely reason this person reached out. Use their own
   words first and the enrichment second.
2. Write the reply in three parts: one line that shows you read their request,
   one useful point about their situation, and one clear next step with
   [booking link]. Under 90 words.
3. Write a subject line of six words or fewer.
4. Check the reply against every rule below. Fix anything that fails before you
   answer.
</task>

<rules>
- Match the tone and length of the examples, not a generic sales email.
- Never write "I hope you're well".
- Only state a fact about their company if it is in the enrichment with a source.
- No pricing and no discounts.
- If fit is 1 or 2, reply helpfully with [self-serve resource] instead of a
  meeting.
</rules>

<output>
JSON only:
{"subject": "", "body": "", "facts_used": [{"fact": "", "source": ""}],
 "confidence": 0.0, "needs_human": false, "why": ""}
</output>""",
  "check": "Run it on your last 100 leads. Have your best rep mark every draft \"send as is\", \"send with edits\" or \"don't send\". Only let it send on its own once 95% are \"send as is\".",
  "fails": ["Opens with a compliment about the company that isn't in the data.", "Writes the same email for every lead because the examples were too similar.", "Books a meeting with a lead that should have had a resource."]},
 {"n": "03", "layer": "Grow", "title": "Spot renewal risk before the customer does",
  "use": "Every week, for every account within 90 days of renewal.",
  "inputs": "Per account: what they bought it for, usage over time, support tickets, call notes and the contacts involved.",
  "prompt": """<role>
You are a customer success analyst. You judge whether a customer has got what
they paid for, using evidence, not tone.
</role>

<context>
We review every account [90] days before renewal. Each account below has the
outcome they bought for, usage data, support tickets and call notes.
</context>

<task>
For each account:
1. State the outcome they bought for, in their words, and whether they have
   reached it. Quote the evidence.
2. Rate renewal risk as low, medium or high. Give the two strongest reasons.
3. Name the person whose view decides the renewal, and when we last spoke to them.
4. Suggest one action for the account owner this week. If risk is low, suggest
   one expansion opportunity with the evidence for it.
</task>

<rules>
- Never invent usage numbers. If data is missing, list what to ask the customer.
- A happy call note is not evidence of value. Usage and outcomes are.
- If the decision-maker has not been in a call for 60 days, risk is at least
  medium.
</rules>

<output>
A table: account | outcome reached? | risk | reasons | decider and last contact
| action this week. Then any accounts where data was missing.
</output>

<data>[paste account data]</data>""",
  "check": "Run it on last year's renewals. It should have flagged the customers who left, at least a quarter before they told you.",
  "fails": ["Rates risk from sentiment in the notes instead of usage.", "Misses that the champion has left.", "Suggests expansion to an account that is still onboarding."]},
 {"n": "04", "layer": "Team", "title": "Turn your best rep's habits into a 30-60-90",
  "use": "Before you hire, and every time you onboard someone new.",
  "inputs": "Transcripts of five calls by your best performer at different stages, their deal notes, and your sales stages with exit criteria.",
  "prompt": """<role>
You are a sales enablement lead. You turn what great reps actually do into
something a new hire can learn.
</role>

<context>
Below are transcripts of [five] calls and the deal notes from our best-performing
[AE / SDR], plus our stages and exit criteria.
</context>

<task>
1. Name the five things this person does on calls that others don't. For each,
   give a short quote and the stage where it happens.
2. Turn them into a 30-60-90 day plan for a new hire: what to learn, what to
   practise, and what "good" looks like at each point, measured in behaviour,
   not just numbers.
3. Write three role-play scenarios from real objections in the transcripts,
   with what a great answer covers.
4. Write a one-page call checklist for each stage.
</task>

<rules>
- Every habit must have a quote from the transcripts. No general sales advice.
- Keep the plan to what a manager can check in a weekly 1:1.
</rules>

<output>Markdown with four sections matching the tasks.</output>

<data>[paste transcripts, notes and stages]</data>""",
  "check": "Show it to the rep it is based on. If they don't recognise themselves, start again.",
  "fails": ["Lists textbook techniques instead of what this person does.", "Makes the plan about activity targets only."]},
 {"n": "05", "layer": "Motivation", "title": "Stress-test a comp plan before reps do",
  "use": "Before you launch a new plan, and whenever behaviour drifts from what you want.",
  "inputs": "The draft plan, targets, and the behaviour you want, for example good-fit customers, price held and multi-year deals.",
  "prompt": """<role>
You are a sales compensation analyst who thinks like the smartest rep on the
team: you look for the easiest way to earn the most.
</role>

<context>
Below is our draft comp plan, our targets, and the behaviour we want:
[for example good-fit customers, price held, multi-year deals].
</context>

<task>
1. Show, step by step, how a rep would earn the most under this plan.
2. Where that behaviour differs from what we want, say what it would cost us.
3. Run last quarter's real deals through the plan. Show who would have earned
   the most and whether those are the deals we want more of.
4. Suggest the simplest change to each part of the plan that fixes it. The
   whole plan must still be easy to explain in one minute.
</task>

<rules>
- Use our numbers. If something is unclear in the plan, list it as a question.
- Prefer one simple change over three clever ones.
</rules>

<output>Markdown: the gaming path, the cost, the back-test table, the changes.</output>

<data>[paste plan, targets and last quarter's deals]</data>""",
  "check": "The people who would have earned most under the new plan should be the people you'd want more of.",
  "fails": ["Proposes accelerators and kickers until nobody can explain the plan.", "Ignores that most reps will optimise for the next payout, not the year."]},
 {"n": "06", "layer": "Rhythm", "title": "Prepare the weekly pipeline review",
  "use": "Every week, the day before the pipeline meeting.",
  "inputs": "This week's and last week's pipeline exports, your stages and exit criteria.",
  "prompt": """<role>
You prepare our weekly pipeline review. You care about facts and next steps,
not activity.
</role>

<context>
Stages and exit criteria: [paste]
This week's export: [paste]
Last week's export: [paste]
</context>

<task>
1. List deals that moved stage, slipped a close date, changed value, or have had
   no activity for [14] days.
2. For each stalled deal, name the exit criterion it is missing for its stage,
   and the one question the owner should answer in the meeting.
3. Compare the forecast with the weighted pipeline. Say in one line whether the
   number looks safe, and which three deals decide it.
4. Flag any deal whose stage doesn't match its evidence.
</task>

<rules>
- Facts from the data only. No guesses about intent.
- One page. The meeting should take 30 minutes, not 90.
</rules>

<output>Markdown: changes, stalled deals with questions, forecast call, stage mismatches.</output>""",
  "check": "For four weeks, compare its \"safe or not\" call with what actually closed.",
  "fails": ["Treats emails sent as progress.", "Takes the rep's stage at face value."]},
 {"n": "07", "layer": "Systems", "title": "Clean up the CRM, one rule at a time",
  "use": "Once a month, and before you build any agent on top of CRM data.",
  "inputs": "An export of deals or contacts, and the fields you say are mandatory.",
  "prompt": """<role>
You audit CRM data. You find the cause of bad data, not just the bad records.
</role>

<context>
Below is an export of our [deals / contacts] and the fields we say are mandatory.
</context>

<task>
1. Find records with missing mandatory fields, duplicates, open deals with close
   dates in the past, and contacts with no company.
2. Group the problems by cause, not by record. Estimate how many records each
   cause affects.
3. For each cause, suggest one validation rule, automation or process change
   that would stop it happening again.
4. Rank the fixes by how much they would improve the forecast.
</task>

<rules>
- Do not change any data. Return a list for a person to review.
- Show record IDs so someone can check your work.
</rules>

<output>A table: cause | records affected | example IDs | fix | effort.</output>

<data>[paste export]</data>""",
  "check": "Spot-check 20 of the records it flags. Every one should be a real problem.",
  "fails": ["Reports 2,000 problems instead of five causes.", "Suggests making every field mandatory."]},
]

PROMPT_INTRO = [
 ("Give it your real examples", "The fastest way to better output is five real examples of what good looks like, from your best person. Generic prompts give generic results."),
 ("Structure the prompt", "Role, context, task, rules and output, each in its own tagged section. It makes the prompt easier to test, and easier for the model to follow."),
 ("Ask for output a system can use", "JSON or a fixed table, not prose. Then the next step, or the next agent, can read it, and you can measure it."),
 ("Make it check itself", "End the task with a self-check against the rules. It catches a lot before a person ever sees it."),
 ("Test on history before the future", "Run it on last quarter's data, where you know the answer, before you trust it on this quarter's."),
 ("Hold it to the 95% rule", "Your best person marks every output: send as is, send with edits, or don't send. It only runs on its own once 95% go as is."),
]

# ---------------------------------------------------------------- workflows

WORKFLOWS = [
 {"slug": "inbound", "title": "The inbound agent", "sub": "Reply to every lead in minutes, with people approving until it earns the right to send alone.",
  "proof": "I built this at UXCam with HubSpot and Claude Code, with Apollo, Lusha and LinkedIn Sales Navigator for enrichment: several agents in one flow, one enriching, one scoring fit from the profile, one writing the message, with every lead and drafted reply posted to a Slack channel for feedback and approval. First reply went from about a day to 5 minutes.",
  "stack": [("CRM and trigger", "HubSpot form submission"), ("Enrichment", "Apollo, Lusha and LinkedIn Sales Navigator"), ("Agents", "Claude, orchestrated with Claude Code"), ("Approval", "A Slack channel: feedback and approve to send"), ("Booking", "Your calendar link")],
  "steps": [
   ("Trigger", "A form is submitted in HubSpot. The workflow passes the contact and form answers to the orchestrator.", "Contact ID, form answers, page and source"),
   ("Enrichment agent", "Researches the company and person: size, funding, what they sell, tech, hiring, recent news. Every fact keeps its source.", "Enrichment record with sources"),
   ("Scoring agent", "Scores fit from 1 to 5 against your written ICP, with a one-line reason and the facts behind it.", "Fit score, reason, evidence"),
   ("Writing agent", "Drafts the reply in your best rep's voice from their real examples, using prompt 02 from the Prompt Pack. Returns JSON with the facts it used.", "Subject, body, facts used, confidence"),
   ("Quality check", "A separate check: every fact must be in the enrichment, no banned phrases, length and tone in range. Fails go back to the writer once, then to a person.", "Pass or fail, with reasons"),
   ("Approval in Slack", "Every lead lands in one Slack channel as it comes in: whether it qualifies, the details that matter, and the reply already drafted. The team gives feedback right on the message and approves to send. All feedback stays in that one channel.", "Decision and feedback, in one place"),
   ("Send and log", "The approved reply is sent from the rep's mailbox. Everything is logged on the HubSpot contact: score, reason, draft, decision.", "Sent email, CRM timeline"),
   ("Hot lead alert", "Fit 4 or 5 alerts an SDR to call straight away, with the brief in the message.", "Slack alert with call brief"),
   ("Learn", "Every edit and rejection is saved with its reason. Once a week, the best edits become new examples for the writer.", "Better examples, rising approve rate")],
  "rollout": [("Shadow", "Two weeks. The agent drafts for every lead. Nobody sees it. A person writes as usual, and you compare."),
              ("Approve", "Every draft goes to Slack. Measure \"approved without edits\" by segment."),
              ("Automate", "A segment sends on its own once 95% are approved without edits over at least [200] leads."),
              ("Audit", "One in twenty sent replies is still reviewed. If quality drops, that segment goes back to approval.")],
  "metrics": ["Time to first reply", "Approved without edits, by segment", "Reply and meeting rate", "Inbound to sales-qualified rate", "Cost per lead processed"],
  "pitfalls": ["Starting with automation instead of approval. The approval data is what tells you when it's ready.", "One agent doing everything. Separate steps are easier to test and fix.", "No reason on rejections. Without the reason, you can't teach it."]},
 {"slug": "outbound", "title": "The outbound signal engine", "sub": "Find the companies where you make the biggest difference, then test the message by person, company and timing.",
  "proof": "I built this at UXCam with Clay and Claude Code, using app store data to find companies where the product could make a big difference. In the first month, the first run reached about 500 accounts and 4,000 contacts, and Lemlist warmed up the sending addresses.",
  "stack": [("Data and enrichment", "Clay, plus the public data your ICP shows up in"), ("Research and writing", "Claude, orchestrated with Claude Code"), ("Sending", "Separate warmed-up sending domains"), ("CRM", "Every touch logged")],
  "steps": [
   ("Define the signal", "From your ICP work (prompt 01), pick the public signals that predict fit. For a mobile product that can be app store data: number of apps, ratings, update rate.", "Two or three testable signals"),
   ("Build the account list", "Pull every company that matches, enrich them, and score them on the signals. Keep the score and why.", "Scored account list"),
   ("Find the people", "For each account, the two or three roles that feel the problem and the one that signs.", "Contacts by persona"),
   ("Research agent", "Writes a short \"why now\" per account from the signals and news, with sources.", "Account brief with sources"),
   ("Writing agent", "Writes a short sequence per persona, using the brief. Every claim must come from the brief.", "Sequence per persona"),
   ("Check and approve", "A person reviews a sample from every batch before it sends, using the same \"would I send this\" test.", "Approved batch"),
   ("Send safely", "Use separate sending domains, warm them up first, keep volumes low per inbox, and stop on bounces.", "Healthy deliverability"),
   ("Test", "Change one thing at a time: the persona, the company type, or the timing. Track replies and meetings, not opens.", "What works, by segment"),
   ("Feed back", "Positive replies and meetings sharpen the signals and the ICP. Bad-fit replies become \"say no\" rules.", "Better list each round")],
  "rollout": [("Small batch", "Start with 50 accounts you know well, so you can judge the research."),
              ("First run", "Scale to your first full list once the briefs are right and replies come in."),
              ("Iterate", "Weekly tests on persona, company and timing. Results build over months, not days."),
              ("Scale", "Add volume only to the segments that work.")],
  "metrics": ["Positive reply rate by segment", "Meetings booked per 100 accounts", "Bounce and spam rates per inbox", "Pipeline created by signal"],
  "pitfalls": ["Sending from your main domain.", "Scaling before you know which segment works.", "Writing \"personalised\" lines from facts nobody checked."]},
 {"slug": "site", "title": "A lead engine for a small business, on free tools", "sub": "The one that runs this website: a free scorecard that sends a report from your own inbox and logs every lead.",
  "proof": "This is the system behind the scorecard on harryjamescoburn.com, built in October 2026 on free tiers.",
  "stack": [("Lead magnet", "An interactive scorecard on the website"), ("Email", "A Google Apps Script that sends from your own Gmail"), ("CRM", "HubSpot free"), ("Booking", "Cal.com, synced to HubSpot")],
  "steps": [
   ("The offer", "A two-minute scorecard: ten taps, a score, three first moves. Useful on its own, with a fuller report by email.", "A reason to leave an email"),
   ("Capture", "The visitor asks for the report, with clear consent for the report and occasional follow-up.", "Name, email, answers, consent"),
   ("Send from your own inbox", "A small Apps Script rebuilds the report from the answers and sends it from your Gmail. Your domain already signs Gmail, so it lands in the inbox, not spam.", "Report delivered, copy to you"),
   ("Log the lead", "The same script records the contact and their scores in HubSpot.", "A CRM record with the report"),
   ("Book", "Every report has a booking link. Cal.com creates the contact and meeting in HubSpot.", "Meeting on the record"),
   ("Review weekly", "Once a week, look at visits, completions, reports and bookings, and change one thing.", "One improvement a week")],
  "rollout": [("Build", "One afternoon."), ("Test", "Send yourself a report from the live site."), ("Promote", "Link it from LinkedIn posts and your email signature, with UTM tags."), ("Improve", "Change one thing a week, based on completions.")],
  "metrics": ["Scorecard completions", "Report requests", "Calls booked", "Where they came from"],
  "pitfalls": ["Sending from a CRM's servers on a free plan, which often lands in spam.", "Asking for too much before giving anything useful.", "No consent wording."]},
]

# ---------------------------------------------------------------- skills

SKILLS_INTRO = ("A skill is a folder that teaches Claude how to do one job your way. At its heart is a SKILL.md file: a short "
                "name and description that tell Claude when to use it, and instructions it follows when it does. You can add "
                "reference files, like your ICP or voice samples, and scripts. Claude only loads a skill when the task needs it, "
                "so you can have many without cluttering every conversation.")

SKILLS = [
 {"name": "account-research", "title": "Account research brief", "files": ["SKILL.md", "reference/icp.md"],
  "why": "A one-page brief on any account before a call or outbound, with every fact sourced.",
  "md": """---
name: account-research
description: Research a company before a sales call or outbound and return a one-page brief with sources. Use when asked to research, prep or look into an account.
---

# Account research brief

## Steps
1. Read reference/icp.md for who we sell to and the signals that matter.
2. Research the company: what they sell, size, funding, leadership, recent news,
   hiring, and the tech they use. Keep the source for every fact.
3. Score fit against the ICP from 1 to 5 and say why in one line.
4. Write three hypotheses about the problems we could solve, each linked to a fact.
5. Suggest the two people to contact first and why.

## Output
A one-page brief with these headings: Snapshot, Why now, Fit, Hypotheses,
Who to contact, Sources.

## Rules
- Every fact needs a source link. If you can't find one, say "not found".
- Never guess revenue. Use "not public" if it isn't.
- Keep it to one page."""},
 {"name": "call-prep", "title": "Call prep", "files": ["SKILL.md", "reference/stages.md"],
  "why": "Turns CRM notes and the account brief into an agenda, questions and the exit criterion for this call.",
  "md": """---
name: call-prep
description: Prepare for a sales call from the CRM notes, emails and account brief. Use when asked to prep a call, meeting or demo.
---

# Call prep

## Steps
1. Find the deal stage and read its exit criteria in reference/stages.md.
2. Read the last three touches: notes, emails and any call summary.
3. Write the one outcome this call must achieve to meet the exit criterion.
4. Write a 30-minute agenda with timings.
5. Write five questions that close the biggest gaps in what we know.
6. List the two objections most likely to come up, with what a good answer covers.

## Output
Outcome, Agenda, Questions, Likely objections, What we still don't know.

## Rules
- Questions must be open and about their business, not our product.
- If something in the notes contradicts something else, flag it."""},
 {"name": "follow-up-in-my-voice", "title": "Follow-up in my voice", "files": ["SKILL.md", "reference/voice.md", "reference/examples.md"],
  "why": "Writes follow-ups that sound like you, from your own rules and real examples.",
  "md": """---
name: follow-up-in-my-voice
description: Write a follow-up email after a sales call in my voice. Use when asked to write a follow-up, recap or next-steps email.
---

# Follow-up in my voice

## Steps
1. Read reference/voice.md for my rules and reference/examples.md for five real
   follow-ups I sent.
2. From the call notes, pull out what they said matters, what we agreed, and the
   next step with a date.
3. Write the email: thank them for one specific thing, recap in three bullets,
   confirm the next step and owner.
4. Check it against every rule in voice.md and fix anything that fails.

## Rules
- Under 120 words.
- Use their words for their problem, not ours.
- Never "I hope you're well". Sign off the way voice.md says.
- Only include what was actually said on the call."""},
 {"name": "pipeline-review", "title": "Weekly pipeline review", "files": ["SKILL.md", "reference/stages.md"],
  "why": "Prepares a one-page review from two pipeline exports, so the meeting is about decisions.",
  "md": """---
name: pipeline-review
description: Prepare the weekly pipeline review from this week's and last week's CRM exports. Use when asked about the pipeline, forecast or deal review.
---

# Weekly pipeline review

## Steps
1. Read the stage exit criteria in reference/stages.md.
2. Compare the two exports. List deals that moved stage, slipped, changed value
   or had no activity for 14 days.
3. For each stalled deal, name the missing exit criterion and one question for
   the owner.
4. Compare forecast with weighted pipeline and name the three deals that decide
   the number.
5. Flag deals whose stage doesn't match their evidence.

## Output
One page: Changes, Stalled deals, Forecast call, Stage mismatches.

## Rules
- Facts from the exports only.
- Never change CRM data."""},
 {"name": "icp-fit-check", "title": "ICP fit check", "files": ["SKILL.md", "reference/icp.md", "reference/rubric.md"],
  "why": "Scores any account or list against your written ICP the same way every time.",
  "md": """---
name: icp-fit-check
description: Score one account or a list of accounts against our ICP and say who to prioritise and who to say no to. Use when asked if a company is a fit, or to prioritise a list.
---

# ICP fit check

## Steps
1. Read reference/icp.md and the scoring rubric in reference/rubric.md.
2. For each account, find the facts the rubric needs. Keep sources.
3. Score each criterion, then the total, exactly as the rubric says.
4. Put each account in one bucket: prioritise, nurture, or say no.

## Output
A table: account | score | bucket | the deciding facts | sources.

## Rules
- If a fact the rubric needs is missing, score that criterion 0 and say so.
- Apply the rubric the same way every time. Don't adjust for brand names."""},
]


# ---------------------------------------------------------------- HTML

CSS = """@page{size:A4;margin:16mm 16mm 18mm}
@font-face{font-family:G;src:url(../../../assets/fonts/schibsted-grotesk-latin-wght-normal.woff2);font-weight:400 900}
@font-face{font-family:S;src:url(../../../assets/fonts/newsreader-latin-opsz-italic.woff2);font-style:italic}
@font-face{font-family:M;src:url(../../../assets/fonts/roboto-mono-latin-500-normal.woff2)}
*{box-sizing:border-box}html,body{margin:0}
body{font-family:G,Arial,sans-serif;color:#0D1411;background:#fff;font-size:10pt;line-height:1.5}
.mono{font-family:M,monospace;font-size:7.4pt;letter-spacing:.08em;text-transform:uppercase;color:#B8461C}
.mark{width:18mm;height:auto;color:#0D1411}.mark .stn{fill:#E2582B}
.cover{height:262mm;display:flex;flex-direction:column;justify-content:space-between;page-break-after:always;background:#10372A;color:#fff;margin:-16mm -16mm 0;padding:22mm 18mm}
.cover .mark{color:#fff;width:24mm}
.cover h1{font-size:40pt;line-height:.98;letter-spacing:-.045em;margin:0 0 5mm}
.cover h1 em{font-family:S,serif;font-weight:400;color:#F4B63F}
.cover p{color:#D7E6DD;font-size:12pt;max-width:140mm}
.cover .mono{color:#F4B63F}
.cover .by{display:flex;justify-content:space-between;align-items:flex-end;font-size:9pt;color:#D7E6DD;border-top:.6pt solid rgba(255,255,255,.25);padding-top:4mm}
h2{font-size:20pt;letter-spacing:-.03em;line-height:1.05;margin:1mm 0 3mm}
h3{font-size:11.5pt;margin:4mm 0 1.5mm;letter-spacing:-.01em}
p{margin:0 0 2mm}
ul,ol{margin:0 0 2mm;padding-left:5mm}li{margin-bottom:1mm}
.sec{page-break-before:always}
.lede{color:#5B6660;font-size:11pt;margin-bottom:4mm}
pre{font-family:M,monospace;font-size:7.6pt;line-height:1.45;background:#F5F3EC;border-radius:2.5mm;padding:4mm 4.5mm;white-space:pre-wrap;margin:0 0 3mm;border-left:2pt solid #E2582B}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.box{border:.8pt solid #E4E8E4;border-radius:2.5mm;padding:3.5mm 4mm;break-inside:avoid}
.box b{display:block;margin-bottom:1mm}
.box p{color:#5B6660;font-size:9pt;margin:0}
.check{background:#10372A;color:#fff;border-radius:2.5mm;padding:3.5mm 4.5mm;margin:2mm 0 3mm;break-inside:avoid}
.check b{color:#F4B63F}
.meta{display:grid;grid-template-columns:28mm 1fr;gap:1.5mm 4mm;font-size:9pt;margin-bottom:3mm}
.meta dt{font-family:M,monospace;font-size:7pt;letter-spacing:.08em;text-transform:uppercase;color:#5B6660;padding-top:.6mm}
.meta dd{margin:0}
table{width:100%;border-collapse:collapse;font-size:8.8pt;margin:1mm 0 3mm}
th{text-align:left;font-family:M,monospace;font-size:6.8pt;letter-spacing:.08em;text-transform:uppercase;color:#5B6660;border-bottom:1pt solid #0D1411;padding:1.5mm 2mm}
td{border-bottom:.5pt solid #E4E8E4;padding:2mm;vertical-align:top}
td:first-child{font-weight:700;width:30mm}
tr{break-inside:avoid}
.proof{background:#FFF6F2;border-radius:2.5mm;padding:3.5mm 4.5mm;margin-bottom:3mm;font-size:9.5pt}
.flow{display:flex;flex-wrap:wrap;gap:1.5mm;margin:1mm 0 4mm}
.flow span{font-family:M,monospace;font-size:7pt;letter-spacing:.05em;text-transform:uppercase;background:#0D1411;color:#fff;border-radius:1.5mm;padding:1.4mm 2.2mm}
.flow i{font-style:normal;color:#B8461C;align-self:center}
.end{page-break-before:always;background:#F5F3EC;border-radius:3mm;padding:8mm}
.end h2 em{font-family:S,serif;font-weight:400;color:#B8461C}
a{color:#0D1411}
.files{font-family:M,monospace;font-size:7.6pt;color:#5B6660;margin-bottom:2mm}
"""


def cover(title_html, kicker, intro):
    return f"""<section class="cover"><div>{MARK}</div>
<div><div class="mono">{escape(kicker)}</div><h1>{title_html}</h1><p>{escape(intro)}</p></div>
<div class="by"><span>Harry James Coburn<br>GTM and AI sales adviser · Berlin · London</span><span>harryjamescoburn.com</span></div></section>"""


def ending():
    return """<section class="end"><div class="mono">Want these built into your engine?</div>
<h2>Trained on your data, checked <em>to your standard.</em></h2>
<p>In a Commercial Systems Build I set up agents like these on your own deals, calls and CRM, and only switch them on once they send what your best people would send.</p>
<p><b>Book an intro call:</b> <a href="https://cal.com/harryjamescoburn/intro?utm_source=pdf&amp;utm_medium=pack">cal.com/harryjamescoburn/intro</a><br>
<b>Score your sales engine:</b> <a href="https://harryjamescoburn.com/scorecard.html?utm_source=pdf&amp;utm_medium=pack">harryjamescoburn.com/scorecard</a><br>
<b>Email:</b> harry@harryjamescoburn.com</p>
<p class="mono" style="margin-top:6mm;color:#5B6660">These are starting points. Test every prompt, workflow and skill on your own data before you trust it.</p></section>"""


def doc(title, body):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{escape(title)} · Harry James Coburn</title><style>{CSS}</style></head><body>{body}</body></html>'


def prompts_html():
    intro = "".join(f'<div class="box"><b>{escape(a)}</b><p>{escape(b)}</p></div>' for a, b in PROMPT_INTRO)
    body = cover("The Sales Agent <em>Prompt Pack</em>", PACKS["prompts"]["kicker"],
                 "Seven prompts I use as starting points for agents, one for each layer of the Coburn Commercial Engine. Each comes with when to use it, what to feed it, how to check it and where it usually goes wrong.")
    body += f'<section><div class="mono">Before you start</div><h2>How to get prompts to work in production</h2><p class="lede">Most prompts fail for the same few reasons. These six fix most of them.</p><div class="grid2">{intro}</div>'
    body += '<h3>The layers</h3><table><tr><th>Layer</th><th>Prompt</th></tr>' + "".join(
        f"<tr><td>{p['n']} · {escape(p['layer'])}</td><td>{escape(p['title'])}</td></tr>" for p in PROMPTS) + "</table></section>"
    for p in PROMPTS:
        fails = "".join(f"<li>{escape(x)}</li>" for x in p["fails"])
        body += f"""<section class="sec"><div class="mono">{p['n']} · {escape(p['layer'])}</div><h2>{escape(p['title'])}</h2>
<dl class="meta"><dt>Use it</dt><dd>{escape(p['use'])}</dd><dt>Feed it</dt><dd>{escape(p['inputs'])}</dd></dl>
<pre>{escape(p['prompt'])}</pre>
<div class="check"><b>Check before you trust it.</b> {escape(p['check'])}</div>
<h3>Where it usually goes wrong</h3><ul>{fails}</ul></section>"""
    return doc(PACKS["prompts"]["title"], body + ending())


def workflows_html():
    body = cover("Sales Agent <em>Workflows</em>", PACKS["workflows"]["kicker"],
                 "Three builds, each step by step: what triggers it, what every agent does, where a person checks, how to roll it out and what to measure. The first two are based on systems I built at UXCam. The third runs my own website.")
    for w in WORKFLOWS:
        flow = '<i>→</i>'.join(f"<span>{escape(s[0])}</span>" for s in w["steps"])
        stack = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td></tr>" for a, b in w["stack"])
        steps = "".join(f"<tr><td>{i + 1}. {escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td></tr>" for i, (a, b, c) in enumerate(w["steps"]))
        roll = "".join(f'<div class="box"><b>{escape(a)}</b><p>{escape(b)}</p></div>' for a, b in w["rollout"])
        mets = "".join(f"<li>{escape(x)}</li>" for x in w["metrics"])
        pits = "".join(f"<li>{escape(x)}</li>" for x in w["pitfalls"])
        body += f"""<section class="sec"><div class="mono">Workflow</div><h2>{escape(w['title'])}</h2><p class="lede">{escape(w['sub'])}</p>
<div class="proof">{escape(w['proof'])}</div>
<div class="flow">{flow}</div>
<h3>The stack</h3><table>{stack}</table>
<h3>Step by step</h3><table><tr><th>Step</th><th>What happens</th><th>Output</th></tr>{steps}</table>
</section><section class="sec"><div class="mono">{escape(w['title'])} · rollout</div><h2>Roll it out, then measure it</h2>
<div class="grid2">{roll}</div>
<div class="grid2" style="margin-top:3mm"><div><h3>Measure</h3><ul>{mets}</ul></div><div><h3>Avoid</h3><ul>{pits}</ul></div></div></section>"""
    return doc(PACKS["workflows"]["title"], body + ending())


REFS = {
 "account-research": [
  "reference/icp.md",
  "# Our ICP\nWho: [B2B SaaS, 50 to 500 staff, Series A to C]\nProblem: [the problem we solve, in the customer's words]\nTrigger to buy now: [new funding, new market, new sales leader, ...]\nWho signs: [role]   Who uses it: [roles]\nSignals in public data: [hiring for X, uses tool Y, app store presence, ...]\nSay no to: [too small, wrong market, no budget owner, ...]",
  "Research [company] before my call on Thursday."
 ],
 "call-prep": [
  "reference/stages.md",
  "# Stages and exit criteria\n1. Discovery: problem confirmed in their words, impact sized, decider named.\n2. Solution: they agree our approach fits, success criteria written down.\n3. Proposal: price shared, decision process and date confirmed.\n4. Commit: legal and procurement steps listed with owners and dates.\n5. Closed won: signed, kick-off booked.",
  "Prep my call with [company] tomorrow at 10."
 ],
 "follow-up-in-my-voice": [
  "reference/voice.md",
  "# How I write\n- Short sentences. British spelling. No em dashes.\n- Open with something specific from the call, never \"I hope you're well\".\n- First email to someone new: sign off \"Thanks, [name]\". After that: [initials].\n- Never promise what we didn't agree.\n- One clear next step with a date.",
  "Write the follow-up from today's call with [name]. Notes below."
 ],
 "pipeline-review": [
  "reference/stages.md",
  "# Stages and exit criteria\nUse the same file as call-prep, so the review and the reps\njudge deals against the same standard.\nAdd your weighting per stage, e.g. Discovery 10%, Solution 25%,\nProposal 50%, Commit 80%.",
  "Prepare this week's pipeline review. Exports attached."
 ],
 "icp-fit-check": [
  "reference/rubric.md",
  "# Fit rubric (0 to 3 each, 15 max)\nSize: 0 under [x] staff, 3 for [range]\nMarket: 0 outside [markets], 3 for [core market]\nTrigger: 0 none found, 3 [strong trigger] in the last 90 days\nBuyer: 0 no clear owner, 3 [role] in place\nTech: 0 incompatible, 3 uses [tool we plug into]\nBuckets: 11+ prioritise, 6 to 10 nurture, under 6 say no",
  "Score this list of 40 accounts against our ICP."
 ]
}


def skills_html():
    body = cover("Claude Skills <em>for Sales</em>", PACKS["skills"]["kicker"],
                 "Five skills that teach Claude to do common sales jobs your way, every time. Copy the SKILL.md files, add your own reference files, and test them on real accounts.")
    rows = "".join(f"<tr><td>{escape(s['title'])}</td><td>{escape(s['why'])}</td></tr>" for s in SKILLS)
    body += f"""<section><div class="mono">Start here</div><h2>What a skill is</h2><p class="lede">{escape(SKILLS_INTRO)}</p>
<h3>How to set one up</h3><ol><li>Make a folder named after the skill, for example <b>account-research</b>.</li>
<li>Add SKILL.md with the name, a description of when to use it, and the steps.</li>
<li>Add your reference files: your ICP, stages, voice rules or examples. Keep each one short.</li>
<li>Add it to Claude, then test it on five real accounts. Tighten the steps wherever the output misses.</li></ol>
<h3>The five skills</h3><table>{rows}</table>
<div class="check"><b>Tip.</b> The description decides when Claude uses a skill. Say what the skill does and the words people use when they need it.</div></section>"""
    for s in SKILLS:
        body += f"""<section class="sec"><div class="mono">Skill · {escape(s['name'])}</div><h2>{escape(s['title'])}</h2><p class="lede">{escape(s['why'])}</p>
<p class="files">Files: {' · '.join(escape(f) for f in s['files'])}</p><pre>{escape(s['md'])}</pre>
<h3>Make it yours: {escape(REFS[s['name']][0])}</h3><pre>{escape(REFS[s['name']][1])}</pre>
<div class="check"><b>Try it.</b> \u201c{escape(REFS[s['name']][2])}\u201d Test it on five real accounts, then tighten the steps wherever the output misses.</div></section>"""
    return doc(PACKS["skills"]["title"], body + ending())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for key, fn in (("prompts", prompts_html), ("workflows", workflows_html), ("skills", skills_html)):
        (OUT / PACKS[key]["file"].replace(".pdf", ".html")).write_text(fn())
    print("Wrote", ", ".join(p["file"].replace(".pdf", ".html") for p in PACKS.values()))


if __name__ == "__main__":
    main()
