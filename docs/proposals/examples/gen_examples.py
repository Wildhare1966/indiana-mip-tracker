# -*- coding: utf-8 -*-
"""Generate three illustrative 'Detailed Segment Summary' example docs as
Word-compatible HTML (mirrors index.html askExport styling). Saved as .doc (Word-compatible HTML). All content is illustrative (fictional hearing)."""
import os

VID = "WF-PC-20260519"  # illustrative video id


def ts(label):
    """[MM:SS] or [H:MM:SS] -> live youtube &t=Ns hyperlink, like tsLink()."""
    parts = [int(x) for x in label.split(":")]
    sec = parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]
    return ('<a href="https://www.youtube.com/watch?v=%s&amp;t=%ds">[%s]</a>'
            % (VID, sec, label))


STYLE = (
    'body{font-family:Calibri,sans-serif;font-size:11pt;color:#1a1a1a;line-height:1.5;}'
    'h1{font-size:16pt;color:#1e3a5f;border-bottom:2pt solid #e8a020;padding-bottom:4pt;margin-bottom:2pt;}'
    'h2{font-size:13pt;color:#1e3a5f;margin:14pt 0 4pt;border-bottom:1pt solid #edf0f4;padding-bottom:2pt;}'
    'h3{font-size:11.5pt;color:#1e3a5f;margin:11pt 0 3pt;}'
    'a{color:#1155cc;text-decoration:underline;}'
    '.banner{background:#fff4d6;border:1pt solid #e8a020;color:#7a5b00;font-size:9.5pt;padding:6pt 9pt;margin:0 0 12pt;}'
    '.sub{color:#4a5568;font-size:10pt;margin:2pt 0 4pt;}'
    '.hdr{font-size:10pt;color:#23344a;margin:1pt 0;}'
    '.hdr b{color:#1e3a5f;}'
    '.outcome{font-size:12pt;font-weight:bold;color:#14532d;background:#e8f5ec;border-left:3pt solid #1a7a4a;padding:6pt 9pt;margin:8pt 0;}'
    '.bottomline{background:#eef3fa;border-left:3pt solid #1e3a5f;padding:6pt 9pt;margin:8pt 0;}'
    'ul{margin:4pt 0 8pt 0;}li{margin:2pt 0;}'
    'table{border-collapse:collapse;width:100%;font-size:10pt;margin:6pt 0;}'
    'th,td{border:1pt solid #cdd6e0;padding:4pt 6pt;text-align:left;vertical-align:top;}'
    'th{background:#1e3a5f;color:#fff;font-size:9.5pt;}'
    'blockquote{margin:5pt 0 5pt 14pt;padding:3pt 0 3pt 10pt;border-left:2pt solid #cdd6e0;color:#33414f;font-style:italic;}'
    '.spk{font-style:normal;font-weight:bold;color:#1e3a5f;}'
    '.meta{color:#4a5568;font-size:9pt;border-top:1pt solid #edf0f4;padding-top:6pt;margin-top:18pt;}'
)

BANNER = ('<div class="banner"><b>DRAFT — illustrative example.</b> Structure proposal only. '
          'Built around a fictional Westfield, IN rezoning hearing to demonstrate the format; '
          'figures are not real and are pending validation against the 10-segment research study '
          '(see proposal &sect;5). Timestamp links are illustrative.</div>')

HEADER = (
    '<div class="hdr"><b>Project:</b> Maple Grove &mdash; residential PUD subdivision</div>'
    '<div class="hdr"><b>Jurisdiction / body:</b> City of Westfield, Hamilton County, IN &middot; Advisory Plan Commission</div>'
    '<div class="hdr"><b>Meeting date:</b> May 19, 2026</div>'
    '<div class="hdr"><b>Agenda item:</b> Docket 2605-PUD-04 &middot; Ordinance 26-15 (rezone AG-SF1 &rarr; PUD)</div>'
    '<div class="hdr"><b>Segment:</b> ' + ts("18:42") + '&ndash;' + ts("41:30")
    + ' &middot; <a href="https://www.youtube.com/watch?v=%s&amp;t=1122s">open video at segment start</a></div>' % VID
)

FOOTER = (
    '<p class="meta"><b>Sources:</b> '
    '<a href="https://www.youtube.com/watch?v=%s">Meeting recording (YouTube)</a> &middot; '
    '<a href="#">Agenda packet (PDF)</a> &middot; <a href="#">Staff report (PDF)</a><br>'
    'Detailed agenda-item summary &mdash; generated from the meeting transcript by MRD '
    '(Municipal Resource Dashboard), scoped to this project&rsquo;s agenda item. '
    'Timestamp links open the cited moment in the source video.</p>' % VID
)


