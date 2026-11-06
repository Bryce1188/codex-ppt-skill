import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { buildDeck } from '../scripts/build_editable_deck.mjs';

const options = { moduleRoot: process.env.RUNTIME_NODE_MODULES };
const sharedProfile = JSON.parse(await fs.readFile(new URL('../references/design-profiles/technical-editorial.json', import.meta.url), 'utf8'));
const node = (id, left) => ({ type:'shape', id, position:{left,top:100,width:200,height:100} });
const fixture = () => ({
 fontFamily:'Arial',
 data:{sample:{values:[['Field','Role'],['id','PK']]}},
 slides:[{elements:[
  node('source',60),node('target',500),
  {type:'text',text:'Editable diagram',position:{left:60,top:30,width:600,height:50},fontSize:32},
  {type:'table',dataKey:'sample',position:{left:60,top:300,width:640,height:180},fontSize:24,
   borderColor:'#CBD5E1',borderWidth:1,cellPadding:{left:12,right:12,top:10,bottom:10},
   headerColor:'#FFFFFF',bodyColor:'#173A32'}
 ],connectors:[{from:'source',to:'target',fromSide:'right',toSide:'left'}]}]
});
test('rejects duplicate diagram ids',async()=>{
 const s=fixture();s.slides[0].elements[1].id='source';
 await assert.rejects(buildDeck(s,options),/unique diagram shape id/);
});
test('rejects a missing connector endpoint',async()=>{
 const s=fixture();s.slides[0].connectors[0].to='missing';
 await assert.rejects(buildDeck(s,options),/endpoint not found/);
});
test('rejects an invalid attachment side',async()=>{
 const s=fixture();s.slides[0].connectors[0].fromSide='middle';
 await assert.rejects(buildDeck(s,options),/sides required/);
});
test('rejects self connectors',async()=>{
 const s=fixture();s.slides[0].connectors[0].to='source';
 await assert.rejects(buildDeck(s,options),/self connectors/);
});
test('exports attached directional connectors and styled native tables',async()=>{
 const s=fixture();
 s.slides[0].connectors.push({from:'target',to:'source',fromSide:'bottom',toSide:'bottom',kind:'elbow',arrow:false});
 const {presentation,PresentationFile}=await buildDeck(s,options);
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'ppt-diagram-test-'));
 const output=path.join(dir,'native.pptx');
 await (await PresentationFile.exportPptx(presentation)).save(output);
 const check=`import sys, zipfile, xml.etree.ElementTree as E
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(sys.argv[1]) as z:
 r=E.fromstring(z.read('ppt/slides/slide1.xml'))
 shapes={s.find('p:nvSpPr/p:cNvPr',ns).get('name'):s.find('p:nvSpPr/p:cNvPr',ns).get('id') for s in r.findall('.//p:sp',ns)}
 lines=r.findall('.//p:cxnSp',ns)
 assert len(lines)==2, 'Native connectors missing'
 first=next(s for s in lines if s.find('.//a:stCxn',ns).get('id')==shapes['source'])
 second=next(s for s in lines if s.find('.//a:stCxn',ns).get('id')==shapes['target'])
 assert first.find('.//a:stCxn',ns).get('id')==shapes['source']
 assert first.find('.//a:endCxn',ns).get('id')==shapes['target']
 assert first.find('.//a:tailEnd',ns).get('type')=='arrow', 'Arrow must point to target'
 assert first.find('.//a:headEnd',ns).get('type')=='none'
 assert second.find('.//a:tailEnd',ns).get('type')=='none'
 table=r.find('.//a:tbl',ns)
 assert table is not None and len(table.findall('.//a:tc',ns))==4
 cells=table.findall('.//a:tcPr',ns)
 assert all(int(c.get('marL','-1'))==114300 for c in cells), '12px left padding did not export'
 assert all(int(c.get('marT','-1'))==95250 for c in cells), '10px top padding did not export'
 print('Native endpoints, arrow direction, table cells and padding verified')
`;
 const result=execFileSync(process.env.RUNTIME_PYTHON??'python',['-c',check,output],{encoding:'utf8'});
 assert.match(result,/verified/);
});
test('shared design values reach native PPTX objects', async () => {
 const s = {designProfile:sharedProfile,slides:[{elements:[
  {type:'text',styleRole:'title',text:'Native profile title'},
  {type:'shape',styleRole:'focus',id:'service',position:{left:64,top:220,width:300,height:140}}
 ]}]};
 const {presentation,PresentationFile,designReport}=await buildDeck(s,options);
 assert.equal(designReport.profileId, sharedProfile.id);
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'ppt-profile-test-'));
 const output=path.join(dir,'profile.pptx');
 await (await PresentationFile.exportPptx(presentation)).save(output);
 const check='import sys,zipfile,xml.etree.ElementTree as E\n' +
 "ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}\n" +
 "with zipfile.ZipFile(sys.argv[1]) as z:\n" +
 " r=E.fromstring(z.read('ppt/slides/slide1.xml'))\n" +
 " assert r.find('.//p:bg/p:bgPr/a:solidFill/a:srgbClr',ns).get('val')=='F7F8FC'\n" +
 " title=next(s for s in r.findall('.//p:sp',ns) if 'Native profile title' in ''.join(s.itertext()))\n" +
 " off=title.find('p:spPr/a:xfrm/a:off',ns)\n" +
 " assert int(off.get('x'))==64*9525 and int(off.get('y'))==76*9525\n" +
 " assert title.find('.//a:rPr',ns).get('sz')=='3300'\n" +
 " assert any(e.get('val')=='EAF0FF' for e in r.findall('.//p:sp/p:spPr/a:solidFill/a:srgbClr',ns))\n" +
 " print('Native design profile verified')\n";
 const result=execFileSync(process.env.RUNTIME_PYTHON??'python',['-c',check,output],{encoding:'utf8'});
 assert.match(result,/verified/);
});
