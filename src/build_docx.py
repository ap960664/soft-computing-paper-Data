from pathlib import Path
import re,csv,json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

R=Path(__file__).resolve().parents[1]
doc=Document();sec=doc.sections[0];sec.page_height=Inches(11.7);sec.page_width=Inches(8.3)
for node in list(doc.styles.element.iter(qn('w:pBdr'))):node.getparent().remove(node)
sec.top_margin=sec.bottom_margin=Inches(.75);sec.left_margin=sec.right_margin=Inches(.8)
for name in ['Normal','Title','Heading 1','Heading 2','Caption']:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0);st.font.size=Pt(11 if name=='Normal' else 17 if name=='Title' else 13 if name=='Heading 1' else 11)
    rf=st.element.get_or_add_rPr().find(qn('w:rFonts'))
    for key in list(rf.attrib):
        if 'Theme' in key:del rf.attrib[key]
normal=doc.styles['Normal'];normal.paragraph_format.space_after=Pt(5);normal.paragraph_format.line_spacing=1.05
doc.styles['Caption'].paragraph_format.keep_together=True
doc.styles['Caption'].paragraph_format.line_spacing=1.0
for name in ['Heading 1','Heading 2']:doc.styles[name].paragraph_format.keep_with_next=True
doc.styles['Heading 1'].paragraph_format.space_before=Pt(12)
doc.styles['Heading 1'].paragraph_format.space_after=Pt(6)
doc.styles['Heading 2'].paragraph_format.space_before=Pt(9)
doc.styles['Heading 2'].paragraph_format.space_after=Pt(4)
doc.core_properties.title='Genetic Algorithm-Based Feature Selection for Classification';doc.core_properties.author='Ashish Pathak';doc.core_properties.comments='AI-assisted manuscript. Author details confirmed; independent student authorship and final approval required. See AI_Assistance_Record.md.'
f=sec.footer.paragraphs[0];f.alignment=2
run=f.add_run();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');run._r.addnext(fld)
def table(headers,rows,caption):
    p=doc.add_paragraph(caption,style='Caption');p.paragraph_format.keep_with_next=True
    t=doc.add_table(rows=1,cols=len(headers));t.style='Table Grid'
    for cell,h in zip(t.rows[0].cells,headers):cell.text=h
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        cells=t.add_row().cells
        for c,v in zip(cells,row):c.text=str(v)
    for row in t.rows:
        pr=row._tr.get_or_add_trPr();flag=OxmlElement('w:cantSplit');pr.append(flag)
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(3)
                for run in p.runs:run.font.size=Pt(9)
    for c in t.rows[0].cells:
        for run in c.paragraphs[0].runs:run.bold=True
        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EDF2');c._tc.get_or_add_tcPr().append(shade)
    doc.add_paragraph()

