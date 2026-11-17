from pathlib import Path
import csv,json,html,requests
ROOT=Path(__file__).resolve().parents[1]
def writecsv(name,rows,headers=None):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=headers or list(rows[0]));w.writeheader();w.writerows(rows)

registry=[r for r in csv.DictReader((ROOT/'logs/article_registry.csv').open()) if r['paper_id'] not in ['P010','P011'] and int(r['paper_id'][1:])<12]
doi='10.1186/s40537-020-00398-3';r=requests.get('https://api.crossref.org/works/'+doi,timeout=40);r.raise_for_status();m=r.json()['message'];(ROOT/'logs/metadata/P010.json').write_text(r.text)
registry.append(dict(registry[0],paper_id='P010',kind='primary_candidate',title=m['title'][0],authors='; '.join(a.get('given','')+' '+a.get('family','') for a in m['author']),year=m['published']['date-parts'][0][0],journal_or_conference=m['container-title'][0],volume=m.get('volume',''),issue=m.get('issue','N/A'),pages_or_article_no=m.get('article-number','2'),publisher=m['publisher'],DOI=doi,doi_url='https://doi.org/'+doi,landing_url='https://link.springer.com/article/'+doi))
m=json.loads((ROOT/'logs/metadata/GeFeS.json').read_text())['message'];doi=m['DOI']
registry.append(dict(registry[0],paper_id='P011',kind='primary_candidate',title=m['title'][0],authors='; '.join(a.get('given','')+' '+a.get('family','') for a in m['author']),year=m['published']['date-parts'][0][0],journal_or_conference=m['container-title'][0],volume=m.get('volume',''),issue=m.get('issue','N/A'),pages_or_article_no=m.get('page',m.get('article-number','103974')),publisher=m['publisher'],DOI=doi,doi_url='https://doi.org/'+doi,landing_url=m['resource']['primary']['URL'],pdf_path='',access_level='METADATA_ONLY',fulltext_verified='N'))
registry += json.loads((ROOT/'logs/expanded_candidates.json').read_text())
local={'S01':next(ROOT.glob('Recent*.pdf')),'S02':next(ROOT.glob('Evolutionary*.pdf')),'S03':next(ROOT.glob('A tutorial*.pdf')),'P004':ROOT/'literature/verified/P004_MMFS_GA.pdf','P006':ROOT/'literature/verified/P006_AGAwER.pdf','P010':ROOT/'literature/verified/P010_CDGAFS.pdf','P021':ROOT/'literature/verified/P021.pdf','P022':ROOT/'literature/verified/P022.pdf'}
for prefix,sid in [('A correlation','P002'),('Enhancing','P003'),('Feature selection using','P005')]:
    local[sid]=next((ROOT/'literature/incoming').glob(prefix+'*.pdf'))
for sid,path in json.loads((ROOT/'logs/incoming_batch2.json').read_text()).items():local[sid]=ROOT/path
requested=['P001','P008','P011']
reasons=['Adaptive crossover and Pareto quality, repeat design, compute budget','Three objectives, final Pareto selection, validation separation and budget','Nested cross-validation boundaries, operator details, parallel timing and full baseline comparison; author-hosted PDF now404 and methods retrieval times out']
requested += ['P012','P013','P014','P015','P016','P017']
reasons += ['Filter/filter TAGA representation,validation,classifier transfer,runtime','MOEA-ISa initialization/crossover,large-scale validation,Pareto/resource budget','ReliefF placement,threshold operators,classification/size/runtime tables','Distinguish starting/classification time from search time;validation and objective model','ICS split/class imbalance,operators,SVM/classifier baselines and time boundary','Dominance initialization,duplicate handling,Pareto metrics and overhead']
needed=[(sid,reason) for sid,reason in zip(requested,reasons) if sid not in local]
requested=[x[0] for x in needed];reasons=[x[1] for x in needed]
for row in registry:
    for k,v in row.items():row[k]=html.unescape(str(v))
    row['landing_url']=row['landing_url'].replace('https://linkinghub.elsevier.com/retrieve/pii/','https://www.sciencedirect.com/science/article/pii/')
    row['metadata_verified']='Y: Crossref; publisher PDF/record title and DOI cross-check' if row['paper_id'] in local or row['paper_id'] in requested else 'Crossref only'
    if row['paper_id'] in local:
        row.update(pdf_path=str(local[row['paper_id']].relative_to(ROOT)),access_level='FULL_TEXT',fulltext_verified='Y',screening_status='BACKGROUND_REVIEW' if row['kind']=='review' else 'INCLUDED',kind='review' if row['kind']=='review' else 'primary')
        row['notes']='User-supplied PDF; title/DOI matched' if row['paper_id'].startswith('S') or local[row['paper_id']].parent.name=='incoming' else 'Legitimate open-access publisher/repository PDF; pages verified. P004 supplemental material still NOT VERIFIED.'
    elif row['paper_id'] in ['P009','P020','P024']:
        row.update(screening_status='EXCLUDED',relevance_rq='N/A',notes='Metadata correction: DOI supplied as an unchecked lead resolves to unrelated clustering. Excluded, never cited as GA feature selection.')
        if row['paper_id']=='P020':row.update(access_level='FULL_TEXT',fulltext_verified='Y',pdf_path='literature/verified/P020.pdf',notes='EXCLUDED: GA optimizes ELM input weights; sequential forward selection searches features (pp.1,8-10). Fails GA-central feature-subset-search criterion.')
        if row['paper_id']=='P024':row.update(access_level='FULL_TEXT',fulltext_verified='Y',pdf_path='literature/verified/P024.pdf',notes='EXCLUDED:regression-onlyGA/ElasticNetMaizeprediction;preprintpp5-7explicitlystatesregressionfocus.')
    else:row['screening_status']='PENDING_FULLTEXT'
    if row['paper_id']=='P012':row['notes']='Accepted author manuscript from Loughborough Figshare; version metadata links final DOI;41physicalpages. Final typeset equality not verified.'
    if row['paper_id']=='P018':row['notes']='Full journal XML from EuropePMC;title/authors/DOI verified;PDF unavailable;section/table locators used.'
    if row['paper_id']=='P015':row['access_level']='ABSTRACT_ONLY';row['notes']='User confirms purchase-only;no purchase or repeated download request. Publisher abstract supports objective scope only.'
