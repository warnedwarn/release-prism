from conftest import CONTRACT
URLS=['https://notes.example/r7','https://tests.example/r7','https://security.example/r7']
def mocks(v):
 v.strict_mocks=True;v.check_pickling=True;v.mock_web(r'notes\.example',{'status':200,'body':'Release r7, documented migration.'});v.mock_web(r'tests\.example',{'status':200,'body':'Signed mandatory suite: PASS.'});v.mock_web(r'security\.example',{'status':200,'body':'No critical unresolved advisory.'});v.mock_llm(r'.*Decide release promotion.*','{"decision":"PROMOTE","check_codes":["TESTS_PASS","NO_CRITICAL"]}');v.mock_llm(r'.*Verify exact promotion.*','{"valid":true}')
def test_promote(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);mocks(direct_vm);c.nominate('R7','release-7',URLS,1893463200);c.assess('R7');s=c.get_candidate('R7');assert s['state']=='PROMOTED' and len(s['digests'])==3
def test_expiry_and_duplicate_sources(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);c.nominate('A','r',URLS,1893456060)
 with direct_vm.expect_revert('duplicate candidate'):c.nominate(' a ','r',URLS,1893456060)
 with direct_vm.expect_revert('complete candidate'):c.nominate('B','r',[URLS[0],URLS[0],URLS[2]],1893456060)
 direct_vm.warp('2030-01-01T00:02:00+00:00');c.expire('A');assert c.get_candidate('A')['state']=='EXPIRED'
def test_forged_checks_rejected(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);mocks(direct_vm);c.nominate('X','r',URLS,1893463200);x=c._assess(c.candidates['X']);assert direct_vm.run_validator(leader_result=x);x=dict(x);x['digests']=list(reversed(x['digests']));assert not direct_vm.run_validator(leader_result=x)
