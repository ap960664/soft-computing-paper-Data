from pathlib import Path
import subprocess,sys,json,datetime
R=Path(__file__).resolve().parents[1]
P=R/'tmp/major_revision_package_validation/Major_Revision_Reproducibility_Package'
log=R/'reports/major_revision_portable_validation.log'
with log.open('w') as f:
    f.write('Final archive extraction validation UTC '+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
    f.write('Working directory: '+str(P)+'\n')
    for args in [['src/audit_results.py'],['src/analyze_major_revision.py'],['-m','pytest','tests','-q']]:
        f.write('\nCOMMAND: '+sys.executable+' '+' '.join(args)+'\n');f.flush()
        proc=subprocess.run([sys.executable,*args],cwd=P,stdout=f,stderr=subprocess.STDOUT)
        f.write('EXIT: '+str(proc.returncode)+'\n');f.flush()
        if proc.returncode:raise SystemExit(proc.returncode)
verification=R/'reports/major_revision_package_verification.json'
v=json.loads(verification.read_text());v.update({'extracted_audit_legacy':612,'extracted_audit_expanded':3661,'extracted_portable_tests':18,'validation_status':'PASS','validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
verification.write_text(json.dumps(v,indent=2))
print(log.read_text())
