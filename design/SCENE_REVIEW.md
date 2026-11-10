# Opening scene reviewer

`/scene-review/` provides drag/swipe, keyboard and button voting. Right keeps, left rejects; Space skips and Z undoes. The default queue contains unreviewed live scenes. Kept, rejected and all-scene filters allow revisits; an explicit checkbox includes archived scenes.

The iframe renders the production homepage with a review-only flag. Its artwork uses the same responsive delivery, radius, tilt, crop and frame functions as the site. The reviewer scales a real desktop or phone viewport uniformly, and can show the opening crop or expanded framing. Site navigation is hidden only within the review preview. A requested scene must actually load before it can be rated. Review visits do not consume the homepage shuffle deck.

Decisions and undo history are stored locally under `opening-scene-review-v1`. JSON export/import supports continuing on another browser and later curation by scene ID. Decisions include time, viewport, frame and a render fingerprint; changed renders return to the unreviewed queue without discarding their earlier record. The page does not change the live rotation or send votes to a server. No actual user decisions are committed to Git.

The homepage angle arrows and numeric angle output were removed. Shuffle and scene count remain.

Validation: `python3 scripts/check_scene_review.py --base-url http://127.0.0.1:8742` checks a real horizontal drag, button and keyboard votes, undo, persistence, JSON import/export, the two framing modes, Te Reo, mobile width and absence of angle controls. Outputs go to a temporary directory or `--output`. Chrome and Playwright are required. Completed-deck and revisit behaviour were also checked in the browser.
