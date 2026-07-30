# HANDOFF: Omni Twilio SMS + Voice

Version 1.1
Created 2026-07-30, updated 2026-07-30
Owner: Aaron Baker
Status: SMS live and carrier-verified. Voice live, greeting plus voicemail.

---

## 1. ONE-PARAGRAPH SUMMARY

Omni Pool Builders had a dead A2P 10DLC campaign from 7/28/2024 that blocked all
outbound texting for two years across three registration attempts. The cause was
a single unread field: the end-user consent / call-to-action text submitted to
The Campaign Registry still contained the literal template placeholders
`[Business Name]` and `[URL]`, so a carrier reviewer had nothing real to verify.
That drove both stated rejection reasons (unverifiable website, unverifiable
call to action). The brand itself was always fine. Fix cost $15 and one
resubmission. SMS confirmed working both directions 2026-07-30 at 10:13:05 MST.

---

## 2. CANONICAL IDENTIFIERS

| Object | Value | Status |
|---|---|---|
| A2P Brand SID | `BN68bde436601f3dffb1eaf1ad70465190` | Registered, trust score 75/100 |
| A2P Campaign SID | `CM7bdfdc1086c4d845b203bcef230847f0` | Verified |
| TCR external campaign ID | `CPCMHT1` | Assigned |
| Campaign use case | Low Volume Mixed | |
| Messaging Service SID | `MG686c51d474261162d4189d00afad6de3` | Name: Low Volume Mixed A2P Messaging |
| Working number SID | `PNdb194e3d97e5fb2d7df780fad820d451` | +1 520-468-0010 |
| SMS auto-reply TwiML Bin | `EH256946b97ccef1cf148816ccee392f22` | Name: Omni SMS Auto-Reply (520-468-0010) |
| Voice greeting TwiML Bin | `EHf3299cc2a0ca4f2b79ffd94acaa26370` | Name: Omni Voice Greeting + Voicemail (520-468-0010) |
| Voice post-record TwiML Bin | `EH45d3b0f7fe8e849358ec9bc93d6b4149` | Record action target, closes the call |
| TwiML Bin URL pattern | `handler.twilio.com/twiml/` + bin SID | |

DO NOT re-register or modify the brand. Brand registration is the slow,
expensive stage and it already passed. Only campaigns get deleted and rebuilt.

---

## 3. PHONE NUMBER INVENTORY

| Number | Locality | In sender pool | E911 addr | Notes |
|---|---|---|---|---|
| +1 520-468-0010 | Tucson | yes | NO | primary working number, auto-reply attached |
| +1 520-729-9838 | Tucson | yes | yes | pre-existing |
| +1 520-335-0398 | Sierra Vista | yes | yes | wrong market, release candidate |
| +1 520-613-1888 | unknown | yes | yes | release candidate |
| +1 520-602-8280 | unknown | yes | yes | release candidate |
| +1 888-367-0846 | toll-free | n/a | n/a | verification required, cannot send |

All five local numbers are covered by the approved campaign. Releasing a number
from the sender pool does not affect the brand or campaign. The only
irreversible risk is releasing a number printed on a truck, yard sign, Google
Business Profile, or old advertisement. Verify external footprint before
releasing anything.

---

## 4. COSTS

Verified from Twilio usage, July 2026. Available funds $181.47 at time of writing.

| Item | Type | Amount |
|---|---|---|
| Campaign vetting fee | one-time | $15.00 |
| Campaign registration | monthly | $1.50 |
| Local number rental | monthly, each | $1.15 |
| Emergency Calling Number | monthly, each | $0.75 |
| Toll-free rental | monthly | approx $2.15 |
| Brand registration | one-time, already paid | $4.50 or $46 depending on tier |
| Per-message | usage | fractions of a cent |

Total recurring across all five local numbers plus campaign: $12.40/month.
First billing cycle 8/28 to 8/29.

Each denied campaign resubmission incurs the $15 vetting fee again. This is why
the submit step must be gated behind a full verification pass, not attempted
optimistically.

---

## 5. PROOF OF WORKING STATE

Retain this. It is the cleanest possible before/after and settles any future
"is texting actually registered" question.

| Date | Direction | Result | Error |
|---|---|---|---|
| 2026-05-29 | outbound | Undelivered | 30034 US A2P 10DLC Message from an Unregistered Number |
| 2026-06-03 | outbound | Undelivered | 30034 US A2P 10DLC Message from an Unregistered Number |
| 2026-07-30 10:13:05 MST | inbound from 520-591-8884 | Received | none |
| 2026-07-30 10:13:05 MST | outbound auto-reply | Delivered | none |
| 2026-07-30 15:08:09 MST | inbound text, second round trip | Received | none |
| 2026-07-30 15:08:09 MST | outbound auto-reply | Delivered | none |
| 2026-07-30 15:07:34 MST | inbound VOICE call | Completed, 22 sec, $0.00 | none |

