#!/usr/bin/env python3
# CLASSIFY: L1
"""V-151U hardening: one-send RAC pilot, strict result contracts and atomic immutable evidence."""
import os, sys, json, hashlib, datetime, re
from pathlib import Path
from scipy.stats import chisquare
from quafu import QuantumCircuit, simulate, User

MODE=os.environ.get('MODE','SIM').upper()
ROOT=Path.cwd()
sys.path.insert(0,str(ROOT))
from ci.quafu_rac_io import load_json, write_json_atomic
from ci.quafu_rac_analysis import analyze_pilot_counts
from ci.quafu_rac_immutable import make_snapshot, append_snapshot
PREREG=load_json(ROOT/'ci/QUAFU-RAC-PREFLIGHT-LGT-01.json')
RECEIPT=Path(os.environ.get('RECEIPT_PATH','receipts/quafu-rac-receipt.json'))
SPENT_PATH=ROOT/'ci/QUAFU-RAC-FIRE-SPENT-LGT-01.json'
HISTORY_PATH=ROOT/'ci/QUAFU-RAC-RETRIEVAL-HISTORY-LGT-01.json'
NOW=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
KEY=os.environ.get('QUAFU_KEY','')
R=PREREG['real_submission']; P=PREREG['pilot']; G=PREREG['local_simulation_gate']
receipt={'schema':'lgt.quafu.rac.receipt.v1','experiment_id':PREREG['experiment_id'],'mode':MODE,
         'started_utc':NOW,'sdk':PREREG['sdk'],'prereg_sha256':hashlib.sha256(json.dumps(PREREG,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
         'new_quantum_jobs_confirmed':0,'send_attempts':0,'new_quantum_jobs_uncertain':False,
         'S_real_pilot':None,'task_id':None,'ok':False}

def save():
    write_json_atomic(RECEIPT,receipt)

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
    for v in counts.values():
        if type(v) is not int or v<0: raise ValueError('counts must be nonnegative integer JSON numbers')
    total=sum(counts.values())
    if total<=0: return None,0,0
    hit=0
    for k,v in counts.items():
        q0,q1=bits2(k)
        if (q0^q1)==want: hit+=v
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

KNOWN_STATUSES={'In Queue','Running','Pending','Completed','Failed','Canceled'}
NEGATIVE_TERMINAL={'Failed','Canceled'}
MISSING=object()

def completed_result(res):
    status=getattr(res,'task_status',None)
    logical=getattr(res,'logicalq_res',MISSING)
    raw=getattr(res,'counts',MISSING)
    measures=getattr(res,'measures',MISSING)
    if logical is not MISSING and logical is not None:
        selected=logical; source='logicalq_res'
    elif raw is not MISSING and raw is not None:
        selected=raw; source='counts_fallback'
    else:
        selected={}; source='empty_default'
    out={'task_id':getattr(res,'taskid',None),'task_status':status,
         'task_name':getattr(res,'taskname',None),'status_known':status in KNOWN_STATUSES,
         'counts':selected,'counts_source':source,
         'logicalq_counts':None if logical is MISSING else logical,
         'raw_counts':None if raw is MISSING else raw,
         'measures':None if measures is MISSING else measures,
         'counts_contract':{'logicalq_res_present':logical is not MISSING,
                            'counts_present':raw is not MISSING,
                            'selection':'never use truthiness to discard a present empty logical projection'}}
    return out

def validate_result_contract(out):
    sources={k:out.get(k) for k in ['logicalq_counts','raw_counts']}
    for name,counts in sources.items():
        if counts is None: continue
        if not isinstance(counts,dict): raise ValueError(f'{name} must be a mapping')
        for value in counts.values():
            if type(value) is not int or value<0:
                raise ValueError(f'{name} values must be nonnegative integer JSON numbers')
    logical=sources['logicalq_counts']; raw=sources['raw_counts']
    if logical is not None and raw is not None:
        if sum(logical.values())!=sum(raw.values()):
            raise RuntimeError('raw/logical counts total mismatch; evidence preserved and scoring forbidden')
        measures=out.get('measures')
        if measures is not None:
            if not isinstance(measures,dict): raise ValueError('measures must be a mapping')
            cbits=list(measures.values())
            indexed={bit:i for i,bit in enumerate(sorted(cbits))}
            squeezed=[indexed[bit] for bit in cbits]
            projected={}
            for key,value in raw.items():
                if not isinstance(key,str): raise ValueError('raw counts keys must be strings')
                try: newkey=''.join(key[i] for i in squeezed)
                except IndexError as exc: raise ValueError('raw counts key shorter than measure map') from exc
                if newkey in projected:
                    raise RuntimeError('logical projection collision; refusing lossy counts selection')
                projected[newkey]=value
            if projected!=logical:
                raise RuntimeError('raw/logical counts projection mismatch; evidence preserved and scoring forbidden')
    return out

def score_completed_result(out):
    if not out.get('status_known'):
        raise RuntimeError('unknown task status; evidence preserved and scoring forbidden')
    validate_result_contract(out)
    if out.get('task_status') in NEGATIVE_TERMINAL:
        raise RuntimeError('negative terminal task status; evidence preserved and workflow success forbidden')
    if out.get('task_status')=='Completed':
        counts=out['counts']
        if not counts:
            raise RuntimeError('Completed returned empty counts; evidence preserved and success forbidden')
        s,hit,total=score_counts(counts,P['expected_parity'])
        if s is None or total<=0:
            raise RuntimeError('Completed returned zero shots; evidence preserved and success forbidden')
        analysis=analyze_pilot_counts(counts)
        if analysis.get('status')!='OK' or analysis.get('shots_returned',0)<=0:
            raise RuntimeError('Completed analysis is not OK; evidence preserved and success forbidden')
        out.update({'S_real_pilot':s,'hits':hit,'shots_returned':total,'shots_preregistered':R['shots'],
                    'scope':'single RAC cell only; not eight-cell S_real'})
        assert abs(s-analysis['S_real_pilot'])<1e-15
        out['analysis']=analysis
        receipt['S_real_pilot']=s
    return out

def record_retrieval(out):
    validate_result_contract(out)
    history=load_json(HISTORY_PATH)
    run_id=os.environ.get('GITHUB_RUN_ID','')
    run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT','1')
    if not run_id.isdigit() or not run_attempt.isdigit() or int(run_attempt)<=0:
        raise RuntimeError('numeric GITHUB_RUN_ID and positive GITHUB_RUN_ATTEMPT required for immutable history')
    snap=make_snapshot(run_id,out['task_id'],out['task_status'],out['counts'],str(RECEIPT),
                       'UNSEALED_CURRENT_RECEIPT',
                       datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),run_attempt)
    history=append_snapshot(history,snap)
    write_json_atomic(HISTORY_PATH,history)
    out['counts_sha256']=snap['counts_sha256']
    out['immutable_audit']=history['audit']
    receipt['immutable_audit']=history['audit']
    if history['audit']['immutable_violation']:
        raise RuntimeError('immutable counts violation; scoring forbidden and conflicting evidence preserved')
    return out

try:
    if MODE not in ['SIM','FIRE','RETRIEVE']: raise ValueError('invalid MODE')
    if MODE=='FIRE' and SPENT_PATH.exists(): raise RuntimeError('FIRE spend marker exists; second send forbidden before authentication')
    if MODE=='RETRIEVE':
        tid=os.environ.get('TASK_ID','').strip()
        if not tid: raise ValueError('TASK_ID required')
        receipt['task_id']=tid
        receipt['task_id_role']='requested_existing_task'
        receipt['retrieval_request']={'task_id':tid,'method':'Task.retrieve','new_quantum_jobs':0}
    if not KEY: raise RuntimeError('QUAFU_KEY missing')
    user=User(KEY)
    if MODE=='RETRIEVE':
        from quafu import Task
        task=Task(user)
        try:
            res=task.retrieve(int(tid) if tid.isdigit() else tid)
        except Exception as exc:
            receipt['retrieval_boundary']={'task_id':tid,'stage':'Task.retrieve/ExecResult',
                'raw_counts_available':False,'snapshot_created':False,'error':clean_error(exc)}
            raise
        receipt['retrieval']=completed_result(res); receipt['task_id']=receipt['retrieval']['task_id']
        record_retrieval(receipt['retrieval'])
        score_completed_result(receipt['retrieval'])
        receipt['new_quantum_jobs_confirmed']=0
        receipt['ok']=True
        receipt['ok_semantics']='retrieval operation succeeded; task completion is represented only by retrieval.task_status'
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
            receipt['submission']=completed_result(res)
            receipt['task_id']=receipt['submission']['task_id']
            score_completed_result(receipt['submission'])
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
