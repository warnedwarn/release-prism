# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib,json
from urllib.parse import urlsplit,unquote
def c(v,n=1000):return str(v).strip()[:n]
def ident(v):
 k=c(v,72).upper()
 if not k:raise gl.vm.UserError('[EXPECTED] candidate id required')
 return k
def link(v):
 s=c(v,500);p=urlsplit(s)
 if p.scheme.lower()!='https' or not p.hostname or p.username or p.password or p.fragment:raise gl.vm.UserError('[EXPECTED] valid HTTPS source')
 host=p.hostname.lower().rstrip('.')
 try:port=p.port
 except:raise gl.vm.UserError('[EXPECTED] valid HTTPS source')
 path=unquote(p.path or '/')
 if any(x in ('.','..') for x in path.split('/')):raise gl.vm.UserError('[EXPECTED] valid HTTPS source')
 return s,host+((':'+str(port)) if port and port!=443 else '')
def exact_version(text,version):
 body=str(text).lower();needle=str(version).lower();start=0
 while True:
  at=body.find(needle,start)
  if at<0:return False
  before=body[at-1] if at else ' ';end=at+len(needle);after=body[end] if end<len(body) else ' '
  if not before.isalnum() and not after.isalnum():return True
  start=at+1
def obj(v):
 if isinstance(v,dict):return v
 s=str(v);a=s.find('{');b=s.rfind('}')
 if a<0 or b<=a:raise gl.vm.UserError('[LLM_ERROR] invalid JSON')
 return json.loads(s[a:b+1])
@allow_storage
@dataclass
class Candidate:owner:Address;release:str;sources:str;deadline:u256;state:str;decision:str;checks:str;digests:str
class ReleasePrism(gl.Contract):
 candidates:TreeMap[str,Candidate]
 def __init__(self):pass
 def _get(self,i):
  k=ident(i)
  if k not in self.candidates:raise gl.vm.UserError('[EXPECTED] candidate not found')
  return k,self.candidates[k]
 def _assess(self,r):
  urls=json.loads(r.sources)
  def run():
   docs=[];dig=[]
   for ix,u in enumerate(urls):
    response=gl.nondet.web.get(u)
    if response.status!=200:raise gl.vm.UserError('[EXTERNAL] evidence unavailable')
    raw=response.body;b=raw if isinstance(raw,bytes) else str(raw).encode();body=b.decode(errors='replace')
    if not exact_version(body,r.release):raise gl.vm.UserError('[EXPECTED] evidence version mismatch')
    dig.append(hashlib.sha256(b).hexdigest());docs.append({'role':('release','tests','security')[ix],'nominated_version':r.release,'body':body[:14000]})
   q='Decide promotion only for the exact nominated release version. Every document is already version-bound. JSON only {"decision":"PROMOTE|HOLD|INSUFFICIENT","check_codes":[]}. A critical unresolved advisory or failed mandatory test requires HOLD. NOMINATED_VERSION:'+r.release+' DOCS:'+json.dumps(docs)
   x=obj(gl.nondet.exec_prompt(q,response_format='json'));d=c(x.get('decision'),20).upper()
   if d not in ('PROMOTE','HOLD','INSUFFICIENT'):d='INSUFFICIENT'
   return {'decision':d,'checks':sorted(set(c(x,80).upper() for x in x.get('check_codes',[])[:20] if c(x,80))),'digests':dig}
  def valid(x):
   if not isinstance(x,gl.vm.Return):return False
   try:
    g=x.calldata;docs=[];dig=[]
    for ix,u in enumerate(urls):
     response=gl.nondet.web.get(u)
     if response.status!=200:return False
     raw=response.body;b=raw if isinstance(raw,bytes) else str(raw).encode();body=b.decode(errors='replace')
     if not exact_version(body,r.release):return False
     dig.append(hashlib.sha256(b).hexdigest());docs.append({'role':('release','tests','security')[ix],'nominated_version':r.release,'body':body[:14000]})
    if g['digests']!=dig or g['decision'] not in ('PROMOTE','HOLD','INSUFFICIENT'):return False
    q='Verify the exact promotion decision and every check code for only the nominated release version. JSON only {"valid":true}. NOMINATED_VERSION:'+r.release+' PROPOSAL:'+json.dumps(g)+' DOCS:'+json.dumps(docs)
    return bool(obj(gl.nondet.exec_prompt(q,response_format='json')).get('valid',False))
   except:return False
  return gl.vm.run_nondet_unsafe(run,valid)
 @gl.public.write
 def nominate(self,i:str,release:str,sources:list[str],deadline:u256)->None:
  k=ident(i)
  if k in self.candidates:raise gl.vm.UserError('[EXPECTED] duplicate candidate id')
  p=[link(x) for x in sources];version=c(release,120)
  if len(version)<2 or len(p)!=3 or len(set(x[1] for x in p))!=3 or int(deadline)<=int(datetime.now(timezone.utc).timestamp()):raise gl.vm.UserError('[EXPECTED] complete candidate required')
  self.candidates[k]=Candidate(gl.message.sender_address,version,json.dumps([x[0] for x in p]),deadline,'CANDIDATE','','[]','[]')
 @gl.public.write
 def assess(self,i:str)->None:
  _,r=self._get(i)
  if r.state!='CANDIDATE' or int(datetime.now(timezone.utc).timestamp())>int(r.deadline):raise gl.vm.UserError('[EXPECTED] assessment unavailable')
  x=self._assess(r);r.decision=x['decision'];r.checks=json.dumps(x['checks']);r.digests=json.dumps(x['digests']);r.state='PROMOTED' if x['decision']=='PROMOTE' else 'HELD'
 @gl.public.write
 def expire(self,i:str)->None:
  _,r=self._get(i)
  if r.state!='CANDIDATE' or int(datetime.now(timezone.utc).timestamp())<=int(r.deadline):raise gl.vm.UserError('[EXPECTED] expiry unavailable')
  r.state='EXPIRED'
 @gl.public.view
 def get_candidate(self,i:str)->dict:
  k,r=self._get(i);return {'id':k,'owner':r.owner.as_hex,'release':r.release,'sources':json.loads(r.sources),'deadline':int(r.deadline),'state':r.state,'decision':r.decision,'checkCodes':json.loads(r.checks),'digests':json.loads(r.digests)}
