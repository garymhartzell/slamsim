# SlamSim! Development History

This document tracks the major changes, new features, and bug fixes for the 1.0 version of SlamSim!.

---

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

