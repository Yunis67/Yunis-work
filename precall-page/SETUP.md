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

## 6 · Meeting reminders (Cal.com → GHL webhook)

Cal.com sends each booking straight to GHL, and GHL texts the reminders. This is free on Cal.com: no paid plan needed.

### Step 1 · Make two custom fields in GHL
Go to Settings → Custom Fields → Contact, and add:
- **Demo call time** (type: Date/Time)
- **Reschedule link** (type: Text)

### Step 2 · Make the workflow and get its URL
1. Create a new workflow, "Demo reminders", with the trigger **Inbound Webhook**. Copy its URL.
2. In Cal.com, go to **Settings → Developer → Webhooks → New**.
   - Paste the GHL URL.
   - Tick **Booking Created**, **Booking Rescheduled** and **Booking Cancelled**.
   - Leave the payload template empty (default) and save.
3. Book one test call on yourself in Cal.com. Then go back to the GHL trigger and click **Fetch sample**, so GHL can see the fields.

### Step 3 · What Cal.com sends (the fields you'll map)

| What | Cal.com field |
|---|---|
| Event type | `triggerEvent` (`BOOKING_CREATED`, `BOOKING_RESCHEDULED`, `BOOKING_CANCELLED`) |
| Start time | `payload.startTime` |
| Email | `payload.attendees[0].email` |
| Name | `payload.attendees[0].name` |
| Phone (if the booking form asks for it) | `payload.responses.attendeePhoneNumber.value` |
| Booking ID | `payload.uid` |

**Reschedule link for this booking:** `https://cal.com/reschedule/` + `payload.uid`. This moves the existing booking, so you don't end up with a second one like the general link creates.

### Step 4 · Workflow actions
1. **Find contact** by email (`payload.attendees[0].email`). If no contact is found, create one with the name, email and phone.
2. **If/Else** on `triggerEvent`:
   - **BOOKING_CANCELLED:** remove the contact from this workflow's earlier runs (action "Remove from workflow", pick "Demo reminders"), add the tag `call cancelled`, and stop.
   - **Anything else** (created or rescheduled): continue.
3. **Remove from workflow "Demo reminders"** (only the *other* runs). This clears old reminders when someone reschedules. If GHL won't let a workflow remove itself, use a second tiny workflow that only does this step and runs first.
4. **Update contact fields:**
   - Demo call time = `payload.startTime`
   - Reschedule link = `https://cal.com/reschedule/{{inboundWebhookRequest.payload.uid}}`
5. **Wait** until 24 hours before **Demo call time**, then send this SMS:
   > Hey {{contact.first_name}}, reminder: your call with Yousef is tomorrow at {{contact.demo_call_time}}. Need a new time? {{contact.reschedule_link}}
6. **Wait** until 1 hour before **Demo call time**.
7. **If/Else:** does the contact have the tag `call confirmed`?
   - **Yes:** send "Starting in an hour. Talk soon!"
   - **No:** send "Your call with Yousef starts in an hour. Quick 2-min video + confirm here: https://rezflo-call.netlify.app/?cid={{contact.id}}"

> **Waits on bookings made the same day:** if the call is less than 24 hours away, GHL skips the 24h wait and sends that reminder right away. Add an If/Else before step 5 if you'd rather skip it.

> **Time zone:** Cal.com sends the start time in UTC. Make sure the GHL location time zone is set to Toronto, so the time shows correctly in the texts.

### Step 5 · Test
- [ ] Book a test call → the contact gets the two fields filled in.
- [ ] Reschedule it → the fields update, and the old reminders don't send.
- [ ] Cancel it → no reminders send, and the contact gets the `call cancelled` tag.

## Swapping videos

Replace a file in `media/` and keep the same name. Each video has a matching `.jpg` cover image. These are web copies (720p) made from the final renders in `renders/`.
