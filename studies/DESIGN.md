# Photographic opening

The opening is one composition with one geometric curve, not independently curved cards. All source photographs are registered to the same circle in a 1600 × 960 artboard: radius 2250, centre (800, 2758.8). The photographed contours, including their tangents, must continue through each seam as the centre panel expands.

Only translation, rotation and uniform scale are allowed. Never distort an image, draw a replacement silhouette, or mask an object to a manufactured curved edge. Rectangular panel crops are allowed. The Artemis photographs have a global black-point adjustment; its lunar edge is untouched.

The fixed-ratio artboard is uniformly scaled and cropped as one unit at every viewport size. Panel expansion changes rectangular clipping only. Do not switch back to independently covering each viewport-sized panel: that changes which unverified portions of the side photographs are exposed.

Use original photographs and archival materials. Do not generate imagery. Source dimensions alone are insufficient: inspect the actual final crop at native Retina size. `build_registered.py` refuses enlargement at the 3840 × 2304 output size. Exact inputs, transforms, hashes and credits are in `registration.json`; measured contour points and browser checks are in `qa/`.

Only accepted compositions enter `shuffle.js` or the studies gallery. There are two accepted compositions: Earthset and the film-grained eclipse. The eclipse ends at a 10% artboard inset so its entire visible edge stays within the original camera frame. Older experiments are not selectable. Broader source discovery belongs in the separate image library and does not imply a successful opening composition.

Intro progress is monotonic. After completion, consume the scroll runway and retain the expanded image on return to the top. Reduced motion opens immediately.

Original downloads remain outside Git; retrieve them from the URLs in `registration.json`. The large museum TIFF is deliberately excluded. Build with Pillow and NumPy via `python3 studies/build_registered.py --sources /path/to/originals`.

Responsive layout: the heading and links are positioned relative to the rendered horizon (`--horizon-y`), accounting for the shared artboard crop. Short landscape viewports use a horizontal research menu. The stage and scroll runway follow the dynamic viewport height. Portrait screens use a separately registered 768 × 1280 artboard, retaining visible side panels. Every photograph is still uniformly scaled and rotated onto the same circle.

Typography follows a parallel arc derived from the image registration radius. Its baseline is positioned optically above Earth or the eclipse glow. A fine stationary grain layer joins the photographed fields and lettering; it does not blur the source photographs or change their edges. Portrait and landscape profiles are recorded in `registration.json` and rebuilt by `build_registered.py`.

The current captive opening uses a 280dvh section: 180dvh of scroll is consumed while the stage remains pinned. Initial composition holds for the first 10% of that runway, expands through 78%, then holds the resolved frame until release. Typography and gutters are shared root tokens in home.css. The direct skip link bypasses the sequence.
