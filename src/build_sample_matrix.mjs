import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=fileURLToPath(new URL('../',import.meta.url));
const input=JSON.parse(await fs.readFile(root+'tmp/sample_style_matrix_data.json','utf8'));
const out=root+'outputs/01a11ce9-c69d-77d1-86a7-82e828ff3742/';
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const sh=wb.worksheets.add('Sheet1');
const count=input.rows.length;const range=sh.getRange('A1:M'+count);range.values=input.rows;
range.format.font={name:'Arial',size:11,color:'#111111'};
range.format.wrapText=true;range.format.verticalAlignment='top';
// Plain single-sheet layout follows the sample; widths expand long scholarly text.
const widths=[8.86,10,31,44,58,24,12,42,56,44,58,54,70];
for(let j=0;j<13;j++)sh.getRangeByIndexes(0,j,count,1).format.columnWidth=widths[j];
for(let i=1;i<input.rows.length;i++){
 const lines=input.rows[i].map((v,j)=>String(v).split('\n').reduce((n,t)=>n+Math.max(1,Math.ceil(t.length/(widths[j]*.9))),0));
 sh.getRangeByIndexes(i,0,1,13).format.rowHeight=Math.min(409,Math.max(150,Math.max(...lines)*14.5+12));
}
sh.getRange('A1:M1').format.font={name:'Arial',size:11,bold:true,color:'#111111'};
sh.getRange('A1:M1').format.rowHeight=40;
sh.getRange('A1:M1').format.verticalAlignment='center';
sh.getRange('A2:B'+count).setNumberFormat('0');sh.getRange('G2:G'+count).setNumberFormat('0');
sh.freezePanes.freezeRows(1);sh.showGridLines=true;
for(const t of input.trace){
 wb.notes.add({id:'citation-'+t.row,target:{cell:{sheetName:'Sheet1',sheetId:sh.sheetId,address:'G'+t.row}},authorId:'',createdAt:'',body:{plainText:'Source: '+t.citation_source+'. Metadata record: https://api.crossref.org/works/'+input.rows[t.row-1][12].match(/https:\/\/doi.org\/([^\n]+)/)[1]}});
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Sheet1!A1:M1',include:'values',tableMaxRows:1,tableMaxCols:13})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20}})).ndjson);
for(const [label,r] of [['identity','A1:D3'],['abstract','D1:F3'],['methods','G1:J3'],['evidence','K1:M3'],['pending','K19:M21']]){
 const p=await wb.render({sheetName:'Sheet1',range:r,scale:1});
 await fs.writeFile(root+'tmp/sample_matrix_'+label+'.png',new Uint8Array(await p.arrayBuffer()));
}
const addedRow=input.rows.findIndex(r=>String(r[3]).startsWith('Fast Genetic'))+1;
const addedPreview=await wb.render({sheetName:'Sheet1',range:'H'+addedRow+':M'+addedRow,scale:1});await fs.writeFile(root+'tmp/sample_matrix_new_study.png',new Uint8Array(await addedPreview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(wb)).save(out+'Literature_Matrix_Sample_Format.xlsx');
console.log('Saved separate sample-format matrix with '+(count-1)+' records and 13 unchanged headings.');
