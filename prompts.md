# Motion Graphics with Claude Code · prompts

Every prompt from the PDF, same numbers. Copy from here, not from the PDF: PDFs break quotes and line breaks.

Before a project: copy the kit's fonts folder into it (and sfx for PROMPT 13). Every prompt here was run and its output checked before it went in the guide.

> **RezFlo additions (PROMPT 15 to 19, at the bottom).** Order for a talking-head ad:
> PROMPT 16 (cut + captions) → PROMPT 11 with the PROMPT 15 style block under it → PROMPT 12 for the one key moment → PROMPT 13 (sounds) → PROMPT 19 (put the opener in front).
> For a standalone opener or product clip: PROMPT 17 or 18, with PROMPT 15 under it.

## PROMPT 01 · Setup

Paste once, in any folder. Restart Claude Code when it's done.

```
Set up this computer so I can make videos with HyperFrames. First work out if I'm on a Mac or on Windows, then:

1. Check I have Node.js 22 or newer. If not, install it (Homebrew on Mac, winget on Windows).
2. Check I have FFmpeg. If not, install it the same way.
3. Check I have whisper-cpp, which turns speech into timed text. If not, install it (Homebrew on Mac; on Windows use the latest release from github.com/ggml-org/whisper.cpp and add it to PATH).
4. Install the HyperFrames skills for Claude Code with npx hyperframes skills.
5. Run npx hyperframes doctor and read the result.

Ignore anything doctor calls optional (Docker, Kokoro, MusicGen). If something needs my password or admin rights, stop and give me the exact command to run myself.

When you're done, tell me in plain words: what was already there, what you installed, and anything I still need to do.

If rendering fails because Chrome can't be downloaded, don't keep retrying. Find a Chrome or Chromium that's already on this computer, point HyperFrames at it with the HYPERFRAMES_BROWSER_PATH environment variable, and try again.
```

Windows note: the original setup was only tested on a Mac. If `node` or `ffmpeg` isn't found right after installing, close the terminal, open a new one, and start Claude Code again.

## PROMPT 02 · Your first render

New empty folder, start Claude Code there, paste.

```
Make me a 6-second video with HyperFrames in this folder, 1920x1080 at 30 fps.

One white frosted-glass card in the middle of a soft purple-to-blue gradient background. On the card: a small grey label that says MY FIRST RENDER, a big number that counts up from 0 to 100, and a green pill that says Made with Claude Code.

The card rises in at the start. The number counts up over 2 seconds. The green pill pops in at 4 seconds.

Use the Inter font. Render it to renders/first.mp4 and tell me where the file is.
```

## PROMPT 03 · The 10 moves demo

New empty folder. Gives you a 14-second video of every move on page 7.

```
Make a 14-second demo video with HyperFrames in this folder, 1080x1920 at 30 fps, that shows 10 animation moves one after another, about 1.3 seconds each. Each move animates a simple white card on a dark background, with the name of the move written small above it. In this order:

1. Rise: the card fades in while moving up 40px.
2. Pop: the card scales from 0.6 to 1 with a little overshoot.
3. Count-up: a number rolls from 0 to 500.
4. Checklist tick: three lines get a green tick, one after the other.
5. Typewriter: a sentence types itself letter by letter.
6. Slide-in: the card slides in from the right.
7. Blur-in: the card goes from blurry to sharp.
8. Punch-in: the whole frame zooms in 15% fast, then holds.
9. Reframe: a full-screen panel shrinks into a rounded card in the bottom half while a new card appears on top.
10. Bar fill: a progress bar fills from 0 to 100%.

Render to renders/moves.mp4.
```

## PROMPT 04 · Style · Kinetic Type

Paste under PROMPT 08, 09, 10 or 11. Copy the kit's fonts folder into your project first.

```
STYLE: Kinetic Type
- The text is the whole video. No cards, no boxes.
- Font: Archivo Black (fonts/ArchivoBlack-400.woff2), all caps, huge. The main word fills most of the width.
- Colours: black background, white text, one accent colour #c6ff3d for the most important word on each screen.
- Motion: words slam in one by one, fast and snappy (power4.out, 0.25 to 0.4 seconds). Mix the moves: slide in from the side, stretch from squashed to full height, split the letters apart and back together. Each screen exits fast before the next one hits.
- Cut the screens on the rhythm of the words, like a beat.
```

