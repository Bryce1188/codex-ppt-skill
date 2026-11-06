#!/usr/bin/env node
// Render the same native content with three palettes. No image service is used.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildDeck} from '../../scripts/build_editable_deck.mjs';
const args = process.argv.slice(2);
const opts = {};
for(let i=0;i<args.length;i+=2) {
  if(!['--module-root','--out'].includes(args[i]) || !args[i+1]) throw new Error('Use --module-root <host node_modules> --out <new directory>');
  opts[args[i]] = args[i+1];
}
if(!opts['--out']) throw new Error('--out is required');
const directory = path.resolve(opts['--out']);
try { await fs.access(directory); throw new Error('Output directory exists; choose a new one.'); }
catch(error) { if(error.code !== 'ENOENT') throw error; }
await fs.mkdir(directory,{recursive:true});
const source = JSON.parse(await fs.readFile(path.join(path.dirname(fileURLToPath(import.meta.url)),'deck.json'),'utf8'));
const palettes = [
 {id:'clean',background:'#F8FAFB',text:'#162B3B',muted:'#5E7180',accent:'#087E8B'},
 {id:'warm',background:'#FBF7F0',text:'#433029',muted:'#79695C',accent:'#A24536'},
 {id:'dark',background:'#10212E',text:'#F1F7FA',muted:'#B6CBD7',accent:'#58D4C0'}
];
for(const palette of palettes){
 const spec = structuredClone(source);
 spec.slides = [spec.slides[3]];
 spec.expectedSlideCount = 1;
 spec.slides[0].background = palette.background;
 spec.data.distribution.series[0].fill = palette.accent;
 for(const el of spec.slides[0].elements){
   el.color = el.color === '#162B3B' ? palette.text : palette.muted;
 }
 const {presentation} = await buildDeck(spec,{moduleRoot:opts['--module-root']});
 const png = await presentation.export({slide:presentation.slides.items[0],format:'png',scale:1});
 await fs.writeFile(path.join(directory,`${palette.id}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log('Rendered three palettes from the same content: '+directory);
