from pathlib import Path
import csv,json,re
R=Path(__file__).resolve().parents[1]
def csvrows(p):return list(csv.DictReader((R/p).open()))
registry={r['paper_id']:r for r in csvrows('logs/article_registry.csv')};primary={r['Study_ID']:r for r in csvrows('evidence/primary_studies.csv')};refs={r['number']:r['key'] for r in json.loads((R/'references/numbered_references.json').read_text())};tabs={}
tabs['Manual_Source_Checks']=[['Check_ID','Priority','Evidence ID / citation','Exact claim to verify','Source page / table / section','Required author action','Author decision','Date / clarification']]
for row in json.loads((R/'evidence/manual_source_checks.json').read_text()):
    # Add the verified DOI and exact local source path without requiring new access.
    ids=re.findall(r'\b[PS]\d{2,3}\b',row[2]);sources=[]
    for sid in ids:
        if sid in registry:sources.append(sid+': '+registry[sid]['doi_url'])
    tabs['Manual_Source_Checks'].append(row[:4]+[row[4]+'\n'+'\n'.join(sources),row[5],'PENDING',''])
tabs['Author_Details']=[['Field','Value','Status','Evidence / required action'],['Name','Ashish Pathak','USER CONFIRMED','User reply9 October2026;authors must approve final manuscript separately'],['Affiliation','School of Computer Science and Engineering, Lovely Professional University','USER CONFIRMED','User reply9 October2026'],['Location','Jalandhar, Punjab, India','USER CONFIRMED','User reply9 October2026'],['Email','ap960664@gmail.com','USER CONFIRMED','User reply9 October2026'],['Coauthors','None','USER CONFIRMED','User reply9 October2026'],['Manuscript authorship','All current prose AI-generated','HUMAN AUTHORSHIP REQUIRED','Independently author compliant prose;verify claims;approve final version']]
tabs['Manuscript_Claims']=[['Claim_ID','Section / paragraph','Exact current passage','Evidence IDs','Exact source / locator','Tool verification status','Required author action','Author decision / date']];section='';i=0
for line in (R/'drafts/review_draft.md').read_text().splitlines():
 if line.startswith('## '):section=line[3:]
 if not line or line.startswith(('#','[[','![')) or section=='References':continue
 ids=list(dict.fromkeys(refs.get(int(n),'NOT VERIFIED') for n in re.findall(r'\[(\d+)\]',line)))
 loc=[]
 for sid in ids:
  if sid in primary:loc.append(sid+': '+primary[sid]['Evidence_Page_Table_Figure'])
  elif sid in registry:loc.append(sid+': notes/03_survey_overlap_audit.md;originalPDF '+registry[sid]['pdf_path'])
  else:loc.append(sid+': results/experiment_manifest.json;dataset_description.txt;UCI/sklearn docs')
 if section.startswith('VI') or 'demonstration' in line.lower():loc.append('results/raw_metrics.csv/summary_metrics.csv/test_predictions.csv;reports/recomputed_prediction_metrics.csv')
 i+=1;tabs['Manuscript_Claims'].append([f'C{i:03}',section,line,'; '.join(ids) or 'Synthesis / syllabus / local result','; '.join(loc) or 'notes/01_input_and_syllabus_audit.md;methods/code;verify foundational claim scope','SOURCE AUDITED; HUMAN REVIEW PENDING','Read named sources and challenge interpretations;independently author prose;do not infer final typeset equality','PENDING'])
tabs['Numerical_Evidence']=[['Study_ID','Dataset','Metric / claim','Value','Units','SD','Comparator','Exact source / locator','Tool status','Required author action','Author decision / date']]
for r in csvrows('evidence/reported_results.csv'):tabs['Numerical_Evidence'].append([r['Study_ID'],r['Dataset'],r['Metric'],r['Value'],r['Units'],r['SD'],r['Baseline'],r['Evidence_Page_Table'],'EXTRACTED FROM STATED SOURCE VERSION','Check table alignment,denominator,metric meaning and protocol;accepted manuscript/XML version limits retained','PENDING'])
tabs['Method_Evidence']=[['Study_ID','Source title / DOI','Field','Extracted description','Exact locator','Tool status','Required author action','Author decision / date']]
for sid,r in primary.items():
 if r['Included (Y/N)']!='Y':continue
 for k in ['Datasets_and_Sources','Sample_Sizes','Original_Feature_Counts','Preprocessing','GA_Variant_or_Hybrid','Chromosome_Encoding','GA_Selection','GA_Crossover','GA_Mutation','Fitness_Objectives','Classifier_and_Baselines','Validation_Protocol','Computational_Cost_or_Runtime','Repeated_Runs_and_Statistical_Tests','Code_and_Data_Availability','Critical_Appraisal']:
  tabs['Method_Evidence'].append([sid,r['Exact_Title']+';DOI:'+r['DOI'],k,r[k],r['Evidence_Page_Table_Figure'],'FULL-TEXT EXTRACTION; ambiguity retained','Verify specific field in original version;distinguish report from reviewer inference','PENDING'])
tabs['Experiment_Summaries']=[['Method','Metric','Recomputed mean','Sample SD','N','Units','Source','Tool status','Required author action','Author decision / date']]
for r in csvrows('results/summary_metrics.csv'):tabs['Experiment_Summaries'].append([r['method'],r['metric'],float(r['mean']),float(r['sd']),int(r['n']),r['units'],'results/raw_metrics.csv;reports/result_audit_checks.csv','RECOMPUTED; AUTHOR REPORTS SEPARATE RERUN','Review interpretation and timing boundaries. No repeat calculation required without a new discrepancy.','Recalculation reported by author,9 October2026;interpretation review pending'])
tabs['Expanded_Results']=[['Dataset','Method','Metric','Mean','Sample SD','N','Source','Required author action']]
for r in csvrows('Results_and_Graphs/major_revision/summary_tidy.csv'):tabs['Expanded_Results'].append([r['dataset'],r['method'],r['metric'],float(r['mean']),float(r['sd']),int(r['n']),'major_revision/raw_metrics.csv;audit.json','Verifyadaptation/costboundary anddescriptiveuncertainty;keepseparatefromlegacyresults'])
tabs['Expanded_Stability']=[['Dataset','Method','Mean Jaccard','SD','Pairs','Interpretation']]
for r in csvrows('Results_and_Graphs/major_revision/stability.csv'):tabs['Expanded_Stability'].append([r['dataset'],r['method'],float(r['pairwise_jaccard_mean']),float(r['sd']),int(r['pairs']),r['note']])
tabs['Audit_Checks']=[['Check','Status','Evidence detail']]+[[r['check'],r['status'],r['detail']] for r in csvrows('reports/result_audit_checks.csv')]
tabs['Pending_Sources']=[['ID','Title','DOI','Access','Status','Required action']]+[[r['Study_ID'],r['Exact_Title'],r['DOI'],r['Evidence_Level'],r['Verification_Status'],'No purchase requested;retain unverified details;use legitimate source only if obtained'] for r in primary.values() if r['Included (Y/N)']=='N' and r['Verification_Status']!='EXCLUDED']
(R/'tmp/author_worksheet_data.json').write_text(json.dumps(tabs,indent=2));print({k:len(v)-1 for k,v in tabs.items()})
