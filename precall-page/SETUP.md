# Pre-call page · setup

A single page that leads take one step at a time: watch Yousef's video, tap **Yes, I'll be there**, then the three FAQ videos. Everything it needs is in this folder (`index.html`, `media/`, `fonts/`, `img/`), so it can be hosted anywhere that serves static files (GHL custom code or file hosting, Netlify, Vercel, Cloudflare Pages, your own domain).

## How it fits your flow

1. **Your team books the call on the phone** in Cal.com. Your existing automation sends the contact to GHL.
2. **A GHL workflow texts the lead the page link**, with their details in it.
3. **The lead watches the video and taps "Yes, I'll be there".**
4. **The page sends that tap to a second GHL workflow**, which tags the contact and pings you.

On the call, the rep can say: *"I'm texting you a short video from Yousef. Watch it before our call and tap confirm."*

## 1 · The link to text out

```
https://YOUR-DOMAIN/precall/?name={{contact.first_name}}&email={{contact.email}}&cid={{contact.id}}
```

- **What it does:** GHL fills in the `{{…}}` parts for each person. The page uses `name` in the top bar ("Marco, your call with Yousef is booked") and sends `cid` and `email` back when they confirm.
- **Optional call time:** if the call time is saved on the contact (for example a custom field), add `&when={{contact.your_field}}` and it shows in the top bar. Leave it off if not.

## 2 · Workflow A: "Send pre-call page"

- **Trigger:** whatever your Cal.com → GHL automation already produces when a call is booked, such as an appointment booked, a tag added (e.g. `call booked`) or a pipeline stage change. Use the one you already have.
- **Action:** Send SMS (and/or Email) with the link above. Example text:
  > Hey {{contact.first_name}}, it's the RezFlo team. Here's a short video from Yousef to watch before our call, plus a button to confirm you'll be there: LINK

## 3 · Workflow B: "Call confirmed"

1. Create a workflow with the trigger **Inbound Webhook**. GHL shows a webhook URL; copy it.
2. Open `index.html`, find `var CONFIG = { webhookUrl: "" };` near the bottom, and paste the URL between the quotes.
3. Open the page using a test link (your own contact) and tap the button once, so GHL receives a sample. Map the contact using `contact_id` (or `email` as a fallback).
4. Add actions:
   - **Add tag:** `call confirmed`
   - **Internal notification** (SMS or email to you): `{{contact.first_name}} confirmed their call with Yousef`

What the page sends on tap: `event=call_confirmed`, `contact_id`, `email`, `first_name`, `page`.

> **Plan note:** on some GHL plans, Inbound Webhook is a premium trigger with a small per-run charge. If you'd rather not use it, the fallback is a one-button GHL form embedded in place of the button. It works the same way but is harder to style to match the page.

## 4 · Optional: reminder for people who didn't confirm

In Workflow A, after the SMS:
- Wait until about 3 hours before the call (or a fixed delay, if the call time isn't on the contact).
- **If/Else:** contact has the tag `call confirmed`?
  - **No:** send one short reminder: "Quick reminder about your call with Yousef today. Tap here to confirm: LINK"
  - **Yes:** do nothing.

## 5 · Test before going live
- [ ] The texted link opens the page and shows the right first name.
- [ ] Both the main video and the FAQ videos play on an iPhone and an Android phone, with sound.
- [ ] Tapping the button shows "You're confirmed", and GHL tags the contact within a minute.
- [ ] You get the "confirmed" notification.
- [ ] Reopening the link on the same phone still shows "You're confirmed". This is stored on the device; the GHL tag is the real record.

## Swapping videos

Replace a file in `media/` and keep the same name. Each video has a matching `.jpg` cover image. These are web copies (720p) made from the final renders in `renders/`.
