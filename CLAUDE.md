# RezFlo Video Studio

Workspace for RezFlo ad videos made with HyperFrames (HTML + GSAP → MP4). Owner: Yunis, founder of RezFlo. He's not a video editor: explain in plain words, show a plan before big changes, and render drafts before finals.

## RezFlo in one paragraph

RezFlo is an AI phone receptionist for restaurants. It answers every call, takes reservations and orders, and never puts anyone on hold. Target: GTA restaurant owners who are busy, understaffed, and missing calls during the dinner rush. Pricing is $149 to $299/month CAD, no contracts. Site: rezflo.ca (a redesign is planned). Ads run on Meta (lead gen) and TikTok (organic).

## Ad rules

- Hook in under 3 seconds. One pain point per ad. One call to action per ad.
- Casual and direct, the way Yunis talks. Short sentences, specific numbers.
- Banned words: solution, leverage, streamline, innovative, cutting-edge, elevate, supercharge, unlock.
- Don't invent stats, testimonials or results. Placeholder numbers must be flagged to Yunis as placeholders. The opener's "20 calls × $50 = $1,000" is a placeholder from the ad playbook, not measured data.
- Meta CTA: "Fill out the form below" or a free call audit. TikTok organic CTA: "Comment DEMO" or "Follow for more", never a link.

## Brand

Use the PROMPT 15 style block in `prompts.md` for every video. Short version:
- Background #0b0a12, purple glow #1d1638. Brand purple #5b41da for fills; #8f7bff for purple text on dark.
- Red #ff5a5f only for missed calls / lost money. Green #34c759 only for answered calls / ticks.
- Fonts in `kit/fonts`: Space Grotesk Bold (headlines), Inter (UI), JetBrains Mono (labels, times, numbers).
- Logo: use the files in `brand/` (SVG preferred, `*-on-dark` versions for dark frames). Never redraw it or use a placeholder mark. See `brand/README.md`.
- Vertical 1080x1920, 30 fps. Text inside the middle 80% of the width. Bottom 20% stays clear for captions and app UI.

## Folder map

- `prompts.md`: every prompt. 01–14 are from Damiano's motion graphics kit; 15–19 are the RezFlo additions. Read the "RezFlo additions" note at the top for run order.
- `opener/`: finished 15-second RezFlo cold open (HyperFrames project). `index.html` holds the whole timeline; scenes are commented with their time ranges.
- `renders/rezflo-opener.mp4`: the current render of the opener.
- `kit/`: fonts, sfx (9 code-made sounds, free to use in ads), practice clip and practice screenshots.
- `brand/`: the RezFlo logo (vector remake, light and dark versions).
- `raw/`: Yunis drops raw phone recordings here. Git ignores its contents, so recordings stay local.
- `.claude/skills/brag` and `brag-slim`: the /brag skill, vendored from latent-spaces/brag v0.4.0. See `.claude/skills/VENDORED.md` to update it.

When starting a new video, make a new folder next to `opener/`, copy `kit/fonts` and `kit/sfx` into it, and work there. Don't edit `opener/` unless asked.

## Workflow

- Talking-head ad: PROMPT 16 (cut + captions, show the cut list and wait for OK) → PROMPT 11 + PROMPT 15 → PROMPT 12 for the key moment → PROMPT 13 → PROMPT 19 to put the opener in front.
- Standalone motion piece: PROMPT 17 (opener) or PROMPT 18 (product demo) with PROMPT 15 underneath.
- Launch video from the website: the /brag skill (already in this repo) (`/brag https://rezflo.ca --format vertical --tone polished`). Wait for the site redesign before using it for anything final. Check the music license before using a /brag track in a paid ad.

## Before saying a video is done

1. `npx hyperframes check` passes with no errors.
2. Pull frames at the key moments with ffmpeg and look at them: nothing cut off, overlapping, or hard to read.
3. Draft renders: `--quality draft`. Final ad exports: `--quality delivery`.

## Known issues

- If the render fails because Chrome won't download, point HyperFrames at a Chrome already on the machine with the `HYPERFRAMES_BROWSER_PATH` environment variable.
- The opener loads GSAP from a local `gsap.min.js` so it renders offline. Keep it that way.
- Speech-to-text timings can be up to a second off. When a graphic lands early or late, sync it to the spoken word, not a timestamp.
