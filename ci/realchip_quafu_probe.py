#!/usr/bin/env python3
# QUAFU-PROBE-02 · 源码对齐 Backend.name/qubit_num/status/task_in_queue；零量子 job。
import os,json,sys,subprocess,datetime,inspect,urllib.parse
TS=datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
out={'v':'QUAFU-PROBE-02','ts':TS,'job_submitted':False,'probe':{}}
key=os.environ.get('QUAFU_API_KEY','').strip()
out['probe']['secret_present']=bool(key)
def clean(x):
 s=str(x)
 if key:
  s=s.replace(key,'[REDACTED]').replace(urllib.parse.quote(key,safe=''),'[REDACTED]')
 return s[:240]
def primitive(x):
 return x if isinstance(x,(str,int,float,bool)) or x is None else None
subprocess.run([sys.executable,'-m','pip','install','-q','pyquafu'],check=False)
try:
 import quafu
 from importlib.metadata import version,PackageNotFoundError
 try: out['probe']['sdk_version']=version('pyquafu')
 except PackageNotFoundError: out['probe']['sdk_version']='unknown'
 out['probe']['User_signature']=str(inspect.signature(quafu.User.__init__))
 if not key:
  out['probe']['auth']={'ok':False,'error':'MISSING_SECRET'}
 else:
  user=quafu.User(key)  # 官方构造路径；不 save_apitoken，不落凭证文件。
  out['probe']['auth']={'ok':True,'constructor':'User(api_token)'}
  try:
   backs=user.get_available_backends()
   rows=[]
   if isinstance(backs,dict): iterable=list(backs.items())
   elif isinstance(backs,(list,tuple)): iterable=[(None,b) for b in backs]
   else: iterable=[(None,backs)]
   for label,b in iterable:
    info=b if isinstance(b,dict) else {}
    def field(names,stringify=False):
     for n in names:
      v=info.get(n) if isinstance(info,dict) else getattr(b,n,None)
      p=primitive(v)
      if p is not None: return p
      if stringify and v is not None: return clean(v)
     return None
    rows.append({'name':field(['system_name','name','backend_name']) or (label if isinstance(label,str) else None),
                 'qubits':field(['qubits','qubit_num','num_qubits','n_qubits']),
                 'status':field(['status','state'],stringify=True),
                 'queue':field(['task_in_queue','queued_len'])})
   out['probe']['backends']={'count':len(rows),'items':rows}
  except Exception as e:
   out['probe']['backends']={'ok':False,'error':type(e).__name__+':'+clean(e)}
except Exception as e:
 out['probe']['auth']={'ok':False,'error':type(e).__name__+':'+clean(e)}
finally:
 key=''
os.makedirs('receipts',exist_ok=True)
path=f'receipts/quafu-probe-{TS}.json'
with open(path,'w') as f: json.dump(out,f,ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False)[:1200])
