#!/usr/bin/env python3
"""Preregistered V148 analysis for the single RAC pilot; no platform calls."""
import math, hashlib, json

Z95=1.959963984540054

def analyze_pilot_counts(counts):
    clean={}
    for key,value in counts.items():
        bits=''.join(str(key).split())
        if bits not in {'00','01','10','11'}: raise ValueError('pilot counts require two-bit keys')
        if type(value) is not int:
            raise ValueError('counts must be integer JSON numbers; bool/float/string forbidden')
        n=value
        if n<0: raise ValueError('negative count')
        clean[bits]=clean.get(bits,0)+n
    canonical={k:clean.get(k,0) for k in ['00','01','10','11']}
    n=sum(canonical.values())
    base={'schema':'lgt.quafu.rac.pilot.analysis.v1','counts':canonical,
          'counts_sha256':hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest(),
          'shots_returned':n,'S_real_pilot':None,'scope':'single RAC cell x1=1,x2=1,basis=X; not eight-cell S_real'}
    if n==0:
        base.update({'status':'EMPTY','reason':'no counts; no score computed'})
        return base
    odd=canonical['01']+canonical['10']; even=canonical['00']+canonical['11']
    s=odd/n; z2=Z95*Z95; den=1+z2/n; center=(s+z2/(2*n))/den
    half=Z95*math.sqrt(s*(1-s)/n+z2/(4*n*n))/den
    if odd:
        chi2=(canonical['01']-canonical['10'])**2/odd
        p=math.erfc(math.sqrt(chi2/2)); balance=(canonical['01']-canonical['10'])/odd
    else:
        chi2=None; p=None; balance=None
    ideal={'00':0.0,'01':0.5,'10':0.5,'11':0.0}
    tv=0.5*sum(abs(canonical[k]/n-ideal[k]) for k in canonical)
    base.update({'status':'OK','target_parity':1,'hits':odd,'parity_errors':even,
                 'S_real_pilot':s,'S_sim_pilot':1.0,'delta_sim_minus_real':1.0-s,
                 'S_wilson95':[max(0.0,center-half),min(1.0,center+half)],
                 'even_error_rate':even/n,'odd_conditional_balance_D':balance,
                 'odd_balance_chi2_df1':chi2,'odd_balance_p':p,
                 'total_variation_to_ideal':tv,
                 'ideal_distribution':ideal,'shots_preregistered':1024,'shots_match_preregistered':n==1024,
                 'interpretation':'descriptive single-cell comparison; no eight-cell or QRAND inference'})
    return base
