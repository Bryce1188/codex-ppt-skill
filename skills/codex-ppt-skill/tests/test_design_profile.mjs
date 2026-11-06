import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { applyDesignProfile, resolveDesignProfile } from '../scripts/design_profile.mjs';

const profile = JSON.parse(await fs.readFile(new URL('../references/design-profiles/technical-editorial.json', import.meta.url), 'utf8'));
const fixture = () => ({
  slides: [1, 2].map(number => ({ elements: [
    { type: 'text', styleRole: 'title', text: 'Page ' + number },
    { type: 'text', styleRole: 'body', text: 'Evidence', position: {left:64,top:184,width:600,height:100} },
    { type: 'shape', styleRole: 'node', id: 'service', position:{left:64,top:320,width:300,height:120} }
  ] }))
});
test('applies the same visual system across pages without changing input', () => {
  const input = fixture(), before = structuredClone(input);
  const { spec, report } = applyDesignProfile(input, profile);
  assert.deepEqual(input, before);
  assert.equal(spec.slides[0].background, spec.slides[1].background);
  assert.deepEqual(spec.slides[0].elements[0].position, profile.textStyles.title.position);
  assert.equal(spec.slides[0].elements[1].fontSize, profile.textStyles.body.fontSize);
  assert.equal(spec.slides[1].elements[2].lineColor, profile.shapeStyles.node.lineColor);
  assert.equal(report.exceptions.length, 0);
});
test('rejects unexplained background, typography and heading-position drift', () => {
  for (const mutate of [
    s => { s.slides[1].background = '#000000'; },
    s => { s.slides[1].elements[0].fontSize = 31; },
    s => { s.slides[1].elements[0].position = {left:80,top:90,width:800,height:60}; },
    s => { s.slides[1].elements[2].lineColor = '#FF0000'; }
  ]) {
    const spec = fixture(); mutate(spec);
    assert.throws(() => applyDesignProfile(spec, profile), /design drift/);
  }
});
test('rejects nested textStyle overrides that bypass the shared style', () => {
  const spec = fixture(); spec.slides[0].elements[0].textStyle = {fontSize:12};
  assert.throws(() => applyDesignProfile(spec, profile), /textStyle bypasses/);
});
test('records deliberate local exceptions without changing other pages', () => {
  const spec = fixture();
  Object.assign(spec.slides[0].elements[0], {fontSize:40,designException:'用户指定的长标题需要这一页使用较小字级'});
  const result = applyDesignProfile(spec, profile);
  assert.equal(result.spec.slides[0].elements[0].fontSize, 40);
  assert.equal(result.spec.slides[1].elements[0].fontSize, profile.textStyles.title.fontSize);
  assert.equal(result.report.exceptions.length, 1);
});
test('rejects unknown roles and alternate content-page backgrounds', () => {
  const spec = fixture(); spec.slides[0].elements[1].styleRole = 'unknown';
  assert.throws(() => applyDesignProfile(spec, profile), /known styleRole/);
  const spec2 = fixture(); spec2.slides[0].backgroundRole = 'section';
  assert.throws(() => applyDesignProfile(spec2, profile), /cover or section/);
});
test('preserves old specs without imposing a profile', async () => {
  const input = {fontFamily:'Arial',slides:[]};
  const output = await resolveDesignProfile(input);
  assert.equal(output.spec, input);
  assert.equal(output.report, null);
});
test('global profile edits propagate to all pages', () => {
  const changed = structuredClone(profile);
  changed.textStyles.title.color = '#7D3220';
  const { spec } = applyDesignProfile(fixture(), changed);
  assert.ok(spec.slides.every(page => page.elements[0].color === '#7D3220'));
});
test('applies the chart palette while preserving exact source values', () => {
  const spec = fixture(), palette = ['#3155D9', '#7A8CB3'];
  spec.data = { result: {categories:['A','B'],series:[{name:'Measured',values:[1.25,3.5]}]} };
  spec.slides[0].elements.push({type:'chart',dataKey:'result',position:{left:64,top:320,width:600,height:240}});
  const changed = {...profile,chartPalette:palette};
  const { spec: resolved } = applyDesignProfile(spec, changed);
  assert.equal(resolved.data.result.series[0].fill, palette[0]);
  assert.deepEqual(resolved.data.result.series[0].values, [1.25,3.5]);
  assert.equal(spec.data.result.series[0].fill, undefined);
});
