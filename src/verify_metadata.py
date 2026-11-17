from pathlib import Path
import requests,json,csv,time
ROOT=Path(__file__).resolve().parents[1]
DOIS=['10.1016/j.swevo.2026.102318','10.1016/j.swevo.2024.101661','10.1016/j.engappai.2023.107136','10.1016/j.knosys.2021.107218','10.1016/j.asoc.2022.108964','10.1016/j.eswa.2024.124518','10.1016/j.asoc.2024.112332','10.1016/j.asoc.2025.112872','10.1016/j.knosys.2024.112345','10.1016/j.cose.2021.102448','10.1016/j.ins.2020.08.083','10.1016/j.ins.2021.02.054']
out=ROOT/'logs/metadata';out.mkdir(exist_ok=True)
rows=[]
for i,doi in enumerate(DOIS):
    response=requests.get('https://api.crossref.org/works/'+doi,timeout=40)
    (out/f'{doi.replace("/","_")}.json').write_text(response.text)
    if response.status_code!=200:
        print(doi,response.status_code);continue
    m=response.json()['message']; authors='; '.join(' '.join([a.get('given',''),a.get('family','')]).strip() for a in m.get('author',[]))
    published=m.get('published',m.get('issued',{})).get('date-parts',[[None]])[0][0]
    row=dict(paper_id=('S'+str(i+1).zfill(2) if i<3 else 'P'+str(i-2).zfill(3)),kind=('review' if i<3 else 'primary_candidate'),title=m['title'][0],authors=authors,year=published,journal_or_conference=m.get('container-title',[''])[0],volume=m.get('volume','NOT REPORTED'),issue=m.get('issue','NOT REPORTED'),pages_or_article_no=m.get('page',m.get('article-number','NOT REPORTED')),publisher=m.get('publisher',''),DOI=m['DOI'],doi_url='https://doi.org/'+m['DOI'],landing_url=m.get('resource',{}).get('primary',{}).get('URL',m['URL']),pdf_path='',access_level='METADATA_ONLY',metadata_verified='Crossref record verified; publisher access pending',fulltext_verified='N',relevance_rq='RQ1;RQ2;RQ3',screening_status='PENDING_FULLTEXT',notes='Crossref deposit is article metadata, not method verification.')
    rows.append(row);print(row['paper_id'],row['title'],row['year'],row['journal_or_conference'],row['landing_url'])
    time.sleep(.15)
with (ROOT/'logs/article_registry.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
