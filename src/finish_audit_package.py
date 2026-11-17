from pathlib import Path
import json,hashlib,shutil,zipfile,datetime
R=Path(__file__).resolve().parents[1];S=R/'tmp/repro_package'
for f in ['Final_Research_Paper.docx','Complete_Literature_Matrix.xlsx','Author_Verification_Worksheet.xlsx','Research_Paper_References.bib','Research_Methodology_and_Search_Log.md','Final_Quality_and_Submission_Checklist.md','AI_Assistance_Record.md','Source_and_Result_Audit_Report.md','Remaining_Issues_and_Resolution_Plan.md','Reproducibility_and_Test_Report.md','Source_Verification_Report.md']:
 (S/'research_artifacts').mkdir(exist_ok=True);shutil.copy2(R/f,S/'research_artifacts'/f)
for f in ['tests_final.log','tests_package.log','tests_audit.log','selected_masks.json','audit_from_zip.log','tests_extracted_zip.log']:shutil.copy2(R/'results'/f,S/'results'/f)
for p in (R/'reports').glob('*.json'):shutil.copy2(p,S/'reports'/p.name)
for p in (R/'reports').glob('*.csv'):shutil.copy2(p,S/'reports'/p.name)
# Source collection manifests containpaths/hashes only;not publisher fulltexts.
manifest={str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.name!='PACKAGE_SHA256.json'}
(S/'PACKAGE_SHA256.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(R/'Complete_Reproducibility_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in [*manifest,'PACKAGE_SHA256.json']:z.write(S/name,'Complete_Reproducibility_Package/'+name)
with zipfile.ZipFile(R/'Complete_Reproducibility_Package.zip') as z:
 assert z.testzip() is None
 for name,h in manifest.items():assert hashlib.sha256(z.read('Complete_Reproducibility_Package/'+name)).hexdigest()==h
print('ZIP CRC and',len(manifest),'SHA256 entries verified;', (R/'Complete_Reproducibility_Package.zip').stat().st_size,'bytes')
