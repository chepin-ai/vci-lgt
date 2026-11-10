#!/usr/bin/env python3
import json, math, os, random, re, shutil, subprocess, sys, tempfile
from fractions import Fraction
from pathlib import Path
from scipy.stats import binomtest, chi2 as chi2_dist

W=Path(__file__).resolve().parent
sys.path.insert(0,str(W))
import quafu_rac_immutable as im
import quafu_rac_analysis as an

checks={}
# Independent statistical properties, not production helper reuse.
rng=random.Random(151)
max_wilson=0.0; max_p=0.0; max_tv=0.0
for i in range(512):
    n=rng.choice([1,2,3,4,7,16,31,64,100,255,512,1024])
    vals=[rng.randint(0,n) for _ in range(4)]
    scale=n/max(1,sum(vals))
    counts={k:int(vals[j]*scale) for j,k in enumerate(['00','01','10','11'])}
    if sum(counts.values())==0: counts['01']=1
    out=an.analyze_pilot_counts(counts)
    n=sum(counts.values()); odd=counts['01']+counts['10']; even=n-odd
    assert out['S_real_pilot']==odd/n and out['hits']==odd and out['parity_errors']==even
    ci=binomtest(odd,n).proportion_ci(confidence_level=0.95,method='wilson')
    max_wilson=max(max_wilson,abs(out['S_wilson95'][0]-ci.low),abs(out['S_wilson95'][1]-ci.high))
    if odd:
        x=(counts['01']-counts['10'])**2/odd
        max_p=max(max_p,abs(out['odd_balance_p']-chi2_dist.sf(x,1)))
    exact=Fraction(1,2)*sum(abs(Fraction(counts[k],n)-v) for k,v in [('00',0),('01',Fraction(1,2)),('10',Fraction(1,2)),('11',0)])
    max_tv=max(max_tv,abs(out['total_variation_to_ideal']-float(exact)))
assert max_wilson<1e-12 and max_p<1e-12 and max_tv<1e-15,(max_wilson,max_p,max_tv)
checks['statistical_property_test']={'random_cases':512,'seed':151,'max_wilson_abs_error':max_wilson,
    'max_chi2_p_abs_error':max_p,'max_exact_tv_abs_error':max_tv,'independent_reference':'SciPy binomtest Wilson + chi2.sf + Fraction TV'}

# Strict count typing in both independent implementations.
invalid_values=[1.5,True,'2',-1,None]
strict=[]
for value in invalid_values:
    for name,fn in [('immutable',im.canonical_counts),('analyzer',an.analyze_pilot_counts)]:
        try:
            fn({'01':value,'10':2}); raise AssertionError((name,value,'accepted'))
        except (ValueError,TypeError): strict.append({'implementation':name,'value_type':type(value).__name__,'value':str(value),'rejected':True})
checks['strict_count_typing']=strict
# Canonical equivalence and terminal-state mutation tests.
def hist(seq):
    h={'schema':im.SCHEMA,'task_id':'T','snapshots':[]}
    for i,(status,counts) in enumerate(seq,1):
        h=im.append_snapshot(h,im.make_snapshot(i,'T',status,counts,f'receipts/{i}.json',f'x{i}',f't{i}'))
    return h
assert im.counts_sha256({'01':513,'10':511})==im.counts_sha256({'10':511,' 01 ':513})
for seq in [
    [('Completed',{'01':513,'10':511}),('In Queue',{})],
    [('Failed',{}),('Completed',{'01':513,'10':511})],
    [('Canceled',{}),('Running',{})]]:
    h=hist(seq); a=h['audit']
    assert a['status']=='IMMUTABLE_VIOLATION' and a['terminal_status_violation'] and a['immutable_violation'] and not a['scoring_allowed']
checks['terminal_regression_mutations']='PASS'
# Prior V149 module regressions.
h0=hist([('In Queue',{}),('In Queue',{})]); h1=hist([('In Queue',{}),('Completed',{'01':513,'10':511})])
h2=hist([('Completed',{'01':513,'10':511}),('Completed',{'01':513,'10':511})])
h3=hist([('Completed',{'01':513,'10':511}),('Completed',{'01':512,'10':512})])
assert [h['audit']['status'] for h in [h0,h1,h2,h3]]==['NO_COMPLETED','FIRST_COMPLETED','IMMUTABLE_OK','IMMUTABLE_VIOLATION']
checks['v149_module_regression']='PASS'

