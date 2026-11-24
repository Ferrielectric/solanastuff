#!/usr/bin/env python3
"""Build the weekly follow-up list from an Apollo export.

Who gets a weekly nudge:
  * has a deliverable email and has not unsubscribed
  * has been reached out to before (called at least once; our process is
    call -> email, so a call means an email went out)
  * has never engaged: stage is Cold / Approaching / Unresponsive and no
    call with them was ever dispositioned as a conversation

Who never gets an automated nudge (person level):
  * stage Interested, Replied, Not Interested, Do Not Contact, Bad Data,
    Changed Job
  * any connected call with a positive or negative outcome, or a call note
    that says they left, asked to be removed, etc.

Org-wide respect:
  * if ANYONE at a company is Interested / Replied / had a positive call
    (i.e. we are in conversation or have a meeting), every contact at that
    company is held back from automated follow-ups.
  Companies are matched by Apollo organization_id, then email domain.

Usage:
  python3 build_followup_list.py <contacts.json> <calls.json> [outcomes.json] <out_dir>
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

STAGES = {
    "6a9a67d0ae65c8001cae2848": "Cold",
    "6a9a67d0ae65c8001cae2849": "Approaching",
    "6a9a67d0ae65c8001cae284a": "Replied",
    "6a9a67d0ae65c8001cae284b": "Interested",
    "6a9a67d0ae65c8001cae284c": "Not Interested",
    "6a9a67d0ae65c8001cae284d": "Unresponsive",
    "6a9a67d0ae65c8001cae284e": "Do Not Contact",
    "6a9a67d0ae65c8001cae284f": "Bad Data",
    "6a9a67d0ae65c8001cae2850": "Changed Job",
}
NUDGEABLE_STAGES = {"Cold", "Approaching", "Unresponsive"}
ENGAGED_STAGES = {"Interested", "Replied"}          # suppress whole org
NEGATIVE_STAGES = {"Not Interested", "Do Not Contact", "Bad Data", "Changed Job"}

# Call notes that mean "don't automate this person".
NEGATIVE_NOTE = re.compile(
    r"remove|not interested|no interest|don'?t call|do not call|stop|"
    r"not at .* anymore|no longer|left the company|retired|wrong (person|number)|"
    r"no real lead|not a fit|unsubscribe",
    re.I,
)
# Call notes that mean a live conversation / meeting is in flight.
ENGAGED_NOTE = re.compile(
    r"meeting|demo|scheduled|calendar|call back|callback|follow ?up|intro|"
    r"interested|send (me|over|info)|loop in|next week",
    re.I,
)
BAD_EMAIL_STATUS = {"unavailable", "bounced", "invalid"}

FREE_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com"}


def org_key(c):
    if c.get("organization_id"):
        return "org:" + c["organization_id"]
    email = (c.get("email") or "").lower()
    if "@" in email:
        dom = email.split("@", 1)[1]
        if dom not in FREE_DOMAINS:
            return "dom:" + dom
    name = (c.get("organization_name") or "").strip().lower()
    return "name:" + name if name else "contact:" + c["id"]


def main():
    args = sys.argv[1:]
    contacts = json.load(open(args[0]))
    calls = json.load(open(args[1]))
    outcomes = json.load(open(args[2])) if len(args) == 4 else {}
    out_dir = Path(args[-1])
    out_dir.mkdir(parents=True, exist_ok=True)

    # Outcome names may come as {id: name} or a list of {id, name}.
    if isinstance(outcomes, list):
        outcomes = {o["id"]: o.get("name") or o.get("display_name") for o in outcomes}

    def outcome_kind(oid):
        name = (outcomes.get(oid) or "").lower()
        if not name:
            return None
        if any(w in name for w in ("not interested", "negative", "do not", "wrong", "bad")):
            return "negative"
        if any(w in name for w in ("interested", "meeting", "positive", "demo", "booked")):
            return "positive"
        return "neutral"

    calls_by_contact = defaultdict(list)
    for call in calls:
        if call.get("contact_id"):
            calls_by_contact[call["contact_id"]].append(call)

    # Pass 1: person-level signals.
    person = {}
    for c in contacts:
        stage = STAGES.get(c.get("contact_stage_id"), "Unknown")
        cc = calls_by_contact.get(c["id"], [])
        notes = " | ".join((x.get("note_text") or "").strip() for x in cc if x.get("note_text"))
        kinds = {outcome_kind(x.get("phone_call_outcome_id")) for x in cc}
        engaged = stage in ENGAGED_STAGES or "positive" in kinds or bool(ENGAGED_NOTE.search(notes))
        negative = stage in NEGATIVE_STAGES or "negative" in kinds or bool(NEGATIVE_NOTE.search(notes))
        person[c["id"]] = dict(stage=stage, calls=len(cc), notes=notes,
                               engaged=engaged, negative=negative,
                               last_call=max((x.get("start_time") or "" for x in cc), default=""))

    # Pass 2: which companies are "in conversation".
    engaged_orgs = defaultdict(list)
    for c in contacts:
        if person[c["id"]]["engaged"]:
            engaged_orgs[org_key(c)].append(c.get("name") or c["id"])

    rows = []
    for c in contacts:
        p = person[c["id"]]
        key = org_key(c)
        reason = ""
        if not c.get("email"):
            reason = "no email"
        elif c.get("email_unsubscribed"):
            reason = "unsubscribed"
        elif (c.get("email_status") or "").lower() in BAD_EMAIL_STATUS:
            reason = f"email {c.get('email_status')}"
        elif p["negative"]:
            reason = "negative response / remove (hands-on)"
        elif p["engaged"]:
            reason = "in conversation / meeting (hands-on)"
        elif key in engaged_orgs:
            reason = "company in conversation via " + ", ".join(engaged_orgs[key][:3])
        elif p["stage"] not in NUDGEABLE_STAGES:
            reason = f"stage {p['stage']}"
        elif p["calls"] == 0:
            reason = "never contacted"
        rows.append({
            "contact_id": c["id"],
            "name": c.get("name"),
            "title": c.get("title"),
            "company": c.get("organization_name"),
            "email": c.get("email"),
            "stage": p["stage"],
            "calls": p["calls"],
            "last_call": p["last_call"][:10],
            "eligible": "yes" if not reason else "no",
            "excluded_reason": reason,
            "call_notes": p["notes"][:300],
        })

    rows.sort(key=lambda r: (r["eligible"] != "yes", r["company"] or "", r["name"] or ""))
    fields = list(rows[0].keys())
    for fname, subset in (("followup_eligible.csv", [r for r in rows if r["eligible"] == "yes"]),
                          ("followup_all_contacts.csv", rows)):
        with open(out_dir / fname, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(subset)

    tally = defaultdict(int)
    for r in rows:
        bucket = r["excluded_reason"] or "ELIGIBLE"
        if bucket.startswith("company in conversation"):
            bucket = "company in conversation (org-wide hold)"
        tally[bucket] += 1
    print(f"contacts: {len(rows)}  engaged companies: {len(engaged_orgs)}")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {v:5d}  {k}")
    json.dump(sorted(engaged_orgs), open(out_dir / "engaged_org_keys.json", "w"), indent=1)


if __name__ == "__main__":
    main()
