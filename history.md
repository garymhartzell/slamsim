# SlamSim! Development History

This document tracks the major changes, new features, and bug fixes for the 1.0 version of SlamSim!.

---

## v1.0 Beta 1 (2025-10-14)

This first official beta has two new features and several bug fixes. Next, I'll start working on the AI match writer.

### New Features

- In Booker Mode, you can now filter out events, wrestlers, and tag-teams by status (Inactive, Active, etc. for wrestlers and tag-teams, Past, Future, and Canceled for events).
- In Booker Mode, before you finalize an event, warnings about inconsistancies (unequal sides, incorrectly tagged winners or losers, etc.) are displayed for your attention. You can either go back and fix them or choose to ignore them and publish anyhow.

### Bug Fixes

- Fixed a bug in the fan route that was preventing viewing of belts.
- Fixed a bug where match_result_display changes were not being saved.
- Fixed a sorting bug on the fan.roster page.
- Fixed a bug where match_class was not being updated dynamically in the segments builder.
- Fixed a bug in the segments builder where participants_display was not showing tag-teams and individual wrestlers correctly in multi-person matches.
- Fixed a couple of bad url_for strings in fan.home.

## v1.0 Alpha 4 - Fan Mode Completion & Engine Overhaul (2025-10-01)

This is the final and largest alpha release, preparing the application for its beta phase. This version introduces the complete "Fan Mode," a full-featured, read-only view of the promotion designed for an audience. It also includes a major overhaul of the core booking engine, focusing on data integrity, narrative control, and professional-grade administrative tools.

### New Features: The Complete Fan Mode

The application now has a fully realized "Fan Mode," a complete front-end experience for the wrestling promotion.

- Homepage: A customizable homepage that aggregates content, including latest news, upcoming/recent events, and a list of current champions.
- Championship Section: A dedicated champions list page that displays all belts and their current holders (with tag team members expanded). Each championship links to a detailed, chronological history page showing every title reign.
- News System: A complete news section with a main page for recent articles and yearly archives, allowing fans to follow the narrative of the promotion.

### Booking Engine & Data Integrity Overhaul

- **Match Finish System:** The segment editor has been completely overhauled. It now includes a detailed "Match Finish & Presentation" section with options for "Method of Victory" (Pinfall, Submission, etc.) and a comprehensive "Match Outcome" dropdown that properly handles draws and no contests.

- **Narrative Control:** The match_result string is now an intelligent, narrative-driven sentence that correctly reports on title changes (e.g., "...to become the new World Champion") and successful defenses.

- **Conditional Deletion:** Deletion logic has been hardened across the entire application. Entities that are part of the historical record (e.g., a wrestler with a match, a belt with a reign history, a finalized event) can no longer be deleted, protecting data integrity.

- **Architectural Improvements:** Added a Display_Position to Divisions and Belts for custom sorting and a Division_Type to Divisions to enforce correct entity assignment.

### Bug Fixes

- Critical Fix: Corrected the event finalization logic to ensure individual wrestlers' Tag_Wins and Tag_Losses are properly updated when their tag team competes in a match.
- Resolved multiple critical bugs related to file generation, template rendering, and JavaScript functionality that were causing application crashes and a

## v1.0 Alpha 3 - Introducing Fan Mode (2025-09-23)

This release marks the official debut of "Fan Mode," providing the first public-facing views of the promotion. This version establishes the architectural foundation for the fan experience and introduces the initial Roster and Events pages. Additionally, this version includes critical bug fixes to the core simulation engine, ensuring greater data integrity for wrestler and tag team records.

### New Features: The Fan Mode Experience

* **Architectural Foundation:** Implemented a new two-tiered base template system (`_booker_base.html`, `_fan_base.html`) to create a distinct look and feel for each mode while maintaining a shared core structure and navigation.
* **Fan Mode Roster Page:** Created the initial Fan Mode Roster page (`/fan/roster`), which correctly groups active wrestlers and tag teams by their assigned division. The page fully implements all user-configurable sorting options: Alphabetical, Total Wins, and Win Percentage (with a 5-match minimum qualifier).
* **Fan Mode Events Pages:** Built the main Fan Mode Events Index (`/fan/events`), which displays "Upcoming Events" and "Recent Results" sections based on user preferences.
* **Yearly Event Archives:** The Events Index now links to new yearly archive pages (e.g., `/fan/events/2025`) to provide a clean, organized view of the promotion's history.