# Offline execution of the actual production script with independent known-answer roots.
with tempfile.TemporaryDirectory(prefix='lgt-v151-selfcert-') as td:
    base=Path(td); markers=[]
    def make_root(name):
        root=base/name; (root/'ci').mkdir(parents=True); (root/'receipts').mkdir(); (root/'quafu').mkdir()
        for fn in ['QUAFU-RAC-PREFLIGHT-LGT-01.json','quafu_rac_analysis.py','quafu_rac_immutable.py','realchip_quafu_rac.py']:
            shutil.copy(W/fn,root/'ci'/fn)
        shutil.copy(W/'QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json',root/'ci'/'QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json')
        (root/'quafu'/'__init__.py').write_text('''import json, os\nfrom types import SimpleNamespace\nclass QuantumCircuit:\n    pass\ndef simulate(*a,**k):\n    raise RuntimeError("offline selfcert: simulate forbidden")\nclass User:\n    def __init__(self,key): self.authenticated=bool(key)\nclass Task:\n    def __init__(self,user): assert user.authenticated\n    def retrieve(self,tid):\n        counts=json.loads(os.environ.get("STUB_COUNTS","{}"))\n        return SimpleNamespace(taskid=str(tid),task_status=os.environ["STUB_STATUS"],taskname="SELFTEST",logicalq_res=counts,counts=counts)\n    def send(self,*a,**k):\n        open(os.environ["STUB_SEND_MARKER"],"w").write("SEND_FORBIDDEN")\n        raise RuntimeError("offline selfcert: send forbidden")\n''')
        markers.append(root/'SEND_CALLED')
        return root
    def run(root,rid,status,counts):
        env=os.environ.copy(); env.update({'MODE':'RETRIEVE','TASK_ID':'91C842B01A238734','QUAFU_KEY':'synthetic-offline-v151',
          'GITHUB_RUN_ID':str(rid),'RECEIPT_PATH':f'receipts/selfcert-{rid}.json','STUB_STATUS':status,
          'STUB_COUNTS':json.dumps(counts),'STUB_SEND_MARKER':str(root/'SEND_CALLED'),'PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1'})
        cp=subprocess.run(['python3',str(root/'ci'/'realchip_quafu_rac.py')],cwd=root,env=env,capture_output=True,text=True,timeout=60)
        rec=json.loads((root/'receipts'/f'selfcert-{rid}.json').read_text())
        history=json.loads((root/'ci'/'QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json').read_text())
        return cp,rec,history
    # A: V149 full regression, including canonical counts conflict.
    root=make_root('regression'); rows=[]
    for rid,status,counts in [(9001,'In Queue',{}),(9002,'Completed',{'01':513,'10':511}),(9003,'Completed',{'01':513,'10':511}),(9004,'Completed',{'01':512,'10':512})]:
        cp,rec,h=run(root,rid,status,counts)
        rows.append({'rid':rid,'returncode':cp.returncode,'audit':h['audit']['status'],'S':rec['S_real_pilot'],'analysis_present':'analysis' in rec.get('retrieval',{})})
    assert [r['returncode'] for r in rows]==[0,0,0,1] and [r['audit'] for r in rows]==['NO_COMPLETED','FIRST_COMPLETED','IMMUTABLE_OK','IMMUTABLE_VIOLATION']
    assert rows[-1]['S'] is None and not rows[-1]['analysis_present']
    checks['production_v149_regression']=rows
    # B: canonical equivalent counts remain immutable; shots mismatch is explicit.
    root=make_root('canonical'); cp,r1,h=run(root,9101,'Completed',{'01':513,'10':511}); assert cp.returncode==0
    cp,r2,h=run(root,9102,'Completed',{'10':511,' 01 ':513})
    assert cp.returncode==0 and h['audit']['status']=='IMMUTABLE_OK' and r2['S_real_pilot']==1.0
    root=make_root('shots'); cp,r,h=run(root,9103,'Completed',{'01':60,'10':40})
    assert cp.returncode==0 and r['S_real_pilot']==1.0 and r['retrieval']['shots_returned']==100 and not r['retrieval']['analysis']['shots_match_preregistered']
    checks['canonical_equivalence_and_shots_mismatch']='PASS'
    # C: terminal regression after a real-looking Completed result is forbidden.
    root=make_root('terminal'); cp,r,h=run(root,9201,'Completed',{'01':513,'10':511}); assert cp.returncode==0
    cp,r,h=run(root,9202,'In Queue',{})
    assert cp.returncode==1 and r['S_real_pilot'] is None and h['audit']['terminal_status_violation'] and not h['audit']['counts_immutable_violation']
    checks['production_terminal_regression']={'returncode':cp.returncode,'audit':h['audit'],'score':r['S_real_pilot']}
    # D: each malformed count is rejected by the production path without a score.
    malformed=[]
    for j,value in enumerate(invalid_values):
        root=make_root(f'invalid{j}'); cp,r,h=run(root,9300+j,'Completed',{'01':value,'10':2})
        malformed.append({'value_type':type(value).__name__,'returncode':cp.returncode,'error_type':r.get('error',{}).get('type'),'score':r['S_real_pilot']})
        assert cp.returncode==1 and r['S_real_pilot'] is None and r['error']['type'] in {'ValueError','TypeError'}
    checks['production_malformed_counts']=malformed
    # D2: a terminal Completed with no positive shots is evidence, never a successful run.
    empty_completed=[]
    for j,counts in enumerate([{}, {'00':0,'01':0,'10':0,'11':0}]):
        root=make_root(f'emptyCompleted{j}'); cp,r,h=run(root,9350+j,'Completed',counts)
        row={'case':'empty' if not counts else 'all_zero','returncode':cp.returncode,'receipt_ok':r['ok'],
             'error_type':r.get('error',{}).get('type'),'score':r['S_real_pilot'],
             'analysis_present':'analysis' in r.get('retrieval',{}),'audit':h['audit']['status'],
             'completed_snapshots':h['audit']['completed_snapshots']}
        empty_completed.append(row)
        assert cp.returncode==1 and not r['ok'] and r['S_real_pilot'] is None
        assert r['error']['type']=='RuntimeError' and not row['analysis_present']
        assert h['audit']['status']=='FIRST_COMPLETED' and h['audit']['completed_snapshots']==1
    checks['production_completed_without_positive_shots']=empty_completed
    # E: unknown status is preserved then rejected; Failed/Canceled are negative, never scored.
    root=make_root('unknown'); cp,r,h=run(root,9401,'Mystery',{})
    assert cp.returncode==1 and r['S_real_pilot'] is None and r['retrieval']['task_status']=='Mystery' and not r['retrieval']['status_known']
    checks['unknown_status_fail_closed']=True
    negatives=[]
    for j,status in enumerate(['Failed','Canceled']):
        root=make_root(f'negative{j}'); cp,r,h=run(root,9410+j,status,{})
        assert r['S_real_pilot'] is None and not r['ok'] and 'analysis' not in r['retrieval']
        negatives.append({'status':status,'returncode':cp.returncode,'receipt_ok':r['ok'],'score':r['S_real_pilot']})
    checks['negative_terminal_states']=negatives
    assert all(not m.exists() for m in markers)
    checks['send_called']=False