def doc(title, sub, body):
    return (
        '<html xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:w="urn:schemas-microsoft-com:office:word" '
        'xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="utf-8">'
        '<title>%s</title><style>%s</style></head><body>'
        '<h1>%s</h1><p class="sub">%s</p>%s%s%s%s</body></html>'
        % (title, STYLE, title, sub, BANNER, HEADER, body, FOOTER)
    )


# ─────────────────────────────────────────────────────────────────────────────
# V1 — EXECUTIVE BRIEF
# ─────────────────────────────────────────────────────────────────────────────
v1_body = (
    '<div class="outcome">APPROVED 6&ndash;1 &mdash; favorable recommendation forwarded to City Council (June 8, 2026).</div>'
    '<h2>What happened</h2><ul>'
    '<li>Petitioner Arbor Homes sought to rezone ~62 acres from AG-SF1 to PUD for <b>184 single-family lots</b>. ' + ts("20:15") + '</li>'
    '<li>Planning staff recommended approval subject to conditions. ' + ts("18:42") + '</li>'
    '<li>Commissioner concerns centered on traffic at 161st &amp; Oak Rd and school capacity. ' + ts("27:50") + '</li>'
    '<li>Three residents spoke (2 opposed on traffic/schools, 1 in favor on housing need). ' + ts("33:10") + '</li>'
    '<li>Four conditions attached, incl. a traffic study before Council and a 20-ft tree buffer. ' + ts("38:05") + '</li>'
    '</ul>'
    '<h2>Vote</h2><p>6&ndash;1 favorable recommendation; lone dissent on traffic adequacy. '
    '(Roll call in V2/V3.) ' + ts("41:05") + '</p>'
    '<div class="bottomline"><b>Bottom line for MRD:</b> 184-lot Arbor Homes project clears Plan '
    'Commission with conditions and moves to Council on Jun 8 &mdash; track for the traffic-study '
    'outcome, which is the live gating risk before final approval.</div>'
)

# ─────────────────────────────────────────────────────────────────────────────
# V2 — STANDARD DETAILED SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
v2_body = (
    '<h2>Request</h2>'
    '<p>Arbor Homes LLC (Maple Grove Development Partners), represented by attorney Bill Reardon, '
    'requested a rezone of approximately <b>62 acres</b> at the northeast corner of 161st Street and '
    'Oak Road from <b>AG-SF1</b> (agricultural / single-family) to a <b>Planned Unit Development (PUD)</b> '
    'to permit <b>184 single-family lots</b> with a minimum lot width of 60 ft and roughly 12 acres of '
    'HOA-maintained open space. ' + ts("20:15") + '</p>'
    '<h2>Discussion</h2>'
    '<h3>Staff report</h3>'
    '<p>Planning Director Megan Foss summarized the petition and recommended <b>approval subject to '
    'conditions</b>, noting density (~3.0 units/acre) is consistent with the comprehensive plan&rsquo;s '
    'low-density residential designation. ' + ts("18:42") + '</p>'
    '<h3>Petitioner presentation</h3>'
    '<p>Reardon and engineer Priya Nair presented the concept plan, emphasizing the open-space network, '
    'a proposed trail stub to the Monon extension, and a price point Arbor positions as attainable '
    'move-up product. ' + ts("20:15") + '</p>'
    '<h3>Commissioner questions &amp; concerns</h3>'
    '<p>Commissioners pressed on the 161st &amp; Oak intersection capacity and on elementary-school '
    'enrollment. Commissioner Marcus Dunn questioned whether a traffic study should precede a favorable '
    'recommendation rather than follow it. ' + ts("27:50") + '</p>'
    '<h3>Public comment</h3>'
    '<p>Three residents spoke: two opposed (Karen Mills on cut-through traffic; David Cho on school '
    'capacity), one in favor (Susan Albright, citing local housing shortage). ' + ts("33:10") + '</p>'
    '<h2>Conditions &amp; commitments</h2><ul>'
    '<li>Traffic impact study completed before the City Council hearing, with any warranted improvements at 161st &amp; Oak Rd. ' + ts("38:20") + '</li>'
    '<li>20-ft tree-preservation buffer along the east property line. ' + ts("38:55") + '</li>'
    '<li>Pedestrian trail connection to the planned Monon extension. ' + ts("39:30") + '</li>'
    '<li>Minimum 12 acres of open space, HOA-maintained. ' + ts("39:50") + '</li>'
    '</ul>'
    '<h2>Motion &amp; vote</h2>'
    '<p>Commissioner Lena Park moved to forward Docket 2605-PUD-04 to the City Council with a '
    '<b>favorable recommendation</b>, subject to the four conditions; seconded by Commissioner Tom Becker. '
    'Motion carried <b>6&ndash;1</b> (Whitfield, Ortiz, Park, Becker, Reynolds, Halloran in favor; '
    'Dunn opposed). ' + ts("40:20") + '</p>'
    '<h2>Outcome &amp; next steps</h2>'
    '<p>Favorable recommendation forwarded to the <b>Westfield City Council</b>, tentatively scheduled '
    'for <b>June 8, 2026</b>. Final rezone requires Council adoption of Ordinance 26-15. ' + ts("41:05") + '</p>'
)