## PROMPT 05 · Style · Liquid Glass

Paste under PROMPT 08, 09, 10 or 11. Copy the kit's fonts folder into your project first.

```
STYLE: Liquid Glass
- Frosted glass cards: white at about 80% opacity, 30px background blur, thin white border, big rounded corners (32px), soft shadow.
- Background: soft light gradient with two or three blurred colour blobs (pale blue, lilac, peach) drifting slowly.
- Font: Inter (fonts/Inter-700.woff2 for headings, fonts/Inter-400.woff2 for small text). Dark grey text #1d1d1f, small uppercase grey labels above headings.
- Accent: green #34c759, only for ticks and checks.
- Motion: calm and smooth. Cards rise 30px and fade in with power3.out over 0.6 seconds, scaling up slightly from 0.96. Text arrives piece by piece. Nothing bounces.
```

## PROMPT 06 · Style · Editorial Grain

Paste under PROMPT 08, 09, 10 or 11. Copy the kit's fonts folder into your project first.

```
STYLE: Editorial Grain
- It should look like a printed magazine page, not a screen.
- Background: warm paper colour #efe8dc with visible film grain over everything (an animated SVG noise layer at about 12% opacity).
- Font: Instrument Serif (fonts/InstrumentSerif-400.woff2 and fonts/InstrumentSerif-400-italic.woff2) for headlines, large, mixing upright and italic words. Small labels in Inter (fonts/Inter-400.woff2), uppercase, letter-spaced.
- Colours: ink black #1a1a1a and one deep red accent #c2412d.
- Shapes: cut-out paper rectangles behind key words, slightly rotated (1 to 3 degrees), thin rules, and small page numbers in the corners.
- Motion: unhurried and a bit imperfect. Staggered timings that are not perfectly even, gentle slides and wipes, no bounces.
```

## PROMPT 07 · Style · Pop Bold

Paste under PROMPT 08, 09, 10 or 11. Copy the kit's fonts folder into your project first.

```
STYLE: Pop Bold
- Loud, playful, flat colour. No gradients, no glass.
- Font: Bricolage Grotesque ExtraBold (fonts/BricolageGrotesque-800.woff2), big and chunky.
- Colours: flat blocks of #c6ff3d (lime), #8a3cff (purple), #ff4fd8 (pink) and #111111, with 4px black outlines and hard 8px offset shadows with no blur.
- Extras: rotating star and circle stickers, little arrows, a few simple shapes drawn in CSS.
- Motion: bouncy and springy. Things pop in with back.out(2.5), overshoot, wobble a little, squash and stretch. Stickers spin slowly the whole time.
```

## PROMPT 08 · Text-only video

Swap the script for yours. Add a style block underneath, or don't. Copy the kit's fonts folder into your project first.

```
Make a 15-second vertical video (1080x1920, 30 fps) with HyperFrames in this folder, made only of animated text. No footage.

Script:
Most product videos lose people in 2 seconds. Here's how to keep them. Show the result first. Cut every pause. One idea on screen at a time. Then tell them what to do next.

Use my exact words. Don't rewrite or shorten the script. Show one sentence per screen, big enough to read on a phone. If a sentence is long, wrap it over two or three lines on the same screen. Each screen stays up long enough to read. Keep all text inside the middle 80% of the width so phones don't crop it. If there is a STYLE section below, follow it. If not, use clean white frosted cards on a soft light gradient, with the Inter font.

Render to renders/text.mp4.
```

## PROMPT 09 · Product video

Swap Tally and the three features for your product, and give it your real numbers. Drop a product.png in the folder if you have one.

