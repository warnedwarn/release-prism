from conftest import CONTRACT
URLS=['https://notes.example/r7','https://tests.example/r7','https://security.example/r7']
def mocks(v):
 v.strict_mocks=True;v.check_pickling=True;v.mock_web(r'notes\.example',{'status':200,'body':'Release release-7, documented migration.'});v.mock_web(r'tests\.example',{'status':200,'body':'Signed mandatory suite for release-7: PASS.'});v.mock_web(r'security\.example',{'status':200,'body':'Release-7 has no critical unresolved advisory.'});v.mock_llm(r'.*Decide promotion only.*','{"decision":"PROMOTE","check_codes":["TESTS_PASS","NO_CRITICAL"]}');v.mock_llm(r'.*Verify the exact promotion.*','{"valid":true}')
def test_promote(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);mocks(direct_vm);c.nominate('R7','release-7',URLS,1893463200);c.assess('R7');s=c.get_candidate('R7');assert s['state']=='PROMOTED' and len(s['digests'])==3
def test_expiry_and_duplicate_sources(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);c.nominate('A','release-7',URLS,1893456060)
 with direct_vm.expect_revert('duplicate candidate'):c.nominate(' a ','release-7',URLS,1893456060)
 with direct_vm.expect_revert('complete candidate'):c.nominate('B','release-7',[URLS[0],URLS[0],URLS[2]],1893456060)
 direct_vm.warp('2030-01-01T00:02:00+00:00');c.expire('A');assert c.get_candidate('A')['state']=='EXPIRED'
def test_forged_checks_rejected(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);mocks(direct_vm);c.nominate('X','release-7',URLS,1893463200);x=c._assess(c.candidates['X']);assert direct_vm.run_validator(leader_result=x);x=dict(x);x['digests']=list(reversed(x['digests']));assert not direct_vm.run_validator(leader_result=x)
def test_mismatched_release_evidence_cannot_promote(direct_vm,direct_deploy):
 direct_vm.warp('2030-01-01T00:00:00+00:00');c=direct_deploy(CONTRACT);direct_vm.strict_mocks=True;direct_vm.mock_web(r'notes\.example',{'status':200,'body':'Release release-7 notes.'});direct_vm.mock_web(r'tests\.example',{'status':200,'body':'Mandatory tests PASS for release-8.'});direct_vm.mock_web(r'security\.example',{'status':200,'body':'Release release-7 security clear.'});c.nominate('MISMATCH','release-7',URLS,1893463200)
 with direct_vm.expect_revert('evidence version mismatch'):c.assess('MISMATCH')
 assert c.get_candidate('MISMATCH')['state']=='CANDIDATE'
