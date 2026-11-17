from pathlib import Path
import requests,json,html,time
R=Path(__file__).resolve().parents[1]
dois=['10.1016/j.ins.2021.01.020','10.1016/j.asoc.2022.109420','10.1016/j.asoc.2023.110765','10.1016/j.cie.2020.106345','10.1016/j.cose.2023.103675','10.1016/j.swevo.2025.101914','10.1007/s11227-022-04650-w','10.1007/s11227-020-03378-9','10.1186/s40537-024-00887-9','10.3390/systems12070243']
rows=[]
for i,doi in enumerate(dois,12):
    sid=f'P{i:03d}';r=requests.get('https://api.crossref.org/works/'+doi,timeout=35);r.raise_for_status();m=r.json()['message']
    (R/'logs/metadata'/f'{doi.replace("/","_")}.json').write_text(r.text)
    # Prefer issue year where online-first year differs; retain full date metadata.
    year=m.get('published-print',m.get('published',m['issued']))['date-parts'][0][0]
    authors='; '.join(a.get('given','')+' '+a.get('family','') for a in m.get('author',[]))
    row=dict(paper_id=sid,kind='primary_candidate',title=html.unescape(m['title'][0]),authors=authors,year=year,journal_or_conference=m['container-title'][0],volume=m.get('volume','NOT REPORTED'),issue=m.get('issue','NOT REPORTED'),pages_or_article_no=m.get('page',m.get('article-number','NOT REPORTED')),publisher=m['publisher'],DOI=m['DOI'],doi_url='https://doi.org/'+m['DOI'],landing_url=m.get('resource',{}).get('primary',{}).get('URL',m['URL']),pdf_path='',access_level='METADATA_ONLY',metadata_verified='Crossref verified; publisher relevance cross-check pending',fulltext_verified='N',relevance_rq='RQ1;RQ2;RQ3',screening_status='PENDING_FULLTEXT',notes='Expanded GA-central classification lead; no numerical results inferred from surveys.')
    rows.append(row);print(sid,year,row['title'],row['journal_or_conference'],flush=True)
    url='https://link.springer.com/content/pdf/'+doi+'.pdf' if doi.startswith(('10.1007','10.1186')) else None
    if url:
        try:
            p=requests.get(url,timeout=25)
            if p.status_code==200 and p.content[:4]==b'%PDF':
                path=R/'literature/verified'/f'{sid}.pdf';path.write_bytes(p.content);row['pdf_path']=str(path.relative_to(R));row['access_level']='PDF_DOWNLOADED_PENDING_EXTRACTION';print('Downloaded',sid,flush=True)
            else:print('PDF status',sid,p.status_code,flush=True)
        except requests.RequestException as exc:print(sid,str(exc),flush=True)
    time.sleep(.1)
(R/'logs/expanded_candidates.json').write_text(json.dumps(rows,indent=2))
print('Verified additional metadata',len(rows),flush=True)
