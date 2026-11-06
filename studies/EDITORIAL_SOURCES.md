# Opening scenes

The approved deck contains 43 compositions from 30 found originals, with 13 distinct central photographs. Different materials share one measured circle in each authored profile: historical mathematical and astronomical prints, metal, ceramic, woven fibre, optical glass, microscopy and fossils beside a real photographed horizon. A scene never repeats a motif category.

## The physical curve

Earth scenes register the common curve on the visible opaque Earth or cloud-body boundary beneath the atmospheric envelope. The outer blue halo and upper auroral/airglow ribbons are not the target. Apollo and sunlit Earth use manually inspected native cloud/body anchors, distinct from the rejected outer-halo fits. New ocean and polar photographs and corrected cloud/airglow groups keep their glow above the shared horizon. Native film and cloud transitions are optically soft; fit residuals do not imply subpixel certainty about a physical surface.

Side contours use genuine object silhouettes, engraved circles or architectural boundaries. The ocean/sunlit side-angle errors that crossed engraving texture or missed a ceramic rim were corrected. Natural texture and small physical irregularities remain visible. The proposed Colosseum ground/hatch boundary was rejected in plain-image review and is not an approved composition. The optical-glass source uses a genuine internal circular ridge. Shapes are never stretched or replaced by a circular stencil.

Unresolved dune, ocean-haze and station-aurora registrations are held outside the public rotation. Their sources and prior candidates remain private. Whole neoclassical paintings, Venus/Pythia imagery and koru sources are also retained as reference material where no satisfactory common-curve composition has been established; research references are not automatically approved scenes. Inverted classical paintings and small koru crops that hide the head are not approved.

## Screen profiles and controls

Wide artboards are 1600×960; portrait artboards are 768×1280. One circle and inclination define all three images in a profile. Sources are uniformly scaled, rotated and cropped; portrait phases and radii may differ when the actual measured source span and native coverage permit it. Output densities are limited by original pixels. The viewport covers its artboard uniformly, preserving geometry, and the heading follows the same radius and inclination.

The initial composition holds through captive scrolling, expands and settles once. Returning to the top never reverses consumed progress. Reduced motion opens the settled frame immediately. Compact previous/next angle buttons select complete precomposed scenes at the next distinct angle, wrapping through the available angles. Repeated visits to an angle cycle its available compositions. The shuffle button browses the full deck. Every scene is consumed before a shuffled repeat, consecutive central photographs differ, and different central families appear promptly.

Buttons preserve partial or completed opening progress. A pending change retains the previous complete composition until all three images decode, and a stale image request cannot overwrite a later selection. Keyboard controls, blocked storage and failed image loads recover. Scene-derived asset fingerprints invalidate obsolete photographic crops on deployment. A direct ?study= link selects its first frame, then releases that selection for refreshed visits.

## Source archive and rights

scenes.json records original URLs, rights, credits, SHA-256, source contours and transforms. ATTRIBUTION.txt accompanies each approved group; plates/credits.html lists approved originals once per hash. Derivatives retain applicable source licences. Only approved cropped WebPs are published. Original masters, research contact sheets, rejected candidates, and personal photographs remain in the organised private opening-image library. Raw masters are excluded from its local metadata Git repository; they are not backed up by Git.

## Rebuild and verify

Run `python3 studies/build_catalogue.py` after metadata changes. Build with `python3 studies/build_scenes.py --cache SOURCE_CACHE --scene SCENE_ID`; repeat `--slot` to rebuild only changed layers. The source cache accepts preserved library-relative originals and the earlier research-cache layout. Rebuild credits with `python3 studies/build_credits.py`.

Checks: `python3 studies/check_opening_geometry.py --cache SOURCE_CACHE`, `python3 studies/check_openings.py`, `python3 studies/check_scene_switching.py`, and `python3 studies/check_scene_angles.py`. Source checks cover native density, visible corners and verified empty-black extensions. Browser checks cover desktop, phone, landscape, one-way scrolling, reduced motion, deck exhaustion, keyboard controls, angle wrap, rapid selection and load failures. Physical native-image inspection remains necessary: a small numerical circle residual is not sufficient proof of a correct visible edge.
