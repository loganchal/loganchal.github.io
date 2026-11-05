# Opening scenes

The approved deck contains 27 compositions from 22 found image sources. Centre panels remain real horizons: Earth’s atmosphere and aurora, ocean/cloud limbs, lunar terrain, a sand crest, and an observed solar limb. Engravings, ceramics, woven fibre, optical glass and microscopy sit beside that horizon. A scene never repeats a motif category.

New Earth additions include two actual Artemis II daylit limbs and a full-resolution Apollo 17 film scan. The selected station-and-aurora image preserves its full native height, including the station above the green and red aurora. Its fitted curve follows the visible atmospheric layer, rather than claiming a geophysical surface measurement. The other new horizons are a White Sands sand/sky crest and the Solar Orbiter visible-light solar limb; its original scientific colour rendering is retained and credited.

Each screen profile defines one target circle and inclination for all three images. Sources are rotated, uniformly scaled and cropped. Their outlines are never stretched, warped or replaced with circular stencils. Source circles come from the actual visible contour: the red bowl uses its physical outer edge, not an interior colour band, and the new compound-eye group uses the corrected celadon rim. Native relief, photographic softness and small engraved irregularities remain visible.

The wide artboard is 1600×960; the phone artboard is 768×1280. Different profile radii and source rotation phases are allowed, while all three images in a profile retain a common circle. The viewport covers the artboard uniformly. Higher-density renders are built from originals without enlarging native pixels. The complete stage and curved heading adapt to viewport dimensions; settled side strips remain visible on tall phones.

Initial panels are held through a captive scroll, then expand and settle. The consumed progress never rewinds on scrolling back to the top. Reduced motion opens the settled frame immediately. The Change scene button preserves current progress. Refreshed visits and the button use the same shuffled deck; central photographs alternate where available, each different centre appears promptly before repeated families, and every scene is consumed before a repeat. A direct ?study= link selects its first frame, then releases that selection for subsequent refreshes. Blocked storage and failed image loads recover without losing the current complete frame.

## Source archive and rights

scenes.json records original URLs, licences, hashes and transforms. Each published scene also has ATTRIBUTION.txt; plates/credits.html provides public credits. CC BY-SA and CC BY-NC-SA derivatives retain their source licences. Only cropped approved assets are published. Full originals and research contact sheets remain in the private organised opening-image library, where the catalogue currently contains 282 public sources. Personal photographs remain private and are not uploaded.

Recorded global black-point adjustments provide the NASA photographic grade and a continuous empty black sky; no luminous limb is cut off. The polarized belemnite uses a recorded adjustment of 22. Its outside source boundary is admitted only where the actual photographed field is black. The unresolved moonlit-ocean and airglow trials, rejected column, duplicate ceramic pairs and mixed Saturn/Earth compositions are excluded from the public catalogue.

## Rebuild and verify

Run `python3 studies/build_catalogue.py` after editing scene metadata. Build a selected scene with `python3 studies/build_scenes.py --cache SOURCE_CACHE --scene SCENE_ID`. The source resolver accepts either the scratch layout or the preserved private library root.

Run `python3 studies/check_opening_geometry.py --cache SOURCE_CACHE`, `python3 studies/check_openings.py`, and `python3 studies/check_scene_switching.py`. Geometry checks use source pixels and visible panel corners; browser checks cover large desktops, phones, landscape, one-way scrolling, reduced motion, deck exhaustion, keyboard controls and image-load recovery. Receipts are in studies/qa.