writecsv('logs/article_registry.csv',registry)

queries=[('Q01','site.sciencedirect.com "genetic algorithm" "feature selection" classification','Broad publisher discovery'),('Q02','site.sciencedirect.com "Adaptive crossover operator based multi-objective binary genetic algorithm"','Exact publisher verification from survey citation'),('Q03','site.sciencedirect.com "Enhancing classification with hybrid feature selection"','Exact publisher verification'),('Q04','site.sciencedirect.com "Multi-objective genetic algorithm for multi-view feature selection"','Exact publisher verification'),('Q05','site.sciencedirect.com "Feature selection using guided population"','Exact publisher verification'),('Q06','"A correlation guided genetic algorithm" pdf','Legitimate open access lookup'),('Q07','"Feature selection using a classification error impurity" pdf','Open repository lookup'),('Q08','site.sciencedirect.com "genetic algorithm" "feature selection" runtime efficiency classification 2026','Focused cost/date discovery'),('Q09','site.sciencedirect.com "binary genetic algorithm" "feature selection" accuracy reproducibility','Focused evidence-quality discovery'),('Q10','"A problem-specific non-dominated sorting genetic algorithm for supervised feature selection" pdf','Open access lookup'),('Q11','site.journalofbigdata.springeropen.com "A novel community detection based genetic algorithm"','Supplemental primary search')]
queries += [('Q12','"GeFeS: A generalized wrapper feature selection" pdf','Additional validation counterevidence lead'),('Q13','"GeFeS" site:utupub.fi','Legitimate repository lookup'),('Q14','"GeFeS" site:diva-portal.org','Legitimate repository lookup')]
queries += [('Q15','site.sciencedirect.com "genetic algorithm" "feature selection" classification 2020 2021 2022 2023 2024 2025','User-requested expansion toward20 primary records'),('Q16','"A new and fast rival genetic algorithm for feature selection" DOI','Metadata verification'),('Q17','"Hybrid wrapper feature selection method based on genetic algorithm and extreme learning machine" DOI','Full-text screening lead,subsequently excluded'),('Q18','site.sciencedirect.com "TAGA: Tabu Asexual Genetic Algorithm"','Publisher verification'),('Q19','site.sciencedirect.com "A multi-objective evolutionary algorithm with interval based initialization"','Publisher verification'),('Q20','site.mdpi.com "Automated Network Incident Identification through Genetic Algorithm-Driven Feature Selection"','Replacement GA-central study')]
queries += [('Q21','Crossref query.title=genetic algorithm feature selection classification;from-pub-date2020-01-01;until-pub-date2026-10-09;typejournal-article;rows20','Major-revision broadmetadata discovery'),('Q22','Crossref query.title=genetic algorithm feature selection;prefix10.1016;from-pub-date2020-01-01;until-pub-date2026-10-09;typejournal-article;rows20','Publisher-prioritymajor-revision discovery;P023included/P024excluded')]
qrows=[dict(query_id=q,platform='web search (ScienceDirect-priority; not native Scopus)',search_date='2026-10-09',exact_query=t,filters='Domain restriction where literally present; no UI date filter',displayed_count='NOT DISPLAYED',url='https://www.sciencedirect.com/' if 'sciencedirect' in t else 'publisher/repository URLs in article_registry.csv',export_file='logs/search_queries.csv',method=why) for q,t,why in queries]
for q in qrows:
    if q['query_id'] in ['Q21','Q22']:
        filename='logs/major_revision_crossref_search.json' if q['query_id']=='Q21' else 'logs/major_revision_elsevier_search.json'
        saved=json.loads((ROOT/filename).read_text());q.update(platform='CrossrefAPI',url=saved['request_url'],export_file=filename,displayed_count=str(len(saved['response']['message']['items']))+'returnedrecords;notallsearchhits')
