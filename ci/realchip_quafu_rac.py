#!/usr/bin/env python3
"""V147 Quafu RAC pilot: local simulation gate; at most one real Task.send."""
import os, sys, json, hashlib, datetime, re
from pathlib import Path
from scipy.stats import chisquare
from quafu import QuantumCircuit, simulate, User

MODE=os.environ.get('MODE','SIM').upper()
ROOT=Path.cwd()
PREREG=json.loads((ROOT/'ci/QUAFU-RAC-PREFLIGHT-LGT-01.json').read_text())
RECEIPT=Path(os.environ.get('RECEIPT_PATH','receipts/quafu-rac-receipt.json'))
NOW=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
KEY=os.environ.get('QUAFU_KEY','')
R=PREREG['real_submission']; P=PREREG['pilot']; G=PREREG['local_simulation_gate']
receipt={'schema':'lgt.quafu.rac.receipt.v1','experiment_id':PREREG['experiment_id'],'mode':MODE,
         'started_utc':NOW,'sdk':PREREG['sdk'],'prereg_sha256':hashlib.sha256(json.dumps(PREREG,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
         'new_quantum_jobs_confirmed':0,'send_attempts':0,'new_quantum_jobs_uncertain':False,
         'S_real_pilot':None,'task_id':None,'ok':False}

def save():
    RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+'\n')

def clean_error(exc):
    s=str(exc)
    if KEY: s=s.replace(KEY,'[REDACTED]')
    s=re.sub(r'(?i)(api_token["\']?\s*[:=]\s*["\']?)[^,"\'\s}]+',r'\1[REDACTED]',s)
    return {'type':type(exc).__name__,'message':s[:1200]}

def fresh_rac(x1,x2,basis):
    q=QuantumCircuit(2)
    q.h(0); q.cnot(0,1)
    if x1: q.x(0)
    if x2: q.z(0)
    if basis=='X': q.h(0); q.h(1)
    elif basis!='Z': raise ValueError('basis must be X or Z')
    q.measure([0,1],[0,1])
    return q

def bits2(s):
    s=''.join(str(s).split())
    if len(s)!=2 or set(s)-{'0','1'}: raise ValueError('expected two-bit string')
    return int(s[0]),int(s[1])  # PyQuafu big-endian: q0 is leftmost.

def score_counts(counts,want):
    total=sum(int(v) for v in counts.values())
    if total<=0: return None,0,0
    hit=0
    for k,v in counts.items():
        q0,q1=bits2(k)
        if (q0^q1)==want: hit+=int(v)
    return hit/total,hit,total

def local_gate():
    known=[]
    for case in G['bit_mapping_known_answers']:
        q=QuantumCircuit(2)
        q.x(0 if case['prepare']=='X(0)' else 1); q.measure([0,1],[0,1])
        counts=simulate(q,shots=64).counts
        known.append({'prepare':case['prepare'],'expected':case['expected'],'counts':counts,
                      'pass':counts=={case['expected']:64}})
    cells=[]
    for basis in ['Z','X']:
        for x1 in [0,1]:
            for x2 in [0,1]:
                q=fresh_rac(x1,x2,basis); want=x1 if basis=='Z' else x2
                counts=simulate(q,shots=G['shots_per_cell']).counts
                s,hit,total=score_counts(counts,want)
                cells.append({'basis':basis,'x1':x1,'x2':x2,'want_parity':want,'counts':counts,
                              'S':s,'hits':hit,'shots':total,'pass':s is not None and s>=G['S_sim_min'] and total==G['shots_per_cell']})
    qr=QuantumCircuit(G['qrand']['qubits'])
    for i in range(G['qrand']['qubits']): qr.h(i)
    qr.measure(list(range(G['qrand']['qubits'])),list(range(G['qrand']['qubits'])))
    qc=simulate(qr,shots=G['qrand']['shots']).counts
    observed=[int(qc.get(format(i,'08b'),0)) for i in range(256)]
    chi=chisquare(observed)
    mapping_pass=all(x['pass'] for x in known)
    sim_pass=mapping_pass and all(c['pass'] for c in cells) and float(chi.pvalue)>=G['qrand']['chi2_p_min'] and sum(observed)==G['qrand']['shots']
    return {'bit_mapping':{'convention':'big-endian; q0=leftmost','known_answers':known,'pass':mapping_pass},
            'rac_cells':cells,'S_sim_min_observed':min(c['S'] for c in cells),
            'qrand_local':{'counts':qc,'shots':sum(observed),'chi2':float(chi.statistic),'df':255,'p':float(chi.pvalue),
                           'pass':float(chi.pvalue)>=G['qrand']['chi2_p_min'],'real_chip_submission':False},'pass':sim_pass}

def backend_snapshot(user):
    raw=user.get_available_backends(print_info=False)
    rows=[]
    iterable=raw.items() if isinstance(raw,dict) else enumerate(raw)
    for key,b in iterable:
        info=b if isinstance(b,dict) else None
        def field(names):
            for n in names:
                v=info.get(n) if info is not None else getattr(b,n,None)
                if v is not None: return v
            return None
        name=field(['name','backend_name']) or (key if isinstance(key,str) else None)
        rows.append({'name':name,'qubit_num':field(['qubit_num','qubits','qubit_number']),
                     'status':field(['status','state']),'task_in_queue':field(['task_in_queue','queue','pending_tasks'])})
    return rows

def completed_result(res):
    status=getattr(res,'task_status',None)
    out={'task_id':getattr(res,'taskid',None),'task_status':status,
         'task_name':getattr(res,'taskname',None)}
    counts=getattr(res,'logicalq_res',None) or getattr(res,'counts',None) or {}
    out['counts']=counts
    if status=='Completed' and counts:
        s,hit,total=score_counts(counts,P['expected_parity'])
        out.update({'S_real_pilot':s,'hits':hit,'shots_returned':total,'shots_preregistered':R['shots'],
                    'scope':'single RAC cell only; not eight-cell S_real'})
        receipt['S_real_pilot']=s
    return out

try:
    if MODE not in ['SIM','FIRE','RETRIEVE']: raise ValueError('invalid MODE')
    if not KEY: raise RuntimeError('QUAFU_KEY missing')
    user=User(KEY)
    if MODE=='RETRIEVE':
        tid=os.environ.get('TASK_ID','').strip()
        if not tid: raise ValueError('TASK_ID required')
        from quafu import Task
        task=Task(user)
        res=task.retrieve(int(tid) if tid.isdigit() else tid)
        receipt['retrieval']=completed_result(res); receipt['task_id']=receipt['retrieval']['task_id']
        receipt['new_quantum_jobs_confirmed']=0
        receipt['ok']=receipt['retrieval']['task_status'] not in ['Failed','Canceled']
    else:
        receipt['local_simulation_gate']=local_gate()
        rows=backend_snapshot(user); receipt['backend_snapshot']=rows
        selected=next((x for x in rows if x['name']==PREREG['backend_policy']['selected']),None)
        backend_pass=bool(selected and str(selected['status']).lower()=='online' and int(selected['qubit_num'])>=PREREG['backend_policy']['min_qubits'])
        receipt['selected_backend']=selected; receipt['backend_gate_pass']=backend_pass
        eligible=bool(receipt['local_simulation_gate']['pass'] and backend_pass)
        receipt['fire_eligible_on_snapshot']=eligible
        if MODE=='FIRE':
            if os.environ.get('CONFIRMATION','')!=R['confirmation']: raise RuntimeError('FIRE confirmation mismatch')
            if not eligible: raise RuntimeError('simulation or backend gate failed; send forbidden')
            pilot=fresh_rac(P['x1'],P['x2'],P['basis']); pilot.to_openqasm()
            receipt['pilot']={'x1':P['x1'],'x2':P['x2'],'basis':P['basis'],'expected_parity':P['expected_parity'],
                              'openqasm':pilot.openqasm,'qasm_sha256':hashlib.sha256(pilot.openqasm.encode()).hexdigest()}
            from quafu import Task
            task=Task(user); task.config(backend=PREREG['backend_policy']['selected'],shots=R['shots'],compile=R['compile'],priority=R['priority'])
            receipt['send_attempts']=1
            res=task.send(pilot,name=R['task_name'],group=R['group'],wait=False)  # exactly once; no retry
            receipt['new_quantum_jobs_confirmed']=1
            receipt['submission']=completed_result(res); receipt['task_id']=receipt['submission']['task_id']
            receipt['ok']=receipt['task_id'] is not None
        else:
            receipt['fire_executed']=False; receipt['ok']=eligible
except Exception as exc:
    receipt['error']=clean_error(exc)
    if MODE=='FIRE' and receipt['send_attempts']==1 and receipt['new_quantum_jobs_confirmed']==0:
        receipt['new_quantum_jobs_uncertain']=True; receipt['submission_outcome']='UNCERTAIN_NO_RETRY'
    receipt['ok']=False
    save(); print(json.dumps({'ok':False,'mode':MODE,'error_type':type(exc).__name__,'send_attempts':receipt['send_attempts']},ensure_ascii=False))
    sys.exit(1)
receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
save()
print(json.dumps({'ok':receipt['ok'],'mode':MODE,'new_quantum_jobs_confirmed':receipt['new_quantum_jobs_confirmed'],
                  'send_attempts':receipt['send_attempts'],'task_id':receipt['task_id'],'S_real_pilot':receipt['S_real_pilot']},ensure_ascii=False))