### Bug Fixes & Stability Improvements

* **Critical Fix:** Corrected the event finalization logic to ensure individual wrestlers' `Tag_Wins` and `Tag_Losses` are properly updated when their tag team competes in a match.
* Resolved an issue where tag teams were not being sorted correctly in the Booker Mode participant builder.
* Further hardened the application by making win/loss records read-only in the UI and implementing conditional deletion logic to protect historical data.
* Improved data integrity by adding a "Division Type" (Singles/Tag-Team) to divisions, ensuring entities can only be assigned to the correct type of division.

## v1.0 Alpha 2 - Championship Update (2025-09-08)

This is a major feature release that moves SlamSim! from a collection of CLI scripts to a fully functional web dashboard. This release also introduces a complete, automated championship tracking system and numerous quality-of-life improvements. The application now functions as a true wrestling simulator, where match outcomes have a direct and permanent impact on statistics and title lineages.

### New Features & Major Changes

* **Web Dashboard:**

* Created a web UI using Python's Flask and Jinja2 modules for a complete menu-driven dashboard of features.
* All data is now created in the dashboard instead of manually needing to generate JSON files.

* **Championships (Belts) Management:**
    * Added a full CRUD (Create, Read, Update, Delete) interface for managing championships.
    * Belts can be designated for "Singles" or "Tag-Team" holders.
    * The current champion can be assigned directly from the Belts editor.

* **Championship History Tracking:**
    * The application now maintains a permanent record of all championship reigns in `data/belt_history.json`.
    * A "History" page for each belt displays a chronological list of every champion, including dates won/lost, reign length in days, and successful defenses.
    * Reign history can be manually created, edited, and deleted for full control over a title's lineage.

* **Event Finalization ("The Event Runner"):**
    * Introduced a new "Finalize Event" process for events with a "Past" status.
    * Finalizing an event is an irreversible action that locks the event card and automatically updates all official records.
    * **Automatic Record Updates:** The runner processes all match results, updating win/loss/draw records for every wrestler and tag team involved. It correctly distinguishes between singles and tag match records for individual wrestlers.
    * **Automatic Title Changes:** The runner automatically processes championship matches, updating the `Current_Holder` on the belt, writing new entries to the title's history log, and updating the `Belt` field on the wrestler/tag team's profile.
    * **Successful Defenses:** The runner automatically increments the "Defenses" count for a champion who successfully retains their title.

### UI/UX Improvements

* The "Belt" field in the Wrestler and Tag Team editors has been replaced with a dynamic dropdown menu populated by active championships.
* The Segment Editor's match builder now displays the current champion when a title is selected.
* The Events list is now sorted in reverse chronological order (most recent first).
* The Wrestlers and Tag Teams lists are now sorted alphabetically.
* The Tag Teams list has been streamlined to remove win/loss stats for a cleaner look.
* Added an "Exit" option to the main menu that leads to a goodbye page.

### Bug Fixes

* Resolved numerous critical bugs in the Segment Editor's JavaScript, restoring full functionality to the dynamic participant builder and results sections.
* Corrected data loading issues that prevented newly created entities from appearing in lists.
* Fixed various structural and logical errors in backend routes and templates.

## v1.0 Alpha 1 (2025-04-29)

This is the initial alpha release of SlamSim!, a wrestling league simulator. 

* Static web pages can be generated for wrestlers, tag-teams, divisions, events, matches, and news.
* Web pages include roster lists, events list, and upcoming events, as well as detailed wrestler and tag-team biographies.

## Future Plans

* Bring back publishing of static web pages.
* AI match and segment writer.
* AI match booking assistance.
* The ability to handle multiple leagues.