writecsv('logs/search_queries.csv',qrows)
screen=[]
for r in registry:
    sid=r['paper_id'];ex='SECONDARY_REVIEW' if sid.startswith('S') else 'WRONG_DOI_UNRELATED_CLUSTERING' if sid=='P009' else 'GA_WEIGHT_TUNING_ONLY' if sid=='P020' else 'REGRESSION_ONLY' if sid=='P024' else ''
    screen.append(dict(record_id=sid,database='local provided + publisher/Crossref' if sid.startswith('S') else 'publisher-priority web + Crossref + citation chasing',query_id='LOCAL' if sid.startswith('S') else 'Q22' if sid in ['P023','P024'] else 'Q01;citation_chasing',search_date='2026-10-09',raw_title=r['title'],normalized_title=r['title'].lower(),DOI=r['DOI'],year=r['year'],duplicate_group=r['DOI'].lower(),title_abstract_decision='BACKGROUND' if sid.startswith('S') else 'EXCLUDE' if ex else 'RETAIN',full_text_status=r['access_level'],full_text_decision=r['screening_status'],exclusion_reason=ex,reviewer_notes=r['notes'],PDF_path=r['pdf_path'],evidence_confidence='page-grounded' if sid in local else 'metadata/preview only'))
writecsv('logs/search_and_screening.csv',screen)
req=[]
for sid,reason in zip(requested,reasons):
    r=next(x for x in registry if x['paper_id']==sid)
    req.append(dict(Study_ID=sid,Exact_Title=r['title'],Authors=r['authors'],Year=int(r['year']),Journal=r['journal_or_conference'],DOI=r['DOI'],DOI_URL=r['doi_url'],Publisher_URL=r['landing_url'],Priority='Essential',Status='UNAVAILABLE_USER_CONFIRMED_NO_PURCHASE',Missing_Evidence=reason))
writecsv('logs/pdf_requests.csv',req)
text='# Unavailable sources — no purchase requested\n\nThese are coverage limitations, not active student download requests. Legitimate alternatives have been checked; no purchase is needed to continue. TAGA accepted manuscript and SLI–GA full journal XML have now been obtained. No locked paper is counted as full-text included.\n\n'
for i,r in enumerate(req,1):text+=f"{i}. **{r['Exact_Title']}** — {r['Authors']}; {r['Journal']}, {r['Year']}. DOI [{r['DOI']}]({r['DOI_URL']}); [ScienceDirect]({r['Publisher_URL']}). Priority Essential. Status UNAVAILABLE_USER_CONFIRMED_NO_PURCHASE. Unverified details: {r['Missing_Evidence']}.\n\n"
text+='P004 main PDF obtained; its supplementary document is also needed for training-runtime results, full parameter table, additional feature counts and data details. [Publisher/DOI](https://doi.org/10.1016/j.asoc.2024.112332). Supplementary evidence remains NOT VERIFIED. P007 remains an important pending intrusion-detection candidate outside this first essential batch.\n'
text+='\nLatest access update: the student reports P001, P008, P011 and P015 are purchase-only/inaccessible. No purchase is requested. All coverage-status labels are inactive; do not ask the student to purchase or download these again. Continue with the included pool while preserving this coverage limitation.\n'
(ROOT/'requests/elsevier_pdfs_needed.md').write_text(text)

