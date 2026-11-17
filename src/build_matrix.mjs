import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const tabs=JSON.parse(await fs.readFile(root+'tmp/matrix_data.json','utf8'));
const wb=Workbook.create();
for(const name of Object.keys(tabs))wb.worksheets.add(name);
for(const [name,rows] of Object.entries(tabs)){
  const sh=wb.worksheets.getItem(name);sh.showGridLines=false;
  const range=sh.getRangeByIndexes(0,0,rows.length,rows[0].length);range.values=rows;
  range.format.font={name:'Arial',size:10,color:'#111827'};range.format.wrapText=true;range.format.verticalAlignment='top';range.format.columnWidth=28;range.format.rowHeight=110;
  if(name==='Expanded_Results'||name==='Expanded_Stability')range.format.rowHeight=46;
  const head=sh.getRangeByIndexes(0,0,1,rows[0].length);head.format.fill='#243746';head.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};head.format.rowHeight=46;
  sh.freezePanes.freezeRows(1);
  if(name==='Primary_Studies'){
    sh.getRange('A:A').format.columnWidth=12;sh.getRange('B:C').format.columnWidth=14;sh.getRange('E:E').format.columnWidth=55;
    sh.getRange('L:AM').format.columnWidth=48;range.format.rowHeight=175;head.format.rowHeight=80;
  }
  if(name==='Summary'||name==='READ_ME'){
    sh.getRange('A:A').format.columnWidth=40;sh.getRange('B:B').format.columnWidth=90;range.format.rowHeight=42;
  } else {
    sh.tables.add(range.address,true,'T_'+name);
  }
  for(let j=0;j<rows[0].length;j++){
    if(/URL|doi_url|landing_url|Publisher_URL/.test(rows[0][j])){
      for(let i=1;i<rows.length;i++)if(String(rows[i][j]).startsWith('https://')) sh.getCell(i,j).formulas=[['=HYPERLINK("'+String(rows[i][j]).replaceAll('"','""')+'","'+String(rows[i][j]).replaceAll('"','""')+'")']];
    }
  }
}
const summary=wb.worksheets.getItem('Summary');
summary.getRange('B2').formulas=[['=COUNTIF(Primary_Studies!B2:B'+tabs.Primary_Studies.length+',"Y")']];
summary.getRange('B3').formulas=[['=COUNTIF(Screening!L2:L'+tabs.Screening.length+',"AWAITING_USER_PDF")+COUNTIF(Screening!L2:L'+tabs.Screening.length+',"PENDING_FULLTEXT")']];
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Summary!A1:B9',include:'values,formulas',tableMaxRows:9,tableMaxCols:2})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20}})).ndjson);
for(const [name,rows] of Object.entries(tabs)){
  const cols=Math.min(4,rows[0].length);const letters=['A','B','C','D'];
  const p=await wb.render({sheetName:name,range:'A1:'+letters[cols-1]+Math.min(rows.length,4),scale:1.5});
  await fs.writeFile(root+'tmp/'+name+'_preview.png',new Uint8Array(await p.arrayBuffer()));
}
for (const [label,range] of [['titles','E1:H4'],['results','AA1:AD4'],['provenance','AK1:AM4']]) {
 const p=await wb.render({sheetName:'Primary_Studies',range,scale:1.2});
 await fs.writeFile(root+'tmp/primary_'+label+'_preview.png',new Uint8Array(await p.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(root+'Complete_Literature_Matrix.xlsx');
console.log('Saved Complete_Literature_Matrix.xlsx');
