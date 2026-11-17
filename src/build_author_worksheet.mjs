import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=fileURLToPath(new URL('../',import.meta.url));const tabs=JSON.parse(await fs.readFile(root+'tmp/author_worksheet_data.json','utf8'));const wb=Workbook.create();
for(const [name,rows] of Object.entries(tabs)){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;const r=sh.getRangeByIndexes(0,0,rows.length,rows[0].length);r.values=rows;r.format.font={name:'Arial',size:10,color:'#111827'};r.format.columnWidth=36;r.format.rowHeight=150;r.format.wrapText=true;r.format.verticalAlignment='top';
 sh.getRange('A:A').format.columnWidth=18;const h=sh.getRangeByIndexes(0,0,1,rows[0].length);h.format.fill='#243746';h.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};h.format.rowHeight=50;sh.freezePanes.freezeRows(1);sh.tables.add(r.address,true,'T_'+name);
 if(name==='Manuscript_Claims'){sh.getRange('C:C').format.columnWidth=115;sh.getRange('E:E').format.columnWidth=100;r.format.rowHeight=290;h.format.rowHeight=50;}
 if(name==='Method_Evidence'){sh.getRange('B:B').format.columnWidth=70;sh.getRange('D:E').format.columnWidth=80;}
 if(['Expanded_Results','Expanded_Stability','Experiment_Summaries','Audit_Checks','Author_Details'].includes(name)){r.format.rowHeight=46;h.format.rowHeight=50;}
 if(name==='Manual_Source_Checks'){
  sh.getRange('A:B').format.columnWidth=16;sh.getRange('C:C').format.columnWidth=22;
  sh.getRange('D:F').format.columnWidth=66;sh.getRange('G:H').format.columnWidth=28;
  r.format.rowHeight=170;h.format.rowHeight=50;
  sh.getRange('G2:G'+rows.length).dataValidation={rule:{type:'list',values:['PENDING','VERIFIED','CORRECTION REQUIRED','CAVEAT RETAINED']}};
 }
 const p=await wb.render({sheetName:name,range:'A1:D3',scale:1});await fs.writeFile(root+'tmp/author_'+name+'_preview.png',new Uint8Array(await p.arrayBuffer()));
}
wb.recalculate();console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#VALUE!|#DIV/0!',options:{useRegex:true,maxResults:10}})).ndjson);
const finalChecks=await wb.render({sheetName:'Manual_Source_Checks',range:'C28:F30',scale:1});await fs.writeFile(root+'tmp/author_final_checks_preview.png',new Uint8Array(await finalChecks.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(wb)).save(root+'Author_Verification_Worksheet.xlsx');console.log('Saved author workbook');