headers=['Study_ID','Included (Y/N)','Year','Authors','Exact_Title','Journal_or_Conference','Publisher','DOI','Publisher_URL','Local_PDF_Path','Evidence_Level','Research_Objective','Domain_Application','Datasets_and_Sources','Sample_Sizes','Original_Feature_Counts','Class_Distribution_or_Task','Preprocessing','GA_Variant_or_Hybrid','Chromosome_Encoding','GA_Selection','GA_Crossover','GA_Mutation','Fitness_Objectives','Classifier_and_Baselines','Validation_Protocol','Reported_Accuracy_or_F1_or_AUC','Selected_Feature_Count_or_Reduction','Computational_Cost_or_Runtime','Repeated_Runs_and_Statistical_Tests','Code_and_Data_Availability','Main_Findings','Reported_Limitations','Critical_Appraisal','Candidate_Gap_or_Implication','RQ_Tags','Evidence_Page_Table_Figure','Verification_Status','Last_Verified_Date']
primary=[]
details={
'P004':dict(Research_Objective='Select features and suppress noisy views jointly',Domain_Application='Synthetic multi-view classification; TCGA; ADNI/TADPOLE',Datasets_and_Sources='Nine datasets reported: synthetic; TADPOLE; ADNI conversion; six TCGA datasets (pp.8-10)',Sample_Sizes='Synthetic 100/class; TADPOLE 1739 training/814 test; ADNI 332 (166/166); TCGA 2875 aggregate',Original_Feature_Counts='Synthetic five views of 500 each; ADNI 314 MRI + 17 cognitive/demographic; other dimensions in supplements NOT VERIFIED',Class_Distribution_or_Task='Binary and multiclass; ADNI 140 converters/332',Preprocessing='Synthetic noise/views controlled; real data details partly supplemental; fold placement of all preprocessing Unclear',GA_Variant_or_Hybrid='MMFS-GA, multiniche NSGA-II, intra-view and between-view stages',Chromosome_Encoding='Binary intra-view masks; integer 0-5 between-view indices',GA_Selection='Tournament on nondominated rank then crowding distance',GA_Crossover='Binomial intra-view; two-point between-view',GA_Mutation='Random intra-view mutation; shuffle between-view; duplicate repair',Fitness_Objectives='Classification error (balanced accuracy intended) and selected feature count; Eq.5 normalization has ambiguity versus Table2',Classifier_and_Baselines='LDA binary/MLR multiclass; multi-kernel SVM, Lasso-SVM and SFFS baselines',Validation_Protocol='10-fold internal scoring; external ADNI/TADPOLE test sets; TCGA 10-fold evaluation; nested details partly supplemental',Reported_Accuracy_or_F1_or_AUC='ADNI conversion balanced accuracy 0.805 vs Lasso-SVM 0.784 and SFFS 0.745 (Table7); synthetic feature-recovery F1 distinct from class F1',Selected_Feature_Count_or_Reduction='Synthetic unequal-view multiclass Table9: 4+4 informative-view features; zero other views; medians in binary Table4 separately',Computational_Cost_or_Runtime='Six CPU cores (p.8); training time deferred to supplement §2.4 NOT VERIFIED; hardware model NOT REPORTED in main text',Repeated_Runs_and_Statistical_Tests='10 synthetic datasets; SD in tables; some 95% CIs reported; main-text significance testing NOT REPORTED',Code_and_Data_Availability='Data on request (p.16); code URL in S01 is secondary lead, not main-PDF statement',Main_Findings='View-level exclusion and intra-view search improve selected experimental comparisons; ADNI specificity ties Lasso-SVM',Reported_Limitations='Discussion frames curse of dimensionality/noisy-view challenge; no dedicated limitations section',Critical_Appraisal='Classifier/language differences confound pure selector attribution. Feature-recovery F1 must not be class F1. Supplemental runtime still inaccessible. Eq.5 missing averaging factor relative to Table2 requires code check.',Candidate_Gap_or_Implication='Verify metric semantics and timing boundaries, not new method novelty',Evidence_Page_Table_Figure='PDF p.1 cover; pp.5-8 methods; pp.9-10 data/evaluation; p.13 Table7; p.15 Table9; p.16 availability'),
'P006':dict(Research_Objective='Rank nonlinear features then diversify wrapper search with external repository',Domain_Application='Small-sample high-dimensional biomedical classification',Datasets_and_Sources='Colon, CNS, GLI, SMK, Leukemia binary/multiclass, Covid-19, MLL, SRBCT; Table4 p.8',Sample_Sizes='62;60;85;187;72;72;234;72;83',Original_Feature_Counts='2000;7129;22283;19993;7129;7129;15979;12582;2308',Class_Distribution_or_Task='2/3/4 class tasks; per-dataset class distributions Table4 p.8',Preprocessing='Union of top50 CEI, MI and FR yields 121-145 candidates; location of supervised ranking within external validation NOT CLEAR',GA_Variant_or_Hybrid='CMF-AGAwER filter ensemble + adaptive GA with external repository',Chromosome_Encoding='Variable-length feature subsets; initial size 1-10',GA_Selection='Roulette-wheel GA; tournament external repository; truncation survival',GA_Crossover='Variable-length single-point, adaptive Pc initially 0.9',GA_Mutation='Replace selected feature; adaptive Pm initially 0.4, increases on stagnation',Fitness_Objectives='Classifier prediction accuracy; subset compactness emerges from representation, not explicit Pareto objective',Classifier_and_Baselines='Decision tree primary; RBF SVM/Gaussian NB sensitivity; WOA-MC, ATFS, PEFS, EIT-bBOA, EMC-DWES, MPR-MDES, DMC-GAwAR',Validation_Protocol='Table5 average10 runs stratified5-fold CV; Table9 mean3 runs; no distinct untouched outer loop explicitly documented for GA search',Reported_Accuracy_or_F1_or_AUC='Colon Table5: 0.69 before,0.94 after; Table9 competing DMC-GAwAR 0.96,CMF 0.94. No universal superiority.',Selected_Feature_Count_or_Reduction='Table5: Colon6,CNS9,GLI9,SMK8,LeukB9,LeukM5,Covid8,MLL8,SRBCT7',Computational_Cost_or_Runtime='CEI O(m(n log n+l n)); Table8 NFE788 Colon/667 MLL; actual runtime deliberately not reported; i5-4200U1.60GHz,12GB,Windows10,Python3.9.13',Repeated_Runs_and_Statistical_Tests='Table8 caption says3 runs; prose says10 (p.14). Friedman p0.59,Iman-Davenport p0.61 compare classifiers; not equivalence tests.',Code_and_Data_Availability='Implementation/data URL https://github.com/KhaosResearch/CMF-AGAwER (pp.1/15)',Main_Findings='Hybrid reported gains over all-feature DT; Table9 contains multiple baseline counterexamples; NFE includes GA and repository',Reported_Limitations='Future domain evaluation and causality analysis (p.15); authors explicitly favour NFE/complexity over wall time (p.14)',Critical_Appraisal='NFE transparency is useful but not wall time or complete preprocessing cost. Unclear validation nesting weakens generalization inference; failure to reject classifier differences does not prove independence.',Candidate_Gap_or_Implication='Clarify nested filter/search validation and repeat denominators',Evidence_Page_Table_Figure='pp.5-8 methods; p.8 Table4/hardware; p.9 Table5/Eqs19-21; p.10 runs; p.14 Tables8-9 and repeat inconsistency; p.15 availability'),
'P010':dict(Research_Objective='Group correlated features and repair GA subsets within communities',Domain_Application='General classification including microarray',Datasets_and_Sources='SpamBase,Sonar,Arrhythmia,Madelon,Isolet,Colon; main tables six; abstract says nine',Sample_Sizes='4601;208;351;4400;1559;62 (Table1)',Original_Feature_Counts='57;60;279;500;617;2000',Class_Distribution_or_Task='2;2;16;2;26;2 classes (Table1)',Preprocessing='Mean imputation and softmax normalization before random split as described p.14; train-only fitting not established',GA_Variant_or_Hybrid='CDGAFS graph/community-guided repair with Fisher relevance',Chromosome_Encoding='Binary n-feature mask; k communities × omega selected',GA_Selection='Best final chromosome by fitness; parent selector NOT CLEAR in inspected algorithm',GA_Crossover='Single-point; rate0.8',GA_Mutation='Random bit changes; rate0.05; community repair',Fitness_Objectives='Scalar accuracy/redundancy ratio Eq.5; paper calls multi-objective but does not use Pareto survival',Classifier_and_Baselines='kNN fitness; KNN/WEKA SMO SVM/AdaBoost evaluated; PSO,ACO,ABC wrappers',Validation_Protocol='Random train/validation/test partition after normalization; ratios NOT REPORTED; Bayesian parameter optimization described',Reported_Accuracy_or_F1_or_AUC='Colon SVM95.82% vs PSO96.19%; SpamBase SVM93.68% vs PSO92.35%; Table3 p.15',Selected_Feature_Count_or_Reduction='Table4: Colon12.98/2000,SpamBase8.17/57; mean counts across runs',Computational_Cost_or_Runtime='Selection-only Table5: Colon54.95s vs PSO60.82s; hardware3.58GHz CPU8GB RAM; model NOT REPORTED',Repeated_Runs_and_Statistical_Tests='10 independent runs mean/SD; formal significance test NOT REPORTED in full PDF',Code_and_Data_Availability='UCI datasets and https://github.com/mehrdad1988/FeatureSelection stated p.25',Main_Findings='Accuracy and size advantages depend on dataset; explicit selection-only runtime supports narrower efficiency claims',Reported_Limitations='Parameter choice costly; future parameter/community detection improvements (p.24)',Critical_Appraisal='Normalization before partition risks information transfer; not proof of label leakage. Six-table vs nine-abstract inconsistency; scalar formulation must be distinguished from Pareto GA.',Candidate_Gap_or_Implication='Report data preprocessing placement and objective definitions',Evidence_Page_Table_Figure='p.10 Eq.5; p.14 Tables1-2; p.15 Table3; p.17 Table4; p.18 Table5; p.20 timing boundary; p.25 code/data')}
details.update(json.loads((ROOT/'evidence/new_primary_details.json').read_text()))
details.update(json.loads((ROOT/'evidence/additional_fulltext_details.json').read_text()))
details.update(json.loads((ROOT/'evidence/batch2_fulltext_details.json').read_text()))
expanded_preview=json.loads((ROOT/'evidence/expanded_preview_details.json').read_text())
for r in registry:
    if r['kind']=='review':continue
    sid=r['paper_id'];row={h:'NOT VERIFIED' for h in headers}
    row.update(Study_ID=sid,**{'Included (Y/N)':'Y' if r['screening_status']=='INCLUDED' else 'N'},Year=int(r['year']),Authors=r['authors'],Exact_Title=r['title'],Journal_or_Conference=r['journal_or_conference'],Publisher=r['publisher'],DOI=r['DOI'],Publisher_URL=r['landing_url'],Local_PDF_Path=r['pdf_path'] or 'NOT AVAILABLE',Evidence_Level=r['access_level'],RQ_Tags=r['relevance_rq'],Verification_Status=r['screening_status'],Last_Verified_Date='2026-10-09')
    if sid in details:row.update(details[sid])
    elif sid in ['P009','P020','P024']:row['Critical_Appraisal']=r['notes']
    elif sid in expanded_preview:
        row.update(expanded_preview[sid]);row['Evidence_Level']='ABSTRACT_ONLY';row['Evidence_Page_Table_Figure']='Publisher abstract/preview; full-text quantitative details NOT VERIFIED'
    primary.append(row)
