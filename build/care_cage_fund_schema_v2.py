"""care_cage_fund_schema_v2 — ADMIN-% fund-aware care/cage standard (the STL/Prop-P lesson, generalized).

LESSON ENCODED (STL-run, FY98-FY27, SPINOFF_IDEAS.md L2309-2310): St-Louis's Prop-P 2017
special sales tax funded parks care invisibly to the GF-only ratio (0.190->0.118 flat-to-down
through the Cortex/NGA revival era while care money arrived via special funds). CIN/OTR revival
money was private (ledger-invisible). NO's Library/NORD dedicated millages added to CARE.
Therefore: every city is scored through the same channel lens — Boston (GF-era), STL (Prop-P
era), NO (all-funds era) become like-for-like.
Provenance law: every dollar carries a source; estimates are labeled [Estimated].
"""
CHANNEL_TAXONOMY = {
    'GF':               'general fund operating (adopted-book GF columns)',
    'special_fund':     'voted levies (Prop-P 2017), named sales/millage taxes, care-relevant enterprise funds',
    'dedicated_millage':'library / home-repair millages (DET DPL fund 3001, NO Library 4.91 mills)',
    'federal_external': 'FEMA/HUD/CDBG care-BASIS capital — noted, never summed',
    'state_external':   'state caging grants (TN Gov.-Lee $100M MSTF fund) — noted, never summed',
    'private_external': '501(c)(3) revivals (3CDC, Cortex) — ledger-invisible, noted, NOT public care',
    'county_external':  'county-run jails/courts — noted with per-diem flows, not summed',
}
CARE_SUM = ('GF', 'special_fund', 'dedicated_millage')   # public care added to the ratio numerator
CAGE_SUM = ('GF', 'special_fund', 'dedicated_millage')   # public cage added to denominator
NOTED    = ('federal_external', 'state_external', 'private_external', 'county_external')


def care_total(rows):
    """rows = list of dicts {channel, usd, ...}. Federal care-capital noted, not summed."""
    return sum(r['usd'] for r in rows if r['channel'] in CARE_SUM)


def cage_total(rows):
    """State-cage external (e.g. TN $100M) noted, never summed into the city denominator."""
    return sum(r['usd'] for r in rows if r['channel'] in CAGE_SUM)


def ratio_pair(care_rows, cage_rows):
    """THE RATIO-PAIR OUTPUT — one lens for GF-era Boston, Prop-P-era STL, all-funds NO."""
    s = lambda chs, rows: sum(r['usd'] for r in rows if r['channel'] in chs)
    num_gf, den_gf = s(('GF',), care_rows), s(('GF',), cage_rows)
    num_gsp, den_gsp = s(CARE_SUM[:2], care_rows), s(CAGE_SUM[:2], cage_rows)
    notes = {ch: sum(r['usd'] for r in care_rows + cage_rows if r['channel'] == ch)
             for ch in NOTED}
    notes = {k: v for k, v in notes.items() if v} or 'none recorded'
    return {
        'gf_only_ratio':          round(num_gf / den_gf, 4) if den_gf else None,
        'gf_plus_special_ratio':  round(num_gsp / den_gsp, 4) if den_gsp else None,
        'all_public_ratio':       round(care_total(rows=care_rows) / cage_total(rows=cage_rows), 4) if cage_total(rows=cage_rows) else None,
        'total_incl_external_notes': notes,
    }


def demo_stl_fy19():
    """STL FY19 recompute: GF-only (banked, page-cited) vs fund-aware w/ Prop-P visible.
    Sources: FY19 AOP As Adopted (stlouis-mo.gov, S-49..S-52 + dept 3-yr PDFs p.3), rows inside
    stlouis_care_cage_series_v1.jsonl L14. GF care 30,089,560 / cage 254,577,601 [Certain].
    Prop-P parks special-fund share NOT extracted on the GF-only pass (row honest_gaps);
    carried as [Estimated] $5M central with a $3-7M band (one PDF-column pass away)."""
    gf_care = [{'channel': 'GF', 'usd': 30089560}]          # parks 21.4M + health 7.2M + HS 1.5M
    gf_cage = [{'channel': 'GF', 'usd': 254577601}]         # police+corrections+courts banked sum
    special_care = [{'channel': 'special_fund', 'usd': 5_000_000,
                     'note': 'Prop-P parks share [Estimated, band $3-7M] — 2017 parks sales tax, '
                             'all-funds-visible-only per STL-run MIXED-CHANNEL finding'}]
    notes = {'federal_external': 0, 'state_external': 0,
             'private_external': 'Cortex 501(c)(3) + NGA $1.7B federal construction — '
                                 'ledger-invisible, abatement-only exposure (banked ledger_class)',
             'county_external': 'StL County courts/jails via per-diem — not banked for FY19'}
    gf_only = ratio_pair(gf_care, gf_cage)['gf_only_ratio']
    print('=' * 74)
    print('STL FY19 CARE/CAGE — GF-only vs FUND-AWARE (Prop-P special funds visible)')
    print('=' * 74)
    print(f'  GF-only ratio      :  {gf_care[0]["usd"]:,} / {gf_cage[0]["usd"]:,} = {gf_only:.4f}'
          '   [Certain — FY19 AOP S-49..S-52, dept 3-yr tables p.3]')
    for est, lo, hi in ((5.0e6, 3.0e6, 7.0e6),):
        fa = ratio_pair(gf_care + [{'channel': 'special_fund', 'usd': est}], gf_cage)
        band = (ratio_pair(gf_care + [{'channel': 'special_fund', 'usd': lo}], gf_cage)['gf_plus_special_ratio'],
                ratio_pair(gf_care + [{'channel': 'special_fund', 'usd': hi}], gf_cage)['gf_plus_special_ratio'])
        print(f'  fund-aware ratio   :  {fa["gf_plus_special_ratio"]:.4f}   '
              f'[band {band[0]:.4f} @ $3M — {band[1]:.4f} @ $7M]  [Estimated — Prop-P $ not extracted]')
    print('  move               :  +{:>5.1%}  care-side lift invisible to the GF-only lens'
          .format(ratio_pair(gf_care + [{'channel': 'special_fund', 'usd': 5.0e6}], gf_cage)['gf_plus_special_ratio'] / gf_only - 1))
    print('  external notes     :  ' + str(notes))
    print('  source note        :  stlouis_care_cage_series_v1.jsonl FY19 row + FY19 AOP As Adopted')
    return {'gf_only': gf_only, 'fundaware_central': ratio_pair(gf_care + [{'channel': 'special_fund', 'usd': 5.0e6}], gf_cage)}


if __name__ == '__main__':
    demo_stl_fy19()