prod=(W/'realchip_quafu_rac.py').read_text(); wf_path=W/'realchip-quafu-rac-01.yml'
if not wf_path.exists(): wf_path=W.parent/'.github'/'workflows'/'realchip-quafu-rac-01.yml'
wf=wf_path.read_text()
assert len(re.findall(r'\.send\(',prod))==1
assert prod.index('SPENT_PATH.exists()')<prod.index('user=User(KEY)')<prod.index('res=task.send(')
assert prod.index('record_retrieval(receipt')<prod.index('score_completed_result(receipt')
assert prod.index("if history['audit']['immutable_violation']:")<prod.index('score_completed_result(receipt')
assert 'unknown task status' in prod and "type(v) is not int" in prod
assert 'Completed returned empty counts' in prod and 'Completed returned zero shots' in prod and "analysis.get('status')!='OK'" in prod
checks['static_guards']={'one_send':True,'spent_before_auth':True,'immutable_before_score':True,'unknown_status_guard':True,'strict_score_counts':True,'completed_positive_shots_guard':True}
ts_path=W/'TS_PLAN'
out={'schema':'lgt.quafu.rac.v151-selfcert.v1','beat':'V-151','ts':ts_path.read_text().strip() if ts_path.exists() else '2026-11-10T05:12:34Z',
 'verdict':'PASS','checks':checks,'real_platform_calls':0,'real_quantum_jobs':0,'analyzer_used_on_real_counts':False,
 'real_task_status_observed_by_selfcert':None,
 'scope':'Offline mutation/property/production-path validation only; no real-chip result claim',
 'weakening':'Malformed, empty-completed, terminal-regression and unknown-status paths are synthetic known-answer tests; the real task is not accessed by selfcert'}
(W/'QUAFU-RAC-V151-SELFCERT-LGT-01.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print(json.dumps({'verdict':'PASS','random_cases':512,'max_wilson_abs_error':max_wilson,'max_chi2_p_abs_error':max_p,
 'max_exact_tv_abs_error':max_tv,'v149_returncodes':[r['returncode'] for r in checks['production_v149_regression']],
 'strict_count_cases':len(strict),'malformed_production_cases':len(malformed),'empty_completed_cases':len(empty_completed),'real_platform_calls':0,'real_quantum_jobs':0},ensure_ascii=False,indent=2))