writecsv('evidence/primary_studies.csv',primary)
for sid,d in details.items():
    (ROOT/'evidence'/f'{sid}_notes.md').write_text('# '+sid+' extraction\n\n'+ '\n\n'.join('## '+k+'\n'+v for k,v in d.items())+'\n\nAll prose in this extraction is AI-assisted reference material, requiring source verification by the student.\n')

results=[]
def add(sid,dataset,metric,value,units,baseline,page,condition,sd='NOT REPORTED'):
    results.append(dict(Study_ID=sid,Dataset=dataset,Metric=metric,Value=value,Units=units,SD=sd,Baseline=baseline,Protocol=condition,Hardware=details[sid]['Computational_Cost_or_Runtime'],Evidence_Page_Table=page))
for dataset,before,after,k in [('Colon',.69,.94,6),('CNS',.68,.93,9),('GLI',.81,.96,9),('SMK',.56,.77,8),('Leukemia-Binary',.89,.99,9),('Leukemia-Multiclass',.85,.97,5),('Covid-19',.6,.77,8),('MLL',.79,1.,8),('SRBCT',.83,.96,7)]:
    for metric,value,units in [('Accuracy before',before,'proportion'),('Accuracy CMF-AGAwER',after,'proportion'),('Selected features CMF-AGAwER',k,'count')]:add('P006',dataset,metric,value,units,'All-feature decision tree','p.9 Table5; p.10 protocol','10 runs,stratified5-fold CV; nesting unclear')