```
Make a 12-second product launch video with HyperFrames in this folder, 1920x1080 at 30 fps.

The product is Tally, an app that shows what your online shop really earns after fees. If there is a product.png in this folder, use it as the hero image. If not, build the product in HTML and CSS (an app screen, a logo, or a phone with the app on it).

Structure:
1. 0 to 2 seconds: the logo or product name is revealed.
2. 2 to 9 seconds: three feature moments, one at a time. Each one shows the product doing the thing, not just a sentence. Features: connects to your store in one click / shows profit after fees, ads and refunds / sends you one number every morning.
3. 9 to 12 seconds: end card with the product name, one short line and a call to action: Join the waitlist.

If there is a STYLE section below, follow it. If not, use clean white frosted cards on a soft light gradient.

Render to renders/product.mp4.
```

## PROMPT 10 · SaaS promo

Put screenshots of your app in a folder called screenshots. Swap Tally and the one-line description for yours.

```
You're an amazing motion graphics designer. Make a 1-minute promo video for my SaaS with HyperFrames, in this folder, 1920x1080 at 30 fps.

The product is Tally, an app that shows online shops what they really earn after fees, ads and refunds. The screenshots folder has real screens from the app.

1. Look at every screenshot first and work out what each one shows.
2. Build the video around them. Open with a short hook, then show each screen and zoom into the part that matters (the number, the chart, the button) with a short line of text that says what it does for the customer.
3. Use the screenshots as they are. Don't redraw them.
4. Kinetic style: fast zooms and pans into the screenshots, big bold words between the screens, cuts on a steady beat.
5. End on the logo, one short line and a call to action: Start your free trial.

Render to renders/promo.mp4.
```

## PROMPT 11 · Motion graphics on your own video

Put your video in the folder as clip.mp4 (or use the practice clip from the kit). Copy the fonts folder in too.

```
You're a top motion graphics designer. Add motion graphics to my video clip.mp4 with HyperFrames, in this folder.

1. Really analyse the video first. Transcribe it with npx hyperframes transcribe, check the word timings against the audio, and work out what the video is about and which moments matter most. If whisper isn't installed, stop and tell me to run the setup prompt.
2. Keep my video exactly as it is: same size, frame rate, audio and cut. You only add graphics on top.
3. At each important moment, add an animation made for what I'm saying right then: a number becomes a counter, a list becomes a checklist, a before and after becomes a comparison. Each one starts on the exact word.
4. Keep one style across the whole video, so it looks designed, not random.
5. Nothing in the first 3 seconds. That's the hook.
6. Keep graphics off my face, out of the bottom third where captions go, and away from the left and right 10% of the frame.

If there is a STYLE section below, follow it. If not, use clean white frosted cards.

Render to renders/with-cards.mp4.
```

## PROMPT 12 · Fix one spot

Run after PROMPT 11. Put your screenshots in a folder called screenshots and change the sentence to the words you actually say.

```
Now one spot. When I say Sales went from 40 a week to over 90, show the 5 screenshots in the screenshots folder popping up one after another, in order. Cut them in a way that matches the video and keep them in sync with my voice. Keep everything else exactly the same and render again to renders/with-cards.mp4.
```

## PROMPT 13 · Sound effects

Copy the sfx folder from the kit into your project first. Run after PROMPT 11.

```
Add sound effects to this video using the files in the sfx folder. A tick when each list item or check appears, the counter sound while a number rolls, and the chime on the last card. No sound when a card slides in or leaves, and no whooshes. Keep the effects quiet under my voice. Render again to renders/with-cards.mp4.
```

## PROMPT 14 · Transparent export

Run in any finished project. For putting your animation over footage in Premiere or After Effects. Frosted-glass cards go flat with nothing behind them, so switch overlays to solid cards first (PROMPT 15 already uses solid cards).

```
Remove the background so only the card is visible, with everything around it transparent. Then export a transparent version I can put over my own footage in Premiere or After Effects: renders/card.mov (ProRes 4444 with alpha) and a PNG sequence in renders/card-png.
```

## Change anything (page 6)

Say these in the same Claude Code session, after a render. Each one was tested on the PROMPT 02 video.