Voice call SID `CAbb62633ac9274fd4828b355c73789c00`. Recording SID
`RE6a308f103e1469b11a73e52072e1cba8`, playable in console with WAV and MP3
download. Request Inspector showed HTTP 200 in 34ms on the greeting fetch and a
second 200 in 36ms on the post-record callback.

Same account, same destination handset. Delivered means carrier-confirmed
handset receipt, not merely accepted for sending. Error 30034 is the specific
signature of an unregistered or improperly attached number and is the error to
look for if texting ever breaks again.

---

## 6. COMPLIANCE SURFACE (tucsonpoolbuilders.com)

Canonical pages, all HTTP 200, all serving fresh content after nginx purge:

| Page | URL |
|---|---|
| Privacy Policy | https://tucsonpoolbuilders.com/privacy-policy/ |
| SMS Terms | https://tucsonpoolbuilders.com/sms-terms-of-service/ |
| Sign-up form | https://tucsonpoolbuilders.com/text-message-signup/ |

Superseded slugs still exist as harmless orphans, nothing was deleted:
`/tucson-pool-builders-omni-specific-privacy-policy/`, `/sms-terms-conditions/`,
`/sms-signup/`. No live page links to them.

Stack: WordPress on BoldGrid / InMotion. Contact Form 7 and CFDB7 handle the
sign-up form and store submissions with the checkbox value and timestamp.
WP Fastest Cache is the plugin layer. An nginx 1.26.1 proxy cache sits ABOVE
WordPress and does not purge on save. See gotchas.

### The four registered consent paths

These are the only paths described on the site and in the campaign. Do not text
anyone whose consent did not arrive by one of these.

1. `web_signup_checkbox` — unchecked box on the sign-up page, not required to
   submit, stored by CFDB7 with timestamp.
2. `inbound_text_first` — customer texts an Omni business number first, which
   is consent to reply about that inquiry.
3. `verbal` — consent given by phone, in the showroom, or on site, recorded with
   date, time, and method.
4. `signed_document` — text-messaging consent language on a signed proposal,
   contract, or service order.

There is NO "reply Y" confirmation flow. It was removed deliberately because
nothing sends that message. Registering a flow you do not actually perform is a
suspension risk. If Y-confirmation automation is ever built, update the pages
and the campaign together, never one alone.

### Opt-out and help keywords

Handled automatically by Twilio, matching what was registered with carriers.

Opt-out: stop, quit, cancel, unsubscribe, end, revoke, optout, stopall
Help: help, info

---

## 7. CONSENT LOG SPEC

The public pages state that consent is recorded with date, time, and method in
the customer management system. That claim must be true before any real customer
is texted. CFDB7 covers path 1 automatically. Paths 2, 3, and 4 are manual until
this moves into ProDBX.

Sheet name: `Omni_SMS_Consent_Log`, tab `consent`.

```
consent_date | consent_time | first_name | last_name | mobile_number |
consent_method | captured_by | source_detail | opt_out_date | notes
```

- `consent_method`: web_signup_checkbox | inbound_text_first | verbal | signed_document
- `captured_by`: employee name
- `source_detail`: proposal number, showroom visit, job address, or call reference
- `opt_out_date`: populate on STOP so the row shows the full lifecycle

---

## 8. GOTCHAS (each one cost real time)

**Placeholder text in the CTA field.** The two-year blocker. Before any campaign
submission, search the entire submission for `[` and `]`. Zero bracketed
placeholders may remain anywhere.

**Nginx proxy cache above WordPress.** The host runs an nginx page cache that
ignores WP Fastest Cache purges and no-cache request headers. Edits save to the
database and the public URL keeps serving a frozen copy, in one case two weeks
stale. Symptom: the plain URL shows old content but the same URL with a junk
query string (`?cb=1`) shows the new content, and response headers read
`x-proxy-cache: HIT`. Fix requires the host: BoldGrid Central, or an InMotion
ticket asking them to flush the nginx proxy cache. Always verify anonymously,
logged out, at plain URLs with no query string, and read the build stamp in the
page source.

**Sender pool assignment.** Campaign approval alone does not enable a number.
The number must be attached to the messaging service linked to the approved
campaign. An unattached number fails with error 30034 and looks like a brand new
mystery.

**GSM-7 vs UCS-2 segment trap.** A curly apostrophe, curly quote, em dash, or
ellipsis pasted from Word silently switches the encoding and drops the
single-segment limit from 160 characters to 70. Use straight punctuation only.
If a short message suddenly reports three segments, this is why.

