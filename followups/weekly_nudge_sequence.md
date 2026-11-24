# Weekly nudge — never-responded prospects

Apollo sequence, 12 auto-emails, one every 7 days. Email 1 starts a thread;
emails 2–12 reply in that thread so the history stays visible. Claims are
limited to what the existing "Call Follow-up – Meeting Ask" templates say.

## Who is enrolled
Built by `build_followup_list.py` from an Apollo export:

- Contacted before (called at least once; our process is call → email),
  stage Cold / Approaching / Unresponsive, has an email.
- **Skipped (hands-on):** stage Interested / Replied / Not Interested /
  Do Not Contact / Bad Data / Changed Job; any "Connected" call; call notes
  about meetings, demos, pilots, intros, call-backs, "not interested",
  "remove", wrong person, DNC.
- **Org-wide hold:** if anyone at a company is Interested / Replied, had a
  positive call, or has a meeting/intro/pilot note, nobody else at that
  company is enrolled.

## Sequence settings
- Finish contact on reply: on. Finish on "Interested": on. Pause on out-of-office: on.
- Exclude contact stages: Replied, Interested, Not Interested, Do Not Contact,
  Bad Data, Changed Job.
- Schedule: Normal Business Hours (America/Los_Angeles), existing.
- After email 12: move to stage Unresponsive; re-run the builder and
  re-enroll if you want to keep going (Apollo caps a sequence at 25 steps).

## Copy

**Week 1 — new thread.** Subject: `Soiling at {{company}}`
> Hi {{first_name}}, following up on my note from a few weeks back. SwishOS
> uses the inverter data you already collect, plus weather and cleaning-cost
> data, to monitor soiling and time cleanings, with no added hardware.
> Worth 15 minutes to see it?

**Week 2**
> Hi {{first_name}}, rather than me trying to convince you: share historical
> data from one site and we'll show what better-timed cleanings would have
> earned. You see the numbers before deciding anything. Open to that?

**Week 3**
> Hi {{first_name}}, curious how {{company}} schedules panel cleaning today —
> fixed calendar, or based on measured losses? That one answer usually tells
> us whether there's money on the table.

**Week 4**
> Hi {{first_name}}, if soiling and cleaning schedules sit with someone else
> on your team, could you point me to the right person?

**Week 5**
> Hi {{first_name}}, SwishOS is already running across multiple solar farms,
> and operators have seen real revenue gains from cleaning on data instead of
> the calendar. Happy to show you how it works in 15 minutes.

**Week 6**
> Hi {{first_name}}, keeping this to one line: would a soiling-loss analysis
> on one of your sites be worth 15 minutes?

**Week 7**
> Hi {{first_name}}, dust and pollen seasons change when a wash pays for
> itself. SwishOS tracks that per site so you clean when lost revenue
> outweighs the cleaning cost. Want to see it on your own data?

**Week 8**
> Hi {{first_name}}, checking back in. If now isn't the right time, just say
> so and I'll pick this up next quarter instead.

**Week 9**
> Hi {{first_name}}, a quick "not me" is genuinely helpful too. I'd rather
> reach the right person at {{company}} than keep landing in your inbox.

**Week 10**
> Hi {{first_name}}, short version: we turn inverter data you already have
> into a site-by-site cleaning schedule, with up to a 40% increase in net
> revenue. Is soiling something you're tracking this year?

**Week 11**
> Hi {{first_name}}, the offer to run the numbers on one site's history is
> still open — no hardware, no commitment. Want me to send over what we'd need?

**Week 12**
> Hi {{first_name}}, I'll keep checking in now and then. If there's a better
> time of year to talk cleaning schedules, tell me and I'll circle back then.