- Change the card from frosted glass to a solid purple-to-pink gradient card with white text. Keep everything else the same and render again to renders/first.mp4.
- Use my brand colours: background #111111, card #ff5a1f, text white. Keep everything else the same and render again to renders/first.mp4.
- Switch the number to a serif font (Instrument Serif from Google Fonts) and make it 30% bigger. Keep everything else the same and render again to renders/first.mp4.
- Make every animation bouncier, with a bit of overshoot. Keep everything else the same and render again to renders/first.mp4.
- Make the green pill appear at 2 seconds instead of 4. Keep everything else the same and render again to renders/first.mp4.
- Move the card to the top-left corner and make it 20% smaller. Keep everything else the same and render again to renders/first.mp4.

## Export cheat sheet (page 18)

You can just ask Claude (render it in 4K at 60 fps), or run these yourself in the project folder:

```
npx hyperframes render . --fps 60 -o renders/video-60fps.mp4
npx hyperframes render . --resolution 4k -o renders/video-4k.mp4
npx hyperframes render . --resolution 4k --fps 120 -o renders/video-4k-120.mp4
npx hyperframes render . --format mov -o renders/video.mov
npx hyperframes render . --format png-sequence -o renders/frames
npx hyperframes render . --fps 24 -o renders/video-24fps.mp4
npx hyperframes render . --crf 23 -o renders/smaller.mp4
```

MOV and PNG are only transparent if the background is transparent. Run PROMPT 14 first.

Use `--quality delivery` for the final ad export, and `--quality draft` while you're still changing things (much faster).

Made by Damiano · instagram.com/damianodesu


---

# RezFlo additions

Written for RezFlo ads: vertical 1080x1920, Meta lead gen and TikTok. Copy the kit's `fonts` and `sfx` folders into every project.

## PROMPT 15 · Style · RezFlo

Paste under PROMPT 08, 09, 10, 11, 17 or 18. This keeps every RezFlo video looking like the same brand.

```
STYLE: RezFlo
- Dark and clean, like a phone screen at night. Background #0b0a12 with one soft purple glow (#1d1638) behind the main content. No glass, no gradients on cards.
- Brand purple #5b41da for fills (buttons, the logo scene, highlight blocks). For purple TEXT on dark backgrounds use the lighter #8f7bff so it stays readable.
- Red #ff5a5f only for missed calls and lost money. Green #34c759 only for answered calls and ticks. Never use red and green on the same screen except on a phone call card.
- Fonts: Space Grotesk Bold (fonts/SpaceGrotesk-700.woff2) for headlines, tight letter spacing, big. Inter (fonts/Inter-400.woff2, fonts/Inter-700.woff2) for UI text. JetBrains Mono (fonts/JetBrainsMono-400.woff2) for small uppercase labels, times and phone numbers.
- Cards: solid #16141f with a 2px #2a2738 border, 36 to 48px corners, soft dark shadow. Cards on the purple brand scene are white.
- Things that should look like a phone (incoming call, missed call notifications, a booking confirmation) are built in HTML and CSS so they look real, not like slides.
- Motion: headlines reveal line by line from below a mask (power4.out, about 0.5s). Cards rise in (power3.out). Numbers count up. Only the logo and ticks get a small bounce. Cuts are fast; nothing lingers.
- Keep all text inside the middle 80% of the width. Keep the bottom 20% of the frame clear for captions and the TikTok/Reels UI.
```

## PROMPT 16 · Clean up raw footage (cuts + captions)

The kit had no prompt for this. Run it FIRST on a raw phone recording, before PROMPT 11. Put your recording in the folder as raw.mp4.

```
Clean up my raw talking-head video raw.mp4 with HyperFrames, in this folder. It's a vertical phone recording for a TikTok / Reels ad.

1. Transcribe it with npx hyperframes transcribe and check the word timings against the audio. If whisper isn't installed, stop and tell me to run the setup prompt.
2. Cut out dead air: any pause longer than 0.4 seconds, false starts, and repeated takes of the same line (keep the last, cleanest take). Don't cut inside a word and don't change what I say. Keep my original audio.
3. Show me the list of cuts (from-to times and the words around each one) before you render anything, and wait for my OK.
4. After I approve, add word-synced captions in the bottom fifth of the frame: 2 to 4 words at a time, white Inter Bold with a soft dark shadow, the word I'm saying right now highlighted in #8f7bff. Keep them inside the middle 80% of the width.
5. Add a subtle punch-in (about 8% zoom, fast) on the 2 or 3 lines that matter most, so the cut-down video doesn't feel static.

Render to renders/clean.mp4 at the same size and frame rate as raw.mp4. Then rename it to clip.mp4 so PROMPT 11 picks it up.
```