for line in (R/'drafts/review_draft.md').read_text().splitlines():
    if not line.strip():continue
    if line.startswith('# '):
        doc.add_paragraph(line[2:],style='Title')
        p=doc.add_paragraph('Ashish Pathak\nSchool of Computer Science and Engineering\nLovely Professional University, Jalandhar, Punjab, India\nap960664@gmail.com');p.paragraph_format.space_after=Pt(12)
    elif line.startswith('## '):
        p=doc.add_paragraph(line[3:],style='Heading 1')
        if line[3:]=='References':p.paragraph_format.page_break_before=True
    elif line.startswith('### '):doc.add_paragraph(line[4:],style='Heading 2')
    elif line.startswith('!['):
        match=re.match(r'!\[(.*?)\]\((.*?)\)',line);caption,path=match.groups()
        if path=='figures/method_comparison.png':
            # Display the unchanged triptych as larger panels. Native Word crops
            # retain the original PNG and all labels, bars, axes and error bars.
            for panel,crop in enumerate([(0,66667),(33333,33333),(66667,0)]):
                p=doc.add_paragraph();p.alignment=1;p.paragraph_format.keep_with_next=True
                p.paragraph_format.space_after=Pt(2)
                shape=p.add_run().add_picture(str(R/path),width=Inches(3.0))
                shape.height=Inches(3.0*1080/1100)
                shape._inline.docPr.set('descr',caption+f' Panel {panel+1}.')
                fill=shape._inline.graphic.graphicData.pic.blipFill
                cropNode=OxmlElement('a:srcRect');cropNode.set('l',str(crop[0]));cropNode.set('r',str(crop[1]))
                fill.insert(1,cropNode)
        else:
            p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
            shape=p.add_run().add_picture(str(R/path),width=Inches(6.7));shape._inline.docPr.set('descr',caption)
        doc.add_paragraph(caption,style='Caption')
    elif line=='[[TABLE_PRIMARY]]':
        table(['Study','Mechanism','Main evidence limitation'],[
            ['P004 [4]','NSGA-II with intra-view and between-view niching','Supplementary timing unavailable; feature F1 differs from class F1'],
            ['P006 [5]','Filter ensemble plus adaptive GA repository','NFE, not measured wall time; validation nesting unclear'],
            ['P010 [6]','Community-guided binary GA repair','Preprocessing described before partition; scalar fitness'],
            ['P002 [7]','Correlation-guided crossover and mutation','Asymmetric time-to-target aggregation; no independent outer evaluation stated'],
            ['P003 [8]','Ranked feature pools within NSGA-II','Aggregate baseline time; timing-table dataset labels inconsistent'],
            ['P005 [9]','Clustering, arithmetic crossover, adaptive roulette','Exact split design and measured runtime insufficiently reported'],
            ['P021 [10]','Binary GA with fixed cardinality; embedded XGBoost','Large offline search cost; no real-time deployment evaluation'],
            ['P022 [11]','Binary packet-header GA with three-batch evaluation','Accuracy/F1 labels ambiguous; session dependence not excluded'],
            ['P013 [12]','Pareto GA with intervals and adaptive crossover','Front quality differs from final-mask performance'],
            ['P014 [13]','ReliefF and threshold-guided binary GA','Single error objective despite multi-objective feature scoring'],
            ['P016 [14]','Rank fusion and growth-tree GA for ICS','Model-time changes exclude full selection overhead'],
            ['P017 [15]','Dominance initialization and duplicate-analysis GA','Equal NFE does not match duplicate-analysis cost'],
            ['P012 [16]','Fisher + asexual mRMR GA and tabu','Accepted manuscript; validation/cardinality nesting unclear; code demo differs'],
            ['P018 [17]','SLI ranking + mixed initialization wrapper','Full XML; ANN loss/accuracy semantics and dataset labels require checking']
            ,['P023 [18]','CHC with active instance selection and qualitative surrogate','Setup overhead; experimental/theoretical q settings differ; crossover size premise needs checking']
        ],'Table 1. Taxonomy and evidence limits of the fifteen included studies. The original fourteen retain their decisions; P023 is a verified open-access addition. Identifiers link to the literature matrix.')
    elif line=='[[TABLE_MAJOR_DATA]]':
        datasets=json.loads((R/'Results_and_Graphs/major_revision/datasets.json').read_text())
        table(['Dataset','Observations','Features','Classes','Class counts'],[['WDBC' if x['dataset']=='breast_cancer' else x['dataset'].title(),x['n'],x['d'],x['classes'],', '.join(f'{k}: {v}' for k,v in x['class_counts'].items())] for x in datasets],'Table 3. Actual expanded data snapshots. Iris is a finite 15-mask sanity case; the Digits snapshot is the scikit-learn subset, not the entire original UCI collection.')
    elif line=='[[TABLE_MAJOR_RESULTS]]':
        raw=list(csv.DictReader((R/'Results_and_Graphs/major_revision/summary_tidy.csv').open()))
        stability=list(csv.DictReader((R/'Results_and_Graphs/major_revision/stability.csv').open()));rows=[]
        for dataset,label in [('iris','Iris'),('wine','Wine'),('breast_cancer','WDBC'),('digits','Digits')]:
            for method,mlabel in [('all_svm','All'),('anova','ANOVA'),('random','Random'),('basic_ga','Basic'),('cgco_ga','CGCO'),('cgmo_ga','CGMO'),('cgga_adapted','Both')]:
                def v(metric,field='mean'):return float(next(x[field] for x in raw if x['dataset']==dataset and x['method']==method and x['metric']==metric))
                j=float(next(x['pairwise_jaccard_mean'] for x in stability if x['dataset']==dataset and x['method']==method))
                rows.append([label,mlabel,f"{v('balanced_accuracy'):.4f} ± {v('balanced_accuracy','sd'):.4f}",f"{v('feature_count'):.2f}",f"{v('pipeline_seconds'):.4f}",f'{j:.3f}'])
        table(['Dataset','Method','Balanced accuracy ± SD','Mean features','Pipeline seconds','Jaccard'],rows,'Table 4. Expanded outputs: 15 outer evaluations per dataset/method. SD and Jaccard are descriptive; folds and mask pairs are dependent. Iris searches complete all masks. Method abbreviations are defined in Figure 6.')
    elif line=='[[TABLE_EXPERIMENT]]':
        summary=list(csv.DictReader((R/'results/summary_metrics.csv').open()));rows=[]
        for method,label in [('all_svm','All features'),('filter_svm','ANOVA filter'),('ga_svm','GA search'),('random_svm','Random search')]:
            def get(metric):return next(x for x in summary if x['method']==method and x['metric']==metric)
            ba=get('balanced_accuracy');fc=get('feature_count');tm=get('total_train_seconds')
            rows.append([label,f"{float(ba['mean']):.4f} ± {float(ba['sd']):.4f}",f"{float(fc['mean']):.2f} ± {float(fc['sd']):.2f}",f"{float(tm['mean']):.4f}"])
        table(['Method','Balanced accuracy mean ± SD','Features mean ± SD','Selection + fit seconds'],rows,'Table 2. Actual held-out demonstration results from results/summary_metrics.csv. Each method has 15 outer evaluations; SD is descriptive and folds are not independent.')
    elif line=='[[REFERENCES]]':
        for ref in json.loads((R/'references/numbered_references.json').read_text()):
            p=doc.add_paragraph(ref['entry']);p.paragraph_format.space_after=Pt(1.5)
            p.paragraph_format.line_spacing=1.0
            p.paragraph_format.left_indent=Inches(.28);p.paragraph_format.first_line_indent=Inches(-.28)
            for run in p.runs:run.font.size=Pt(9.5)
    elif line in ['[[EQUATION]]','[[GUIDANCE_EQUATION]]']:
        p=doc.add_paragraph();p.alignment=1
        math=OxmlElement('m:oMath')
        def mr(text):
            r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
        def sub(base,index):
            node=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));s=OxmlElement('m:sub');s.append(mr(index));node.append(e);node.append(s);return node
        if line=='[[EQUATION]]':
            math.append(mr('F(m) = 0.9 '));math.append(sub('BA','inner'));math.append(mr('(m) + 0.1 (1 − k/d)     (1)'))
        else:
            math.append(mr('J(S) = '));fraction=OxmlElement('m:f');num=OxmlElement('m:num');den=OxmlElement('m:den')
            num.append(sub('Σ','i ∈ S'));num.append(mr(' SU('));num.append(sub('x','i'));num.append(mr(',y)'))
            rad=OxmlElement('m:rad');pr=OxmlElement('m:radPr');hide=OxmlElement('m:degHide');hide.set(qn('m:val'),'1');pr.append(hide);rad.append(pr);rad.append(OxmlElement('m:deg'));e=OxmlElement('m:e')
            e.append(mr('k + 2 '));e.append(sub('Σ','i < j; i,j ∈ S'));e.append(mr(' SU('));e.append(sub('x','i'));e.append(mr(','));e.append(sub('x','j'));e.append(mr(')'));rad.append(e);den.append(rad);fraction.append(num);fraction.append(den);math.append(fraction);math.append(mr('     (2)'))
        p._p.append(math)
    else:doc.add_paragraph(line)
doc.save(R/'Final_Research_Paper.docx');print('Saved Final_Research_Paper.docx')