**Advanced Opt-Out blast radius.** Customizing the HELP reply requires enabling
Advanced Opt-Out, which changes opt-out behavior across ALL numbers in the
messaging service, including live office lines. Left OFF deliberately.
Compliance is satisfied either way since the default keywords all work.

**Sign-up consent string is byte-locked.** The checkbox label on the sign-up page
is the verbatim string stored in the consent records and submitted to the
carriers. Changing its bytes forks the consent history and desyncs the site from
the registration. If it must change, change page and campaign together and note
the cutover date in the consent log.

**Regulatory bundles are unrelated.** A rejected foreign-number regulatory bundle
(e.g. the abandoned Algeria bundle) sits in a separate system and has no effect
on 10DLC vetting, trust score, or delivery. Ignore it.

**Do not blast a list.** Outbound is technically possible now. Sending to anyone
who did not consent through one of the four registered paths is how verified
brands get suspended.

**`<Record>` without an `action` attribute creates an infinite greeting loop.**
Twilio POSTs the recording result back to the SAME webhook URL by default. If
that URL returns the greeting, the caller hears the greeting again after the
silence timeout, then again, forever, until they hang up. This does NOT show up
when you test by hanging up at the beep, because the call is already gone when
the second response arrives. It only bites real callers who actually leave a
message. Always point `action` at a separate bin that thanks the caller and
hangs up. Test by leaving a message and then STAYING SILENT for six seconds.

**Never save a half-loaded Twilio console form.** The console intermittently
throws "Parts of the application are not loading" and sections revert to generic
placeholder state. On the phone number config page, the Messaging section can
fall back to showing "A2P 10DLC registration required," which is Twilio's promo
block, NOT a status indicator. Saving from that state can null the messaging
config. If any section looks unloaded, hard reload, re-enter, confirm every
section rendered, then save. Verify the save survived a reload rather than
trusting the Save button, since saves can appear to succeed with no timestamp
change and only take effect after a hard refresh.

---

## 9. CURRENT SMS AUTO-REPLY

Lives in TwiML Bin `EH256946b97ccef1cf148816ccee392f22`, scoped to 520-468-0010
only because the messaging service is set to "Defer to sender's webhook." The
other four numbers behave exactly as they did before.

Current body runs 163 characters, which is 2 segments. Optional single-segment
replacement at 145 characters, straight punctuation only:

```
Omni Pool Builders: Thanks for reaching out. We will reply during business hours. Msg&data rates may apply. Reply STOP to opt out, HELP for help.
```

---

## 10. VOICE (DEPLOYED)

Voice required no carrier registration of any kind. There is no A2P equivalent
for inbound calls: no brand, no campaign, no vetting fee, no reviewer. The number
already had voice routing Active; it simply had no instructions for what to do
when a call arrived. That was the entire gap. Total setup time was minutes.

### What is live on 520-468-0010

Primary handler: bin `EHf3299cc2a0ca4f2b79ffd94acaa26370`, validated by Twilio as
Valid Voice TwiML. Amazon Polly greeting, then beep, records up to three minutes
with silence trimming. If nothing is recorded, it tells the caller to call again
or send a text, then hangs up.

Greeting content: thank you for calling Omni Pool Builders and Design, please
leave your name, phone number, and a brief message after the tone and a team
member will return your call, you can also text this same number at any time,
your message will be recorded.

Record action target: bin `EH45d3b0f7fe8e849358ec9bc93d6b4149`. Says "Thank you.
We have your message and a team member will call you back. Goodbye." then hangs
up. This bin exists specifically to prevent the infinite greeting loop described
in Section 8.

Primary handler fails fallback: pointed at the same greeting bin, so a hiccup on
the first request still yields a greeting instead of dead air.

Deliberately NOT built: business hours logic and a staff directory. Callers would
hear whatever was invented. Hours-based routing is impossible in a static TwiML
Bin anyway and requires Twilio Studio or a Function.

Voicemails live under Monitor > Logs > Call recordings.

### Reference templates

Forward to a handset:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial callerId="+15204680010" timeout="20">+1520XXXXXXX</Dial>
  <Say voice="Polly.Joanna">Sorry, we were unable to connect your call. Please try again later.</Say>
</Response>
```

Greeting plus voicemail:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Joanna">Thank you for calling Omni Pool Builders and Design. This call may be recorded. Please leave a message after the tone and we will return your call.</Say>
  <Record maxLength="180" playBeep="true" trim="trim-silence"
          action="https://handler.twilio.com/twiml/EH45d3b0f7fe8e849358ec9bc93d6b4149"/>
  <Say voice="Polly.Joanna">We did not receive a message. Goodbye.</Say>
</Response>
```

