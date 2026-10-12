# Pre-call page · setup

Live at **https://rezflo-call.netlify.app** (Netlify Drop). To update it, drag the new `precall-page` folder onto the site's Deploys page in Netlify.

A single page that leads take one step at a time: watch Yousef's video, tap **Yes, I'll be there**, then the three FAQ videos. Everything it needs is in this folder (`index.html`, `media/`, `fonts/`, `img/`), so it can be hosted anywhere that serves static files (GHL custom code or file hosting, Netlify, Vercel, Cloudflare Pages, your own domain).

## How it fits your flow

1. **Your team books the call on the phone** in Cal.com. Your existing automation sends the contact to GHL.
2. **A GHL workflow texts the lead the page link**, with their details in it.
3. **The lead watches the video and taps "Yes, I'll be there".**
4. **The page sends that tap to a second GHL workflow**, which tags the contact and pings you.

On the call, the rep can say: *"I'm texting you a short video from Yousef. Watch it before our call and tap confirm."*

## 1 · The link to text out

```
https://rezflo-call.netlify.app/?cid={{contact.id}}
```

- **What it does:** GHL fills in `{{contact.id}}` for each person. The page sends it back to GHL when they tap confirm, so GHL knows who confirmed. Keep the link this short: names with spaces or symbols can break a texted link.

## 2 · Workflow A: "Send pre-call page"

- **Trigger:** whatever your Cal.com → GHL automation already produces when a call is booked, such as an appointment booked, a tag added (e.g. `call booked`) or a pipeline stage change. Use the one you already have.
- **Action:** Send SMS (and/or Email) with the link above. Example text:
  > Hey {{contact.first_name}}, it's the RezFlo team. Here's a short video from Yousef to watch before our call, plus a button to confirm you'll be there: LINK

## 3 · Workflow B: "Call confirmed"

1. Create a workflow with the trigger **Inbound Webhook**. GHL shows a webhook URL; copy it.
2. Already done: the page's `CONFIG.webhookUrl` holds this account's webhook URL. If you ever make a new webhook, paste its URL there.
3. Open the page using a test link (your own contact) and tap the button once, so GHL receives a sample. Map the contact using `contact_id` (or `email` as a fallback).
4. Add actions:
   - **Add tag:** `call confirmed`
   - **Internal notification** (SMS or email to you): `{{contact.first_name}} confirmed their call with Yousef`

What the page sends on tap (JSON): `event` = `call_confirmed`, `contact_id`, `email`, `first_name`, `page`, `confirmed_at`. With the short texted link only `contact_id` is filled.

> **Plan note:** on some GHL plans, Inbound Webhook is a premium trigger with a small per-run charge. If you'd rather not use it, the fallback is a one-button GHL form embedded in place of the button. It works the same way but is harder to style to match the page.

## 4 · Optional: reminder for people who didn't confirm

In Workflow A, after the SMS:
- Wait until about 3 hours before the call (or a fixed delay, if the call time isn't on the contact).
- **If/Else:** contact has the tag `call confirmed`?
  - **No:** send one short reminder: "Quick reminder about your call with Yousef today. Tap here to confirm: LINK"
  - **Yes:** do nothing.

## Preview on your computer

From this folder run `python3 -m http.server 8000`, then open http://localhost:8000 in your browser.

## 5 · Test before going live
- [ ] The texted link opens the page.
- [ ] Both the main video and the FAQ videos play on an iPhone and an Android phone, with sound.
- [ ] Tapping the button shows "You're confirmed", and GHL tags the contact within a minute.
- [ ] You get the "confirmed" notification.
- [ ] Reopening the link on the same phone still shows "You're confirmed". This is stored on the device; the GHL tag is the real record.

## 6 · Meeting reminders (Cal.com → GHL, as built)

Free on Cal.com. GHL sends the texts. The team books the **"Schedule a Meeting" 30min** event (Cal.com event type ID **5598938**).

### Custom contact fields
- **Demo call time** (Date picker)
- **Reschedule link** (Single line)

### Workflow "Cal.com Lead Booking System" (old Cal.com webhook, new bookings)
- **Branch:** `payload.eventTypeId` is `5598938`. This must match the event the team books, or nothing below runs.
- **Create Contact** step also sets:
  - Demo call time = Inbound Webhook Trigger › Payload › Start Time
  - Reschedule link = `https://cal.com/reschedule/` + Inbound Webhook Trigger › Payload › Uid (insert with the tag picker, don't type it)
- **Last step:** Add to Workflow → **Meeting SMS Reminders**.

### Workflow "Meeting SMS Reminders" (no trigger; people are added to it)
```
Wait  → Until a specific date/time → Contact › Demo call time → Before 24 hours
SMS   → "Hey {{contact.first_name}}, it's RezFlo. Reminder: your call with Yousef
         is tomorrow. Need a new time? {{contact.reschedule_link}}"
Wait  → same, Before 1 hour
If/Else → tag "call confirmed"
   Yes → "Your call with Yousef starts in an hour. Talk soon!"
   No  → "Your call with Yousef starts in an hour. Quick 2-min video + confirm
          here: https://rezflo-call.netlify.app/?cid={{contact.id}}"
```
"If this date has already passed" = Skip outbound communication (so same-day bookings skip the 24h text).

### Reschedules and cancels (new Cal.com webhook)
Cal.com webhook with only **Booking rescheduled** and **Booking canceled** ticked (not "created", or it races the booking workflow and can make duplicate contacts). Its GHL workflow:
```
Inbound Webhook → Create/update contact (email, Demo call time, Reschedule link)
→ Remove from Workflow: Meeting SMS Reminders
→ If/Else triggerEvent
   BOOKING_CANCELLED → Add tag "call cancelled"
   None (rescheduled) → Add to Workflow: Meeting SMS Reminders
```

### Debugging
Execution logs → open the run → click a step. If a run went down "None" at the Branch, the event type ID doesn't match.

## Swapping videos

Replace a file in `media/` and keep the same name. Each video has a matching `.jpg` cover image. These are web copies (720p) made from the final renders in `renders/`.
