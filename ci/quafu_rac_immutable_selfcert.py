#!/usr/bin/env python3
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

W=Path(__file__).resolve().parent
sys.path.insert(0,str(W))
import quafu_rac_immutable as im
import quafu_rac_analysis as an

checks={}
known=[{}, {'00':0,'01':513,'10':511,'11':0}, {'00':24,'01':600,'10':400,'11':0}, {'00':250,'01':250,'10':250,'11':250}]
hash_cross=[]
for counts in known:
    a=im.counts_sha256(counts); b=an.analyze_pilot_counts(counts)['counts_sha256']
    hash_cross.append({'counts':im.canonical_counts(counts),'immutable_sha256':a,'analyzer_sha256':b,'match':a==b})
assert all(x['match'] for x in hash_cross)
checks['counts_hash_crosscheck']=hash_cross

def history_with(statuses_counts):
    h={'schema':im.SCHEMA,'task_id':'T','snapshots':[]}
    for i,(status,counts) in enumerate(statuses_counts,1):
        s=im.make_snapshot(i,'T',status,counts,f'receipts/{i}.json',f'synthetic-{i}',f'2026-01-01T00:00:{i:02d}Z')
        h=im.append_snapshot(h,s)
    return h

h0=history_with([('In Queue',{}),('In Queue',{})])
assert h0['audit']['status']=='NO_COMPLETED'
h1=history_with([('In Queue',{}),('Completed',{'01':513,'10':511})])
assert h1['audit']['status']=='FIRST_COMPLETED'
h2=history_with([('Completed',{'01':513,'10':511}),('Completed',{'01':513,'10':511})])
assert h2['audit']['status']=='IMMUTABLE_OK' and h2['audit']['scoring_allowed']
h3=history_with([('Completed',{'01':513,'10':511}),('Completed',{'01':512,'10':512})])
assert h3['audit']['status']=='IMMUTABLE_VIOLATION' and h3['audit']['immutable_violation'] and not h3['audit']['scoring_allowed']
checks['module_status_transitions']=[h0['audit']['status'],h1['audit']['status'],h2['audit']['status'],h3['audit']['status']]
h=dict(h1); before=len(h['snapshots']); snap=h['snapshots'][-1]
h=im.append_snapshot(h,snap); assert len(h['snapshots'])==before
bad=dict(snap); bad['counts']={'00':0,'01':512,'10':512,'11':0}
try:
    im.append_snapshot(h,bad); raise AssertionError('conflicting duplicate run accepted')
except ValueError: pass
tampered=json.loads(json.dumps(h1)); tampered['snapshots'][-1]['counts']['01']=512
try:
    im.audit_history(tampered); raise AssertionError('tampered history accepted')
except ValueError: pass
try:
    im.append_snapshot(h1,im.make_snapshot(9,'OTHER','In Queue',{},'x','y','z')); raise AssertionError('cross-task accepted')
except ValueError: pass
checks['tamper_and_contamination_rejected']=True