# ─────────────────────────────────────────────────────────────────────────────
# V3 — FULL DEEP-DIVE
# ─────────────────────────────────────────────────────────────────────────────
v3_index = (
    '<h2>Chronological timestamp index</h2>'
    '<table><tr><th>Time</th><th>Speaker / role</th><th>Topic</th></tr>'
    '<tr><td>' + ts("18:42") + '</td><td>M. Foss, Planning Director</td><td>Staff report &amp; recommendation</td></tr>'
    '<tr><td>' + ts("20:15") + '</td><td>B. Reardon, petitioner&rsquo;s attorney</td><td>Project overview</td></tr>'
    '<tr><td>' + ts("23:40") + '</td><td>P. Nair, engineer</td><td>Concept plan, open space, drainage</td></tr>'
    '<tr><td>' + ts("27:50") + '</td><td>Commissioners</td><td>Q&amp;A: traffic &amp; schools</td></tr>'
    '<tr><td>' + ts("31:05") + '</td><td>M. Dunn, Commissioner</td><td>Sequencing of traffic study</td></tr>'
    '<tr><td>' + ts("33:10") + '</td><td>Public</td><td>Public comment opens</td></tr>'
    '<tr><td>' + ts("38:05") + '</td><td>Commission</td><td>Condition deliberation</td></tr>'
    '<tr><td>' + ts("40:20") + '</td><td>L. Park / T. Becker</td><td>Motion &amp; second</td></tr>'
    '<tr><td>' + ts("41:05") + '</td><td>D. Whitfield, President</td><td>Roll-call vote</td></tr>'
    '</table>'
)
v3_proceedings = (
    '<h2>Request</h2>'
    '<p>Petition of Arbor Homes LLC / Maple Grove Development Partners (Docket <b>2605-PUD-04</b>, '
    'Ordinance <b>26-15</b>) to rezone approximately 62.0 acres (Parcel 29-09-..., NE corner 161st St &amp; '
    'Oak Rd) from <b>AG-SF1</b> to <b>PUD</b> for 184 detached single-family lots; min lot width 60 ft; '
    'min lot area 7,200 sf; ~12.1 ac open space; gross density ~3.0 du/ac. ' + ts("20:15") + '</p>'
    '<h2>Proceedings</h2>'
    '<h3>Staff report</h3>'
    '<p>Planning Director Megan Foss presented the staff analysis and a recommendation of approval with conditions. ' + ts("18:42") + '</p>'
    '<blockquote><span class="spk">Foss:</span> &ldquo;The proposed density is consistent with the '
    'low-density residential designation in the 2023 comprehensive plan. Staff&rsquo;s recommendation is '
    'favorable, conditioned on a traffic study and the buffering shown on sheet 4.&rdquo; ' + ts("19:55") + '</blockquote>'
    '<h3>Petitioner presentation</h3>'
    '<blockquote><span class="spk">Reardon:</span> &ldquo;This is attainable move-up product. We are '
    'committing to the Monon trail stub and to twelve acres of open space maintained by the HOA, not the '
    'City.&rdquo; ' + ts("21:30") + '</blockquote>'
    '<blockquote><span class="spk">Nair:</span> &ldquo;Stormwater is handled by two regional ponds; the '
    'east buffer preserves the existing tree line.&rdquo; ' + ts("24:10") + '</blockquote>'
    '<h3>Commissioner questions &amp; concerns</h3>'
    '<blockquote><span class="spk">Reynolds:</span> &ldquo;What is the trip count at 161st and Oak at '
    'build-out?&rdquo; <span class="spk">Nair:</span> &ldquo;A full study is pending; preliminary counts '
    'suggest a left-turn lane may be warranted.&rdquo; ' + ts("28:20") + '</blockquote>'
    '<blockquote><span class="spk">Dunn:</span> &ldquo;I&rsquo;m uncomfortable recommending approval '
    'before we see the traffic study, not after.&rdquo; ' + ts("31:05") + '</blockquote>'
    '<h3>Public comment</h3>'
    '<table><tr><th>Speaker</th><th>Position</th><th>Key point</th><th>Time</th></tr>'
    '<tr><td>Karen Mills</td><td>Against</td><td>Cut-through traffic on Oak Rd</td><td>' + ts("33:25") + '</td></tr>'
    '<tr><td>David Cho</td><td>Against</td><td>Elementary school at capacity</td><td>' + ts("35:10") + '</td></tr>'
    '<tr><td>Susan Albright</td><td>For</td><td>Local shortage of attainable housing</td><td>' + ts("36:40") + '</td></tr>'
    '</table>'
    '<h2>Conditions &amp; commitments (verbatim)</h2><ul>'
    '<li>&ldquo;A traffic impact study shall be completed and submitted prior to the City Council hearing, '
    'with improvements at 161st &amp; Oak Rd as warranted.&rdquo; ' + ts("38:20") + '</li>'
    '<li>&ldquo;A minimum twenty-foot tree-preservation buffer shall be maintained along the east property line.&rdquo; ' + ts("38:55") + '</li>'
    '<li>&ldquo;The developer shall construct a pedestrian connection to the planned Monon extension.&rdquo; ' + ts("39:30") + '</li>'
    '<li>&ldquo;No less than twelve acres of open space, maintained by the HOA.&rdquo; ' + ts("39:50") + '</li>'
    '</ul>'
    '<h2>Procedural notes</h2><ul>'
    '<li>No continuance; petition heard and acted on the same night. ' + ts("38:05") + '</li>'
    '<li>No recusals declared.</li>'
    '<li>Motion amended once to add the trail-connection condition before the vote. ' + ts("40:05") + '</li>'
    '</ul>'
    '<h2>Motion &amp; roll-call vote</h2>'
    '<p>Moved by Park, seconded by Becker: forward to Council with a favorable recommendation subject to '
    'the four conditions. ' + ts("40:20") + '</p>'
    '<table><tr><th>Member</th><th>Vote</th></tr>'
    '<tr><td>Dana Whitfield (President)</td><td>Aye</td></tr>'
    '<tr><td>Raymond Ortiz (Vice President)</td><td>Aye</td></tr>'
    '<tr><td>Lena Park</td><td>Aye</td></tr>'
    '<tr><td>Tom Becker</td><td>Aye</td></tr>'
    '<tr><td>Aisha Reynolds</td><td>Aye</td></tr>'
    '<tr><td>Greg Halloran</td><td>Aye</td></tr>'
    '<tr><td>Marcus Dunn</td><td>Nay</td></tr>'
    '</table>'
    '<p><b>Result: 6&ndash;1, favorable recommendation.</b> ' + ts("41:05") + '</p>'
    '<h2>Outcome &amp; next steps</h2>'
    '<p>Forwarded to Westfield City Council (tentative June 8, 2026) for action on Ordinance 26-15. '
    'Final rezone requires Council adoption. ' + ts("41:30") + '</p>'
    '<h2>Appendix</h2><ul>'
    '<li><b>Agenda item text:</b> &ldquo;Docket 2605-PUD-04 &mdash; Maple Grove PUD, rezone ~62 ac AG-SF1 to PUD, 184 lots.&rdquo;</li>'
    '<li><b>Ordinance reference:</b> 26-15.</li>'
    '<li><b>Related prior hearings:</b> Technical Advisory Committee review (Apr 30, 2026); concept '
    'pre-application (Mar 2026).</li>'
    '</ul>'
)

OUT = os.path.dirname(os.path.abspath(__file__))
files = {
    "v1-executive-brief.html": doc(
        "Maple Grove &mdash; Executive Brief",
        "Detailed segment summary &middot; Version 1 of 3 (Executive Brief)",
        v1_body),
    "v2-standard-detailed.html": doc(
        "Maple Grove &mdash; Standard Detailed Summary",
        "Detailed segment summary &middot; Version 2 of 3 (Standard Detailed)",
        v2_body),
    "v3-full-deep-dive.html": doc(
        "Maple Grove &mdash; Full Deep-Dive",
        "Detailed segment summary &middot; Version 3 of 3 (Full Deep-Dive)",
        v3_index + v3_proceedings),
}
for name, html in files.items():
    out_name = name.replace(".html", ".doc")
    with open(os.path.join(OUT, out_name), "w", encoding="utf-8") as f:
        f.write("\ufeff" + html)  # BOM, matching the app's askExport blob
    print("wrote", out_name, len(html), "bytes")