Post-record bin, the `action` target:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Joanna">Thank you. We have your message and a team member will call you back. Goodbye.</Say>
  <Hangup/>
</Response>
```

The `action` attribute is not optional. Omitting it is the loop defect.

Transcription bills per minute if `transcribe="true"` is added. Arizona is
one-party consent so the spoken recording notice is not legally required, and the
privacy policy already discloses recording, transcription, and staff review, but
keep the notice since the end state is a front desk taking customer calls.

Recordings accrue monthly storage charges. Set a retention habit early or they
pile up quietly.

Dial timeout note for any future forwarding setup: use 15 seconds, not 20 or 30.
A typical cell rolls to its own voicemail at 20 to 25 seconds, so a longer Twilio
timeout drops the caller into a personal voicemail greeting instead of Omni's,
which looks like broken TwiML but is not.

---

## 11. RUNBOOKS

### Add a new number to the working setup
1. Buy the number with Voice and SMS capability.
2. Attach it to messaging service `MG686c51d474261162d4189d00afad6de3`.
3. Confirm it appears in the sender pool. This is the step that gets skipped.
4. Add an Emergency Calling Number, $0.75/month.
5. Send a real test text from an outside handset. Look for Delivered, not Sent.
6. Add the number to the "Numbers We Send From" section of the SMS Terms page.

### Texting suddenly stops working
1. Check the Messaging log for error 30034. That means unregistered or detached.
2. Confirm the number is still in the messaging service sender pool.
3. Confirm campaign `CM7bdfdc1086c4d845b203bcef230847f0` still reads Verified.
4. Confirm the account has funds. A zero balance halts sending.
5. Only then look at webhooks or TwiML.

### A campaign gets rejected
1. Failed campaigns cannot be argued into approval. Delete and re-register.
2. Never re-register the brand. Reuse `BN68bde436601f3dffb1eaf1ad70465190`.
3. Re-read every submitted field for bracketed placeholders before submitting.
4. Verify the site anonymously at plain URLs first. Each attempt costs $15.

### Deploy or change voice on a number
1. Set the webhook on the PHONE NUMBER under Voice & Fax > "A Call Comes In".
   Not on the messaging service. Messaging services do not handle voice.
2. Method HTTP POST. Populate "Primary handler fails" with the same bin.
3. If the TwiML contains `<Record>`, it MUST have an `action` pointing at a
   separate closing bin. See Section 8.
4. Confirm every section of the config page rendered before saving.
5. Save, then hard reload and confirm the change persisted.
6. Test call. Leave a message, then stay silent six seconds. You must hear the
   closing message and the line must drop.
7. Verify in Monitor > Logs > Calls: status Completed, and check Request
   Inspector for HTTP 200 on both the greeting fetch and the post-record POST.

### Website edit did not go live
1. Request the URL with `?cb=1`. If the new content appears, it is the cache.
2. Clear WP Fastest Cache.
3. Purge the host nginx cache via BoldGrid Central or an InMotion ticket.
4. Re-verify logged out, plain URL, and read the build stamp in page source.

---

## 12. OPEN ITEMS

| Item | Owner | Priority |
|---|---|---|
| Build consent log sheet | Aaron | before first customer text |
| Delete CFDB7 test row TEST / DELETE-ME ufid 1528 | Aaron | whenever |
| Sign-up notifications to info@omnipoolbuilders.com | WordPress agent | this week |
| E911 address on 520-468-0010, $0.75/mo | Aaron approve, agent execute | do this, line now answers |
| Confirm loop fix with a silent-pause test call | Aaron | recommended |
| Voicemail check habit, Monitor > Logs > Call recordings | Aaron | before promoting the number |
| Audit and release unused 520 numbers | Aaron | saves approx $55/yr |
| Toll-free verification on 888-367-0846 | Twilio agent | optional, copy-forward |
| Custom HELP reply via Advanced Opt-Out | leave off | not worth blast radius |
| Business hours routing, needs Studio or Function | future | not possible in a TwiML Bin |
| ProDBX form consent checkbox | deferred | only if web form becomes an opt-in path |

Closed: voice webhook deployed 2026-07-30.

---

## 13. CHANGE LOG

- 2026-07-30 v1.0 — Created. Campaign verified, SMS live both directions,
  website compliance surface rebuilt on canonical slugs, nginx cache purged.
- 2026-07-30 v1.1 — Voice deployed on 520-468-0010: greeting bin, voicemail with
  silence trim, dedicated post-record closing bin, fallback handler. Second SMS
  round trip confirmed. Added the `<Record>` action loop defect and the
  half-loaded console form to gotchas. Added a voice deployment runbook. Voice
  webhook moved from open to closed.
