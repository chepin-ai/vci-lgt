#!/usr/bin/env python3
import json, math
from fractions import Fraction
from scipy.stats import chisquare
from quafu_rac_analysis import analyze_pilot_counts
cases=[
 ('sim_known',{'01':513,'10':511},1,0,Fraction(1,1024)),
 ('uniform',{'00':250,'01':250,'10':250,'11':250},Fraction(1,2),Fraction(1,2),Fraction(1,2)),
 ('all_even',{'00':1024},0,1,1),
 ('single_odd',{'01':1024},1,0,Fraction(1,2)),
 ('mixed',{'00':24,'01':600,'10':400},Fraction(1000,1024),Fraction(24,1024),Fraction(112,1024))]
rows=[]; scipy_errors=[]
for name,counts,s,e,tv in cases:
    a=analyze_pilot_counts(counts); n=sum(counts.values()); odd=counts.get('01',0)+counts.get('10',0)
    assert Fraction(a['hits'],n)==s and Fraction(a['parity_errors'],n)==e
    assert abs(a['S_real_pilot']-float(s))<1e-15 and abs(a['even_error_rate']-float(e))<1e-15
    assert abs(a['total_variation_to_ideal']-float(tv))<1e-15,(name,a['total_variation_to_ideal'],float(tv))
    if odd:
        sp=float(chisquare([counts.get('01',0),counts.get('10',0)]).pvalue)
        scipy_errors.append(abs(sp-a['odd_balance_p']))
        assert abs(sp-a['odd_balance_p'])<1e-14
    rows.append({'case':name,'counts':a['counts'],'S':a['S_real_pilot'],'even_error_rate':a['even_error_rate'],
                 'TV':a['total_variation_to_ideal'],'odd_balance_p':a['odd_balance_p'],'wilson95':a['S_wilson95'],'pass':True})
empty=analyze_pilot_counts({}); assert empty['status']=='EMPTY' and empty['S_real_pilot'] is None
invalid_rejected=False
try: analyze_pilot_counts({'1':10})
except ValueError: invalid_rejected=True
assert invalid_rejected
out={'schema':'lgt.quafu.rac.analyzer.selfcert.v1','known_answers':rows,'empty_counts_rejected_from_scoring':True,
     'invalid_bitstring_rejected':invalid_rejected,'scipy_df1_crosscheck_max_abs_error':max(scipy_errors),
     'independent_exact_TV':'fractions.Fraction expected values','verdict':'PASS','platform_calls':0,'quantum_jobs':0}
print(json.dumps(out,ensure_ascii=False,indent=2))