with tempfile.TemporaryDirectory(prefix='lgt-immutable-selfcert-') as td:
    root=Path(td); (root/'ci').mkdir(); (root/'receipts').mkdir(); (root/'quafu').mkdir()
    for name in ['QUAFU-RAC-PREFLIGHT-LGT-01.json','quafu_rac_analysis.py','quafu_rac_immutable.py','realchip_quafu_rac.py']:
        shutil.copy(W/name,root/'ci'/name)
    shutil.copy(W/'QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json',root/'ci'/'QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json')
    (root/'quafu'/'__init__.py').write_text('''import json, os\nfrom types import SimpleNamespace\nclass QuantumCircuit:\n    pass\ndef simulate(*a,**k):\n    raise RuntimeError("offline selfcert: simulate forbidden")\nclass User:\n    def __init__(self,key): self.authenticated=bool(key)\nclass Task:\n    def __init__(self,user): assert user.authenticated\n    def retrieve(self,tid):\n        counts=json.loads(os.environ.get("STUB_COUNTS","{}"))\n        return SimpleNamespace(taskid=str(tid),task_status=os.environ["STUB_STATUS"],taskname="SELFTEST",logicalq_res=counts,counts=counts)\n    def send(self,*a,**k):\n        open(os.environ["STUB_SEND_MARKER"],"w").write("SEND_FORBIDDEN")\n        raise RuntimeError("offline selfcert: send forbidden")\n''')
    send_marker=root/'SEND_CALLED'
    cases=[]
    def run_case(rid,status,counts):
        env=os.environ.copy(); env.update({'MODE':'RETRIEVE','TASK_ID':'91C842B01A238734','QUAFU_KEY':'synthetic-offline-selfcert',
            'GITHUB_RUN_ID':str(rid),'RECEIPT_PATH':f'receipts/selfcert-{rid}.json','STUB_STATUS':status,
            'STUB_COUNTS':json.dumps(counts),'STUB_SEND_MARKER':str(send_marker),'PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1'})
        cp=subprocess.run(['python3',str(root/'ci'/'realchip_quafu_rac.py')],cwd=root,env=env,capture_output=True,text=True,timeout=60)
        receipt=json.loads((root/'receipts'/f'selfcert-{rid}.json').read_text())
        history=json.loads((root/'ci'/'QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json').read_text())
        row={'run_id':rid,'input_status':status,'input_counts':counts,'returncode':cp.returncode,'ok':receipt['ok'],
             'S_real_pilot':receipt['S_real_pilot'],'send_attempts':receipt['send_attempts'],
             'new_quantum_jobs_confirmed':receipt['new_quantum_jobs_confirmed'],'history_audit':history['audit'],
             'analysis_present':'analysis' in receipt.get('retrieval',{}),'error_type':receipt.get('error',{}).get('type')}
        cases.append(row)
        return cp,receipt,history
    cp,r,h=run_case(9001,'In Queue',{})
    assert cp.returncode==0 and r['S_real_pilot'] is None and h['audit']['status']=='NO_COMPLETED' and len(h['snapshots'])==4
    cp,r,h=run_case(9002,'Completed',{'01':513,'10':511})
    assert cp.returncode==0 and r['S_real_pilot']==1.0 and h['audit']['status']=='FIRST_COMPLETED'
    assert r['retrieval']['analysis']['shots_returned']==1024 and r['retrieval']['analysis']['shots_match_preregistered']
    first_hash=r['retrieval']['counts_sha256']
    cp,r,h=run_case(9003,'Completed',{'01':513,'10':511})
    assert cp.returncode==0 and r['S_real_pilot']==1.0 and h['audit']['status']=='IMMUTABLE_OK'
    assert r['retrieval']['counts_sha256']==first_hash and h['audit']['completed_snapshots']==2
    cp,r,h=run_case(9004,'Completed',{'01':512,'10':512})
    assert cp.returncode==1 and not r['ok'] and r['S_real_pilot'] is None
    assert 'analysis' not in r['retrieval'] and r['retrieval']['counts']=={'01':512,'10':512}
    assert h['audit']['status']=='IMMUTABLE_VIOLATION' and h['audit']['immutable_violation'] and len(h['audit']['distinct_completed_counts_sha256'])==2
    assert r['error']['type']=='RuntimeError'
    assert not send_marker.exists()
    assert all(c['send_attempts']==0 and c['new_quantum_jobs_confirmed']==0 for c in cases)
    checks['production_integration']={'mode':'offline_known_answer_stub','cases':cases,'send_called':False}

prod=(W/'realchip_quafu_rac.py').read_text()
wf_path=W/'realchip-quafu-rac-01.yml'
if not wf_path.exists(): wf_path=W.parent/'.github'/'workflows'/'realchip-quafu-rac-01.yml'
wf=wf_path.read_text()
assert len(re.findall(r'\.send\(',prod))==1
assert prod.index('SPENT_PATH.exists()')<prod.index('user=User(KEY)')<prod.index('res=task.send(')
assert prod.index('record_retrieval(receipt')<prod.index('score_completed_result(receipt')
assert prod.index("if history['audit']['immutable_violation']:")<prod.index('score_completed_result(receipt')
assert 'git add "$RECEIPT_PATH" ci/QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json' in wf
checks['static_integration']={'single_send_call':True,'spent_guard_before_auth_and_send':True,
    'history_before_scoring':True,'violation_before_scoring':True,'history_committed_and_uploaded':True}
ts_path=W/'TS_PLAN'
out={'schema':'lgt.quafu.rac.immutable-selfcert.v1','beat':'V-149','ts':ts_path.read_text().strip() if ts_path.exists() else None,
     'verdict':'PASS','checks':checks,'real_platform_calls':0,'real_quantum_jobs':0,
     'analyzer_used_on_real_counts':False,'real_task_status_at_v149_retrieval':'In Queue',
     'scope':'Offline known-answer validation only; no claim about real counts or eight-cell RAC/QRAND',
     'weakening':'Conflict path tested offline against production code; no second FIRE and no additional real retrieval were used for testing'}
(W/'QUAFU-RAC-IMMUTABLE-SELFCERT-LGT-01.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print(json.dumps({'verdict':out['verdict'],'module_status_transitions':checks['module_status_transitions'],
                  'integration_statuses':[c['history_audit']['status'] for c in checks['production_integration']['cases']],
                  'returncodes':[c['returncode'] for c in checks['production_integration']['cases']],
                  'real_platform_calls':0,'real_quantum_jobs':0},ensure_ascii=False,indent=2))