for method,v in [('MMFS-GA',.805),('LASSO-SVM',.784),('SFFS',.745)]:add('P004','ADNI 5-year conversion','Balanced accuracy '+method,v,'proportion','Within-paper methods','PDF p.13 Table7','166 training/166 test;10-fold internal')
for view,f1,k in [('View1',.83,4),('View2',.58,4)]:
    add('P004','Synthetic unequal-view multiclass '+view,'Feature-recovery F1',f1,'proportion','LASSO-SVM','PDF p.15 Table9; p.10 definition','10 generated datasets; not class F1')
    add('P004','Synthetic unequal-view multiclass '+view,'Selected features',k,'median count','LASSO-SVM','PDF p.15 Table9','10 generated datasets')
add('P004','Synthetic unequal-view multiclass','Classification accuracy',.86,'proportion','LASSO-SVM0.82','PDF p.15 Table9','10 generated datasets',.01)
for dataset,cd,pso,k,n,t in [('SpamBase',93.68,92.35,8.17,57,6.64),('Colon',95.82,96.19,12.98,2000,54.95)]:
    add('P010',dataset,'SVM accuracy CDGAFS',cd,'percent','PSO SVM '+str(pso)+'%','p.15 Table3','10 independent runs; unspecified random partition')
    add('P010',dataset,'Selected features CDGAFS',k,'mean count','Table4 wrappers','p.17 Table4','10 runs')
    add('P010',dataset,'Selection-only runtime CDGAFS',t,'seconds','PSO/ACO/ABC','p.18 Table5;p.20 boundary','10 runs')
