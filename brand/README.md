# RezFlo logo

Vector remake of the RezFlo logo, traced from the original and fitted to it pixel by pixel (average difference under 0.6% at the original size). All lettering is converted to shapes, so the files need no fonts.

| File | Use |
|---|---|
| `rezflo-logo.svg` / `.png` | Stacked logo (mark over wordmark), light backgrounds |
| `rezflo-logo-horizontal.svg` / `.png` | Mark beside wordmark, light backgrounds (lower thirds, headers) |
| `rezflo-mark.svg` / `.png` | The R on its own (app icon, avatar, watermark) |
| `*-on-dark.svg` / `.png` | Same three, recoloured for dark backgrounds |

PNGs are 2048px wide with transparent backgrounds. Prefer the SVGs.

## Colours

| | Light backgrounds | Dark backgrounds |
|---|---|---|
| Front lane of the R + wordmark | `#5B4BCE` (purple, measured from the original) | `#6D5CF0` (purple lane) / `#F3EFE6` (wordmark) |
| Back lane of the R | `#737373` (grey) | `#B9B7C6` (light grey) |

The video brand purple in `CLAUDE.md` is `#5b41da`, a touch redder than the logo's `#5B4BCE`.

## How the mark is built

One ribbon traced twice side by side, purple inside and grey outside: a detached slash at the top-left, the top bar, a half-circle bowl, the middle bar, then the leg. Rules:
- Every diagonal cut shares one angle (slope 0.624, about 32° from vertical).
- The bowl is three concentric circles (radii 4.62, 10.87, 15.5), so each lane keeps one width all the way round, and the leg uses the same widths.
- The slash's purple/grey split is the only off-axis line.

Wordmark: Poppins SemiBold (SIL Open Font License), converted to outlines.

`source/` holds the generator (`build2.py` + `fit2.json`, needs `fontTools`, `cairosvg` and Poppins-SemiBold.ttf) and a side-by-side with the original.
