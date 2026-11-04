# Photographic opening

The opening is one composition with one geometric curve, not independently curved cards. All source photographs are registered to the same circle in a 1600 × 960 artboard: radius 2250, centre (800, 2758.8). The photographed contours, including their tangents, must continue through each seam as the centre panel expands.

Only translation, rotation and uniform scale are allowed. Never distort an image, draw a replacement silhouette, or mask an object to a manufactured curved edge. Rectangular panel crops are allowed. The Artemis image has a global black-point adjustment; its lunar edge is untouched.

The fixed-ratio artboard is uniformly scaled and cropped as one unit at every viewport size. Panel expansion changes rectangular clipping only. Do not switch back to independently covering each viewport-sized panel: that changes which unverified portions of the side photographs are exposed.

Use original photographs and archival materials. Do not generate imagery. Source dimensions alone are insufficient: inspect the actual final crop at native Retina size. `build_registered.py` refuses enlargement at the 3840 × 2304 output size. Exact inputs, transforms, hashes and credits are in `registration.json`; measured contour points and browser checks are in `qa/`.

Only accepted compositions enter `shuffle.js` or the studies gallery. There is currently one accepted composition. Older experiments are not selectable. Broader source discovery belongs in the separate image library and does not imply a successful opening composition.

Intro progress is monotonic. After completion, consume the scroll runway and retain the expanded image on return to the top. Reduced motion opens immediately.

Original downloads remain outside Git; retrieve them from the URLs in `registration.json`. The large museum TIFF is deliberately excluded. Build with Pillow and NumPy via `python3 studies/build_registered.py --sources /path/to/originals`.

Responsive layout: the heading and links are positioned relative to the rendered horizon (`--horizon-y`), accounting for the shared artboard crop. Short landscape viewports use a horizontal research menu. The stage and scroll runway follow the dynamic viewport height. Portrait screens reframe the same uniformly scaled artboard around Artemis; no panel is independently stretched.
