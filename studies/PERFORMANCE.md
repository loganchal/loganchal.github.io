# Opening image delivery

The homepage requests one responsive profile and exactly three visible layers.
The browser selects the smallest available resolution sufficient for its canvas
and screen density. The delivery encoder crops hidden pixels from each layer;
its crop widths are recorded as fractions of the original registered canvas.
Rendering uses those fractions to preserve every image's original scale and
position. WebP quality remains 90.

For standard viewports the two side crops end at the authored opening inset
(26% wide, usually 25% portrait), with two source pixels of guard. The centre
retains everything between the final inset boundaries. Gallery cards also use
26%, so wide sides always cover at least that much. A very tall portrait
viewport automatically selects half-width side crops; its centre URL is shared
with the ordinary portrait choice. This does not add requests to a cold frame.
While replacement images load after a resize, the layout clamps its inset to
pixels contained by the current assets. The complete replacement is applied
only after all three images decode.

The loader shares pending image requests across overlapping selections. An
abort cancels only its subscriber; a synchronous replacement can reuse the
same three requests. Completed images are retained in a six-entry decoded
cache, enough for the current and previous frame. Unneeded pending images are
cancelled, failed images can be retried, and the decoded cache stays bounded.

## Measurements

Recorded 6 November 2026 with local Chrome, `apollo-earth`, cold HTTP cache,
4 Mbps download / 80 ms latency. Desktop: 1512×982 at 2×; phone: 390×844 at 2×.
Readiness means all three images have decoded and the opening is enabled.
The final run includes the complete 44-scene catalogue.

| Delivery | Desktop ready | Desktop image bytes | Phone ready | Phone image bytes | Image requests |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original full profiles | 18.626 s | 8,688,128 | 9.871 s | 4,341,586 | 6 |
| First responsive crops | 4.587 s | 1,536,378 | 2.596 s | 581,608 | 3 |
| Crops bounded by visible insets | 3.183 s | 943,836 | 1.978 s | 371,670 | 3 |

The final image transfer is 89.1% smaller on desktop and 91.4% smaller on the
phone than the original. Compared with the first responsive implementation,
this further reduces image bytes by 38.6% and 36.1% respectively. Timing varies
between runs; the byte counts are exact for these choices.

## Reproduce and verify

From the checkout, with the existing Pillow, NumPy, Playwright and Chrome:

```sh
python3 studies/build_delivery.py
python3 studies/build_catalogue.py
python3 -m http.server 8732 --bind 127.0.0.1
# In another shell:
python3 studies/check_scene_performance.py
python3 studies/check_scene_delivery.py
python3 studies/check_opening_geometry.py --cache SOURCE_CACHE
```

`check_scene_performance.py` records timings and screenshots, compares the
rendered initial and resolved frames against complete registered layers at
the same pixel density, checks a 320×1400 portrait fallback, and verifies
cancel/reselect request sharing and zero-request decoded revisits. Crop
encoding changes WebP block decisions; the screenshot comparison therefore
allows mean absolute channel difference below 2.5/255 and fewer than 1% of
pixels with any channel difference above 40. The observed maximum mean was
1.814/255, with 0.483% of pixels above 40. Exact native curve registration is
checked separately by the geometry checker.

The compact receipts are `qa/scene-performance-checks.json` (final run) and
`qa/scene-performance-baselines.json` (earlier runs). Screenshots default to
`/tmp/opening-performance-2026-11-06/verified/`, outside the published site.
