# Editorial opening scenes

The opening is a found-image composition. Each group has one circle and inclination across its three real contours. Only rotation, uniform scaling, cropping and the recorded NASA black-point adjustment are used. A circle in the configuration is not evidence that the photographed edge follows it: inspect the actual visible joins at initial and settled panel positions, on wide and portrait layouts.

Four additions extend the two existing ink/glaze/eclipse groups:

| Scene | Images | Artboard radius | Inclination | Render density |
| --- | --- | ---: | ---: | ---: |
| prism-eclipse | Umpqua Fresnel glass / Artemis II eclipse / red porcelain | 1900 | −3° | 2.3× |
| porcelain-earth | red porcelain / Artemis II Earthset / Cellarius engraving | 1990 | +3° | 2.4× |
| woven-earth | Timbisha Shoshone woven bowl / Artemis II Earthset / red porcelain | 2100 | −8° | 2.28× |
| night-gradient | Cellarius engraving / ISS sunrise above Brazil / red porcelain | 2000 | 0° | 2.3× |

The wider sources remain in `scenes.json`: original URLs, attribution, rights and hashes accompany each new asset. Full TIFFs and NASA originals stay in the source cache rather than Git. `plates/credits.html` carries public credits, including CC BY-SA 2.0 for Kristina D.C. Hoeppner's glass photograph and its cropped derivatives. Other new object photographs are Cleveland Museum of Art CC0; NASA usage follows its media guidelines.

The photographic inputs are independently registered for 1600×960 and 768×1280 artboards. The whole artboard covers the viewport uniformly. Settled panels retain a visible side strip even when the artboard is cropped by a tall viewport. Higher-density renders never enlarge the native source. Different output densities respect each original's detail while retaining the same CSS sizing.

## Physical-edge correction

The first red-porcelain measurement used R−G > 25, which selected an interior colour band. That produced a visible step despite the configured circles matching. It was removed from rotation and replaced by a fit to the visible outer transition (R−G > 4), then checked against actual rendered Moon/red joins. The fitted source radius changed from roughly 5410 to 4796 pixels. The woven group therefore uses radius 2100 and 2.28× output. Its actual rendered step is about 1.75 artboard pixels on both profiles; natural photographic and lunar relief boundaries are not mathematically perfect lines.

Earthset was reframed through the same circle-preserving transform so the Earth stays clear of the initial mobile panel edge. Naturally black sky in the ISS photo continues onto the black stage; its gradient, city lights and limb remain original photography.

## Rebuild and validate

With originals at their `source_file` paths relative to the cache root:

```sh
python3 studies/build_scenes.py --cache /path/to/cache --scene prism-eclipse --scene porcelain-earth --scene woven-earth --scene night-gradient
python3 studies/check_opening_geometry.py --cache /path/to/cache
python3 studies/check_openings.py --url http://127.0.0.1:8732
```

The checks record source coverage, native pixel density, contour residuals, browser asset loading, responsive overflow, one-way scroll, reduced motion and shuffled visits in `studies/qa/`. Source contours and sampled points are in `studies/qa/editorial-contours/`.

The automatic deck excludes the older space-with-space compositions; their direct `?study=` links remain usable. The deck refreshes when its active catalogue changes, exhausts each shuffled set before repeating, and prevents adjacent repeats at a deck boundary.

## Historical chart addition

`lion-dawn` pairs the La Hire lion-and-stars engraving with the orbital sunrise and celadon glaze: radius 2300, inclination +2 degrees, settled inset 20%, native render density 2.4. Its original engraved band is measured at 25 native-pixel points, with all points retained; the sampled line-center fit has about 0.48 artboard-pixel RMS and 1.43 maximum deviation. The finite printed line is preserved. The images receive only rotation, uniform scale and cropping; no circle is drawn over them. Chart derivatives use CC BY-NC-SA 3.0 according to the source collection.

Opening selection excludes exposed breasts and full classical nudity. The Bouguereau and Galatea research trials are excluded; originals remain private research references. Manuscript diagrams, Galatea silhouette, broad downward-Earth curves and Piranesi trials that fail native-resolution/contour inspection are not promoted into the rotation.
