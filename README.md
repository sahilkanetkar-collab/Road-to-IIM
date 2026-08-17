# Road to IIM — Portal Repository

Student portal for Road to IIM (IPMAT / UGAT / JIPMAT / IIMK prep), served via GitHub Pages.
**Root filenames are load-bearing** — tests fetch `whitelist.json` by relative path, `tests.json` drives the homepage catalogue, and students hold shared links. Do not rename or move live files. New projects go in folders (see `studio/`).

## Map

| Area | Files |
|---|---|
| **Homepage & catalogue** | `index.html` · `tests.json` (add tests here, no HTML edits) · `sky.html` (constellation view) |
| **Online Tests 9–24** | `RoadToIIM_Test*_OnlineTest.html` |
| **Rapid Fire / Speed Tests 01–10** | `RoadToIIM_SpeedTest*_VocabGrammar.html` |
| **Concept Tests CT01–04** | `RoadToIIM_ConceptTest*.html` |
| **RC Series 01–05** | `RoadToIIM_RC_Series*.html` |
| **Challenge Series** | `RoadToIIM_UGATB_VA_ChallengeMock.html` |
| **IWP (Norman Lewis, Weeks 1–9)** | `iwp_week*_session.html` · `iwp_collocations_session.html` |
| **RLS (Read Like a Scholar)** | `RLS_Week*.html` · `rls_tracker.html` |
| **BYOT + question pools** | `byot.html` · `pool_cr/gr/rc/sc.json` |
| **Student tools** | `the_vault.html` · `mistake_bank.html` · `aeon_condenser.html` · `current_affairs.html` · `deck_studio.html` · `downloads.html` · `va_mixed_test.html` |
| **Quiz Live (classroom)** | `quiz_live.html` (presenter) · `quiz_join.html` (students) |
| **Tracker & analytics** | `road_to_iim_tracker_v2.html` · `riim_tags.json` (legacy Tests 16–21) · `riim_tags_RF01.json` |
| **Access control** | `whitelist.json` (fetched relatively by 36 test files — never move) |
| **PWA shells** | `deck-studio-sw.js` + `.webmanifest` · `current-affairs-sw.js` + `.webmanifest` · `icons/` |
| **Test Builder Studio** | `studio/` (installable PWA — AI drafts, Gate-2 review, portal-wired exports) |
| **Constellation PWAs** | `constellation/` · `verbal-constellation/` |
| **Dev tools** | `tools/riim_audit.py` (Gate-1 structural audit) |
| **Archive** | `archive/` — superseded versions kept for reference (`sky_v1_backup`, `sky_v2`, `index_classic`) |

## Conventions

- Every new test: 16-field payload (`topicErrors` = field 16), Apps Script v8 endpoint, whitelist v5 fail-open, jsPDF results download.
- Three-gate QC: Gate 1 `tools/riim_audit.py` → Gate 2 content review → Gate 3 live browser check.