writecsv('evidence/reported_results.csv',results)
for sid,dataset,metric,v,units,base,page,protocol in [
('P002','LSVT','Classification accuracy',.9079,'proportion','IPOP-CMA-ES0.9248','p.10 Table7','Best final5-fold fitness over5 runs'),
('P002','LSVT','Time to target',244,'seconds','IPOP-CMA-ES11s','p.10 Table9; p.9 definition','CGGA mean vs comparator minimum of5; censored beyond3x'),
('P003','CuMiDa Leukemia','Macro-F1',.8575,'proportion','DecisionTree-ranking0.7574','p.10 Table6','Aggregate over feature counts2-50 and10 executions;15-fold CV'),
('P003','CuMiDa Breast Cancer','Macro-F1',.9616,'proportion','Lasso-ranking0.9423','p.10 Table7','Aggregate over feature counts2-50 and10 executions;15-fold CV'),
('P003','CuMiDa Leukemia','MOGA execution time',5455.614,'seconds','Baseline combined5138.171s','p.12 Table11','10 executions; reported h:m:s converted to seconds'),
('P005','Parkinson','Classification accuracy',81.57,'percent','Other metaheuristics in Table3','p.9 Table3','Exact split unavailable;14 runs used in statistical assessment'),
('P005','Parkinson','Selected features',236,'count','754 original features','p.9 Table3;p.8 Table1','Specific reported configuration')]:add(sid,dataset,metric,v,units,base,page,protocol)
for metric,v,units in [('Weighted classification F1',76.89,'percent'),('GA search time',702.5,'minutes')]:add('P021','HIKARI-2021,40 features',metric,v,units,'Chi2/PCA/LDA','p.12 Table7','Fixed subset cardinality; search budget/reporting as paper')
for metric,v in [('Jetson batch inference',.7449),('Server batch inference',.0654)]:add('P021','HIKARI-2021,5 features',metric,v,'seconds','Same reference test set','p.14 Table12','Approx111000 test entries; not per-packet latency')
for sid,dataset,metric,v,units,base,page,protocol,sd in [
('P013','Dataset No.1 (Hill-Valley;Table1)','Test-front hypervolume',.703,'HV units','NSGA-II 0.700','PDF p.8 Table4','30 runs;70/30 split;front evaluation,not accuracy',.00868),
('P014','CrohnDisease','Mean accuracy FTGGA',95.22,'percent','mgFPA95.39','PDF p.11 Table5','10 runs;5-fold protocol;outer test unclear',.97),
('P014','CrohnDisease','Mean subset size FTGGA',187,'mean count','mgFPA545.2','PDF p.11 Table5','10 runs;original22283features','NOT REPORTED'),
('P014','CrohnDisease','Mean runtime FTGGA',489.87,'seconds','mgFPA336.01','PDF p.11 Table5; p.13 boundary','10 runs;hardware in evidence notes','NOT REPORTED'),
('P016','SWaT','Mean CV accuracy',.987978,'proportion','LR0.971971','PDF p.11 Table3','5-fold results;distinct from Table5 optimization comparison','NOT REPORTED'),
('P016','SWaT','Optimization comparison accuracy',.98691,'proportion','BGA0.97767','PDF p.11 Table5','Optimization comparison,500iterations','NOT REPORTED'),
('P016','SWaT','Selected features',6,'count','BGA26','PDF p.11 Table5','Optimization comparison,500iterations','NOT REPORTED'),
('P017','WDBC','Test-front IGD DIDA',.010588,'IGD units;lower better','NSGA-II0.00058824','PDF p.9 Table5','20 runs;70/30 split;empirical reference front,not accuracy',.00526),
]:add(sid,dataset,metric,v,units,base,page,protocol,sd)
for sid,dataset,metric,v,units,base,page,protocol,sd in [
('P012','CLN','SVM accuracy TAGA',97.4,'percent','SFS93.5','Accepted manuscript p24 Table7','30runs;LOOCV;best cardinality1-50;outerselectionunclear',1.3),
('P012','CLN','Selected features SVM TAGA',13.9,'mean count','SFS7','Accepted manuscript p24 Table7','30runs;Fisherpool100;original2000',1.0),
('P012','CLN','Subset search time TAGA',123,'seconds','SFS34','Accepted manuscript p34 Table11','Search over cardinalities1-50;i7 2.6GHz64GB','NOT REPORTED'),
('P012','GLI','SVM score transferred kNN mask',96.47,'percent','SVMclassifieroptimal100','Accepted manuscript p33 Table10','Classifiertargettransfer;not outergeneralizationproof','NOT REPORTED'),
('P018','Colon','Reported ANN classifier error',1.37e-19,'ANNerror;not confirmedzero-one rate','GA0.030484','Full journal XML Table7','100percentrankedpopulation;ANNMSEparameterTable6','NOT REPORTED'),
('P018','Colon','Selected features',11,'count','GA1007(tablealignmentverify)','Full journal XML Table7','100percentrank-guidedinitialization;original2000','NOT REPORTED'),
]:add(sid,dataset,metric,v,units,base,page,protocol,sd)
add('P023','covtype','Median accuracy CHC_QX',93.77,'percent','CHC93.36','p8Table2','10runs;fixedCPUtimecomparison;60/20/20partition',.12)
add('P023','semeion','Median accuracy CHC_QX',93.26,'percent','CHC93.73','p8Table2','10runs;fixedCPUtimecomparison',1.61)
writecsv('evidence/reported_results.csv',results)

quality=[]
definitions={'Dataset_provenance':'Named dataset plus source information','Validation_separation':'Distinct untouched evaluation or external test explicitly stated','Training_only_preprocessing':'Preprocessing and feature ranking fitted solely on training folds','Baselines':'Explicit comparison methods','GA_parameters':'Operators/rates/termination or implementation settings','Repeats_uncertainty':'Replicate count and variation information','Runtime_boundary':'Measured timing with defined operation boundary','Hardware':'CPU or hardware resources described','Code_data_statement':'Explicit main-PDF availability statement'}
codes={
'P023':['Yes','Yes','Unclear','Yes','Yes','Yes','Yes','Yes','Yes'],
'P012':['Yes','Unclear','Unclear','Yes','Yes','Yes','Yes','Yes','Yes'],
'P018':['Yes','Unclear','Unclear','Yes','Unclear','Unclear','Unclear','Yes','Yes'],
'P013':['Yes','Yes','Unclear','Yes','Yes','Yes','Not reported','Not reported','Yes'],
'P014':['Yes','Unclear','Unclear','Yes','Yes','Yes','Unclear','Yes','Unclear'],
'P016':['Yes','Unclear','Unclear','Yes','Yes','Not reported','Unclear','Yes','Unclear'],
'P017':['Yes','Yes','Unclear','Yes','Yes','Yes','Not reported','Not reported','Unclear'],
'P021':['Yes','Unclear','Unclear','Yes','Yes','Not reported','Yes','Yes','Unclear'],
'P022':['Yes','Yes','Unclear','Yes','Yes','Not reported','Not reported','Not reported','Yes'],
'P002':['Yes','Unclear','Unclear','Yes','Yes','Yes','Yes','Yes','Not reported'],
'P003':['Yes','Unclear','Unclear','Yes','Yes','Yes','Unclear','Not reported','Yes'],
'P005':['Yes','Unclear','Unclear','Yes','Yes','Yes','Not reported','Not reported','Yes'],
'P004':['Yes','Yes','Unclear','Yes','Yes','Yes','Unclear','Yes','Unclear'],
'P006':['Yes','Unclear','Unclear','Yes','Yes','Yes','Not reported','Yes','Yes'],
'P010':['Yes','Yes','No','Yes','Yes','Yes','Yes','Yes','Yes']}
for sid in details:
    quality.append(dict(Study_ID=sid,**dict(zip(definitions,codes[sid])),Evidence=details[sid]['Evidence_Page_Table_Figure'],Notes='P010 No = p.14 describes normalization before split. P004 hardware Yes = six cores, not full CPU model. No unavailable supplementary details inferred.'))
