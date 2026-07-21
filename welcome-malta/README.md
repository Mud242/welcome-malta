# Welcome Malta — Digital Pre-Arrival Onboarding Platform (Prototype)




An informative web app for EU/EEA/Swiss jobseekers relocating to Malta, aligned with —
and cross-checked against — current **EURES Malta adviser guidance** (21 Jul 2026).

---

### 1. Link out, don't copy
Cards contain *orientation*, but the authority always lives at the official source
(`cfr.gov.mt`, `identita.gov.mt`, `mfhea.mt`, `dier.gov.mt`, `eures.europa.eu` …). Stable
EU law (Reg. 492/2011, 883/2004, Dir. 2014/92/EU) anchors the evergreen core; volatile
numbers (minimum wage, rent ranges, fees) are deliberately few and clearly flagged.

### 2. Single content registry, separate from code
Every factual entry lives in one JS array (`REGISTRY` in `index.html`) with a
`verified:` date and its `src`. In production this becomes `content.json` or a headless
CMS (Contentful / Strapi / a shared spreadsheet exported as JSON) 

### 3. Built-in freshness engine (the app audits itself)
Header chips and the verification stickers on every card show:
- 🟢 verified < 90 days ago · 🟡 90–180 days "re-verify soon" · 🔴 >180 days "RE-VERIFY"

The **Content Health Dashboard** (footer link / header chips) sorts stale topics to the
top — it *is* the maintenance backlog. The prototype intentionally keeps some amber/red
entries so you can see the queue working.

### 4. Automated link-checking (`tools/check_links.py`)
Websites change (Identity Malta → **Identità**; TMS URL moved to `…-tms_en`). Run monthly
(cron/GitHub Action); it crawls every outbound link, flags redirects (update the registry
to the final URL) and dead links (breaks CI → someone gets nudged). Learning from the
first run: Maltese gov. sites (cfr, dier, jobsplus) bot-block datacenter traffic with
403, so the script classifies 403 as "bot-blocked — spot-check manually", not as dead.

### 5. Human feedback loop
Footer "report outdated info" mailto + (in production) EURES adviser sign-off of the
monthly re-verification queue. The app curates content that EURES/Jobsplus already
publish — it doesn't invent it.

### 6. Honest framing
Visible snapshot date + disclaimer that it is not an official service and official
pages win on conflicts — the correct legal posture for an NGO/social-project tool.

---

## Staying current: the operating model

**layers of defence**

1. **Predictable change calendar** — most policy changes are on a schedule you can plan for:
   | When | What changes | Watch |
   |---|---|---|
   | **October** (Budget speech) | next year's wage/COLA announced | DIER |
   | **1 January** | minimum wage/COLA effective; tax bands; Tallinja plans | DIER, MPT, CFR |
   | **Quarterly** | rents, fees, portal URLs, schemes (TMS) | NSO, Housing Authority, eures.com.mt |
   | **Continuous** | gov.site restructures, renamed agencies (Identity Malta → Identità!) | link checker |

2. **Automated watchers**
   - `tools/check_links.py` — is the source page still alive?
   - `tools/watch_sources.py` — does the source page *still say what we claim*? Pins volatile values (e.g. minimum wage `229.44`) to the DIER page; a missing pin = review alert. Gov sites bot-block scripts, so un-fetchable topics are printed as a manual spot-check queue instead of failing.
   - `.github/workflows/content-watch.yml` — runs both monthly on GitHub Actions; failure emails the repo owner.

3. **Human review cadence** — the dashboard's amber/red queue is the to-do list: 🟡 90 days, 🔴 180 days. Assign one owner; EURES Malta adviser sign-off each quarter.

4. **Feedback loop** — footer "report outdated info" + chat fallbacks route users to EURES advisers, so users themselves flag drift early.

When a change is genuine: fix card copy → bump `verified:` in REGISTRY → update pins in `watch_sources.py` → commit. ~15 minutes per change.

---

## Feature map (prototype vs. production)

| Feature | Prototype | Production path |
|---|---|---|
| Job search (Jobsplus pre-move self-registration, EURES portal) | ✅ — no private commercial sites named | live job-widget via Jobsplus/EURES APIs |
| Targeted Mobility Scheme (financial support) | ✅ guidance + apply-before-start warning | TMS eligibility checker |
| Papers: TIN, SSC, eResidence | ✅ step pipelines | content JSON, quarterly review |
| Social security portability (U1/U2/A1) + double-taxation check | ✅ | per-country variants (EU-27 templates) |
| Qualifications (MFHEA regulated professions, MQRIC recognition) | ✅ | status-tracker for applications |
| Banking incl. N26/Revolut bridge & SEPA IBAN right | ✅ | — |
| Housing: area snapshot, tenant rights, temp stay/SIM/utilities, scam flags | ✅ | ranges refreshed from NSO/market data |
| Cost of living (Numbeo) & climate | ✅ | embedded Numbeo widget |
| Work & rights (2026 minimum wage, leave, probation) | ✅ | annual COLA update job |
| Health (EHIC 3-month rule → SSC entitlement) | ✅ | — |
| Transport (MyTallinja plans, driving licence exchange) | ✅ | — |
| Family: schools/childcare, EU Pet Passport, integration | ✅ | enrolment wizard |
| 23-item interactive checklist | ✅ localStorage | user accounts, per-user notes |
| Chat support | ✅ rule-based demo | live handoff to EURES advisers (Tawk.to/Intercom-style), FAQ model on approved snapshot + GDPR notice |
| Freshness dashboard | ✅ client-side | server-side + email alerts |
| Multilingual | roadmap | EU-24 via i18n JSON |

## Verified-facts log (2026-07-21)
- Jobsplus self-registration usable pre-move with home address; unemployed registration for new arrivals — jobsplus.gov.mt
- Jobsplus vacancies mirrored on EURES portal; TMS at eures.europa.eu/eures-services/eures-targeted-mobility-scheme-tms_en
- U1/U2/A1 portability guidance; double-taxation treaty network (70+) — consultant EURES Malta guidance, cfr.gov.mt
- Regulated professions list & MQRIC online recognition — mfhea.mt (bot-blocks scripts; fine in browsers)
- Minimum wage 2026: €229.44/wk (18+), COLA €4.66/wk — DIER
- eResidence via Expatriates Portal, ~48-working-hour response — Identità
- Free resident bus fares via MyTallinja plans (Intro free / Basic €14.50) — Malta Public Transport
- EHIC covers first ~3 months; SSC-linked entitlement after starting work — EURES L&W Malta page
- EURES Malta: eures.jobsplus@gov.mt, +356 2220 1662, Ħal Far office — eures.com.mt