## PROMPT 17 · RezFlo 15-second opener

Makes the opener that sets the tone of the ad (dinner rush → missed calls → the math → RezFlo answers). Change the numbers to ones you can stand behind.

```
Make a 15-second vertical opener for a RezFlo ad with HyperFrames in this folder, 1080x1920 at 30 fps. No footage, no voiceover. Everything (phone screens, notifications, logo) is built in HTML and CSS.

RezFlo is an AI phone receptionist for restaurants. It answers every call, takes reservations and orders, and never puts anyone on hold.

Scenes, with exact timings:
1. 0 to 3.4s · The rush. Small label "Friday · 7:42 PM" with a red dot. Headline over two lines: "Dinner rush." then "Phone's ringing." (second line in purple). An incoming call card rises in with a phone number, red and green buttons, pulsing rings around the caller icon, and a small shake on each ring.
2. 3.4 to 7s · Headline "Nobody picks up." (second line red). Four "Missed call" notifications slide in fast from the right with times 7:42, 7:49, 8:03, 8:11 PM. Then they clear and a huge red number counts up 0 to 20, with "missed calls this week" under it.
3. 7 to 10.6s · The math. Small label "The math", then "20 calls × $50", then a huge number that counts up to $1,000 and turns red when it lands, with "gone. every week." under it. Then two lines: "No voicemail." (grey) and "They call the next place."
4. 10.6 to 15s · A purple circle wipes out from the centre and fills the screen. The RezFlo wordmark pops in with a small animated sound-wave icon. A white call card rises in: "Answered by RezFlo · 0:01", a caller bubble "Hi, table for 4 at 8 tonight?", then a purple reply bubble "You're booked. See you at 8." with a tick that pops in. Then "Every call. Answered." and "rezflo.ca" small underneath. Hold to the end.

Sounds from the sfx folder, quiet: a tick for each missed-call notification, the counter sound under both count-ups, a pop on the logo, a tick on the booking tick, the chime on "Answered." No whooshes.

Use my exact words. Run npx hyperframes check and fix every error before rendering. Then pull frames at 1.6s, 4.7s, 6.3s, 8.4s, 12.9s and 14.8s and look at them yourself: fix anything cut off, overlapping or hard to read before you tell me it's done.

Follow the STYLE section below. Render to renders/rezflo-opener.mp4 with --quality delivery.
```

## PROMPT 18 · RezFlo product demo (replaces PROMPT 09 for RezFlo)

```
Make a 12-second vertical product video for RezFlo with HyperFrames in this folder, 1080x1920 at 30 fps.

RezFlo is an AI phone receptionist for restaurants. If there is a screenshots folder, use those screens as they are and zoom into the part that matters. If not, build the screens in HTML and CSS.

Structure:
1. 0 to 2s: RezFlo wordmark reveal on the purple brand colour.
2. 2 to 9s: three moments, each showing the product doing the thing, not just a sentence:
   - a call comes in at 9:40 PM and RezFlo picks up on the first ring
   - a live transcript where the caller books a table and gets a confirmation text
   - a dashboard card showing "Calls answered this week" counting up to 143, with "0 missed"
3. 9 to 12s: end card with RezFlo, one short line ("Your phone, answered. Every time.") and the call to action "Book a free demo".

Follow the STYLE section below. Render to renders/product.mp4.
```

## PROMPT 19 · Put the opener in front of your video

Run in the folder that has both renders/rezflo-opener.mp4 and your finished clip.

```
Join renders/rezflo-opener.mp4 and renders/with-cards.mp4 into one video, opener first. Match them to the same size (1080x1920) and frame rate (use the talking-head clip's frame rate). Make the cut between them a fast punch: the last 0.2 seconds of the opener scales up slightly and the clip starts immediately, no fade to black. Keep the clip's audio exactly as it is and let the opener's sounds finish without overlapping my first word. Render to renders/final.mp4 and tell me the total length.
```