writecsv('evidence/evidence_quality.csv',quality)
(ROOT/'evidence/quality_definitions.json').write_text(json.dumps(definitions,indent=2))
counts=dict(registry_records=len(registry),secondary_reviews=3,primary_candidates=len(primary),included_primary=sum(x['Included (Y/N)']=='Y' for x in primary),pending_primary=sum(x['Verification_Status'] in ['AWAITING_USER_PDF','PENDING_FULLTEXT'] for x in primary),excluded_primary=sum(x['Verification_Status']=='EXCLUDED' for x in primary),essential_requests=0)
(ROOT/'logs/selection_counts.json').write_text(json.dumps(counts,indent=2))
print(counts)

order=['S01','S02','S03','P004','P006','P010','P002','P003','P005','P021','P022','P013','P014','P016','P017','P012','P018','P023'];refs=[];bib=[]
for i,sid in enumerate(order,1):
    r=next(x for x in registry if x['paper_id']==sid)
    meta_path=ROOT/'logs/metadata'/('P010.json' if sid=='P010' else r['DOI'].replace('/','_')+'.json')
    meta=json.loads(meta_path.read_text())['message']
    names=[' '.join(p[0]+'.' for p in a.get('given','').split())+' '+a.get('family','') for a in meta['author']]
    authors=names[0]+' et al.' if len(names)>6 else ', '.join(names)
    refs.append(dict(number=i,key=sid,title=r['title'],entry=f"[{i}] {authors}, \"{r['title']}\", {r['journal_or_conference']}, vol. {r['volume']}, "+('pp. '+r['pages_or_article_no'] if '-' in r['pages_or_article_no'] else 'Art. no. '+r['pages_or_article_no'])+f", {r['year']}, doi: {r['DOI']}.",DOI=r['DOI']))
    bib.append('@article{'+sid+',\n'+f"  title = {{{r['title']}}},\n  author = {{{r['authors'].replace('; ',' and ')}}},\n  journal = {{{r['journal_or_conference']}}},\n  year = {{{r['year']}}},\n  volume = {{{r['volume']}}},\n  pages = {{{r['pages_or_article_no']}}},\n  doi = {{{r['DOI']}}},\n  url = {{{r['doi_url']}}}\n"+'}')
for i,key,title,url,org in [(19,'B001','Breast Cancer Wisconsin (Diagnostic)','https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic','UCI Machine Learning Repository'),(20,'B002','load_breast_cancer','https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html','scikit-learn developers'),(21,'B003','load_iris','https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html','scikit-learn developers'),(22,'B004','load_wine','https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html','scikit-learn developers'),(23,'B005','load_digits','https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html','scikit-learn developers')]:
    refs.append(dict(number=i,key=key,title=title,entry=f'[{i}] {org}, "{title}", online documentation, accessed Oct. 9, 2026. [Online]. Available: {url}',DOI='N/A'))
    bib.append('@misc{'+key+',\n'+f'  title = {{{title}}},\n  author = {{{{{org}}}}},\n  url = {{{url}}},\n  note = {{Accessed 2026-10-09}}\n'+'}')
(ROOT/'references/references.bib').write_text('\n\n'.join(bib)+'\n');(ROOT/'references/numbered_references.json').write_text(json.dumps(refs,indent=2));(ROOT/'references/ieee_references.txt').write_text('\n\n'.join(x['entry'] for x in refs))
catalog=[]
for r in registry:
    if r['screening_status']=='EXCLUDED':continue
    catalog.append('@article{'+r['paper_id']+',\n'+f"  title = {{{r['title']}}},\n  author = {{{r['authors'].replace('; ',' and ')}}},\n  journal = {{{r['journal_or_conference']}}},\n  year = {{{r['year']}}},\n  volume = {{{r['volume']}}},\n  pages = {{{r['pages_or_article_no']}}},\n  doi = {{{r['DOI']}}},\n  url = {{{r['doi_url']}}}\n"+'}')
catalog += bib[-5:]
(ROOT/'references/literature_catalog.bib').write_text('\n\n'.join(catalog)+'\n')
