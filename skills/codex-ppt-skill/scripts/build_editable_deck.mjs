#!/usr/bin/env node
/** Build native PPTX evidence from an explicit pixel-based JSON spec.
 * Requires @oai/artifact-tool supplied by the host. Does not install packages,
 * call image services, flatten slides, or overwrite an existing output.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { resolveDesignProfile } from './design_profile.mjs';

function check(ok, message) { if (!ok) throw new Error(message); }
function box(position, canvas, label) {
  check(position && ['left','top','width','height'].every(k => Number.isFinite(position[k])), `${label}: finite pixel position required`);
  check(position.width > 0 && position.height > 0 && position.left >= 0 && position.top >= 0 && position.left + position.width <= canvas.width + .1 && position.top + position.height <= canvas.height + .1, `${label}: object outside slide or nonpositive size`);
  return position;
}
async function loadArtifact(moduleRoot) {
  if (!moduleRoot) return import('@oai/artifact-tool');
  const require = createRequire(path.join(path.resolve(moduleRoot), '__ppt_resolve__.cjs'));
  return import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
}
export async function buildDeck(spec, { specDir = '.', moduleRoot } = {}) {
  const resolved = await resolveDesignProfile(spec, specDir);
  spec = resolved.spec;
  check(spec && Array.isArray(spec.slides) && spec.slides.length, 'spec.slides must be nonempty');
  check(typeof spec.fontFamily === 'string' && spec.fontFamily.trim(), 'fontFamily is required; verify it exists in the rendering environment');
  const canvas = spec.slideSize ?? { width: 1280, height: 720 };
  check([canvas.width, canvas.height].every(n => Number.isFinite(n) && n > 0), 'Invalid slideSize');
  if (spec.expectedSlideCount !== undefined) check(spec.expectedSlideCount === spec.slides.length, 'expectedSlideCount mismatch');
  const { Presentation, PresentationFile } = await loadArtifact(moduleRoot);
  const presentation = Presentation.create({ slideSize: canvas });
  const counts = [];
  for (const [index, page] of spec.slides.entries()) {
    const slide = presentation.slides.add();
    slide.background.fill = page.background ?? '#FFFFFF';
    const summary = { slide: index + 1, texts: 0, charts: 0, tables: 0, images: 0, diagramShapes: 0, connectors: 0 };
    const diagramNodes = new Map();
    const elements = page.elements ?? [];
    check(elements.length, `Slide ${index + 1}: empty page`);
    for (const [ei, el] of elements.entries()) {
      const label = `Slide ${index + 1}, element ${ei + 1}`;
      const position = box(el.position, canvas, label);
      if (el.type === 'shape') {
        check(typeof el.id === 'string' && el.id && !diagramNodes.has(el.id), `${label}: unique diagram shape id required`);
        check(['rect', 'roundRect', 'ellipse'].includes(el.geometry ?? 'rect'), `${label}: unsupported diagram geometry`);
        const node = slide.shapes.add({ geometry: el.geometry ?? 'rect', name: el.id, position,
          fill: el.fill ?? 'none', line: { fill: el.lineColor ?? '#334155', width: el.lineWidth ?? 1, style: el.lineStyle ?? 'solid' } });
        diagramNodes.set(el.id, node);
        summary.diagramShapes++;
      } else if (el.type === 'text') {
        const value = el.textKey ? spec.copy?.[el.textKey] : el.text;
        check(typeof value === 'string' && value.trim(), `${label}: nonempty text or valid textKey required`);
        const shape = slide.shapes.add({ geometry: 'textbox', name: el.id ?? `text-${ei + 1}`, position, fill: 'none', line: { fill: 'none', width: 0 } });
        shape.text = value;
        if (el.insets !== undefined) shape.text.insets = el.insets;
        shape.text.style = { typeface: spec.fontFamily, fontSize: el.fontSize ?? 28, color: el.color ?? '#152536', bold: el.bold ?? false, alignment: el.align ?? 'left', autoFit: 'none', ...el.textStyle };
        summary.texts++;
      } else if (el.type === 'chart') {
        const data = spec.data?.[el.dataKey];
        check(data && Array.isArray(data.categories) && data.categories.length && Array.isArray(data.series) && data.series.length, `${label}: dataKey must resolve to categories and series`);
        for (const s of data.series) check(typeof s.name === 'string' && Array.isArray(s.values) && s.values.length === data.categories.length && s.values.every(Number.isFinite), `${label}: chart values must match categories and be finite numbers`);
        const font = { typeface: spec.fontFamily, fontSize: el.labelSize ?? 23, fill: el.color ?? '#334155' };
        const opts = el.options ?? {};
        check(!['position','categories','series'].some(k => Object.hasOwn(opts, k)), `${label}: put data in spec.data and geometry in position`);
        slide.charts.add(el.chartType ?? 'bar', {
          ...opts, position, categories: data.categories, series: data.series,
          hasLegend: opts.hasLegend ?? data.series.length > 1,
          ...(opts.title ? { titleTextStyle: { ...font, ...opts.titleTextStyle } } : {}),
          xAxis: { ...opts.xAxis, textStyle: { ...font, ...opts.xAxis?.textStyle } },
          yAxis: { ...opts.yAxis, textStyle: { ...font, ...opts.yAxis?.textStyle } },
          dataLabels: { showValue: true, position: ['stacked','percentStacked'].includes(opts.barOptions?.grouping) ? 'center' : 'outEnd', ...opts.dataLabels, textStyle: { ...font, ...opts.dataLabels?.textStyle } },
          legend: { ...opts.legend, textStyle: { ...font, ...opts.legend?.textStyle } },
        });
        summary.charts++;
      } else if (el.type === 'table') {
        const data = spec.data?.[el.dataKey];
        const values = data?.values;
        check(Array.isArray(values) && values.length && Array.isArray(values[0]) && values[0].length && values.every(r => Array.isArray(r) && r.length === values[0].length), `${label}: table dataKey must resolve to a rectangular values matrix`);
        const table = slide.tables.add({ rows: values.length, columns: values[0].length, ...position, values, ...(el.columnWidths ? { columnWidths: el.columnWidths } : {}) });
        if (el.borderColor !== undefined) table.borders.assign({ fill: el.borderColor, width: el.borderWidth ?? 1, style: 'solid' });
        if (el.cellPadding !== undefined) table.cells.block({ row: 0, column: 0, rowCount: values.length, columnCount: values[0].length }).assign({ margins: el.cellPadding });
        for (let r = 0; r < values.length; r++) for (let c = 0; c < values[0].length; c++) {
          const cell = table.getCell(r, c);
          cell.fill = r === 0 ? (el.headerFill ?? '#152536') : (el.bodyFill ?? '#F3F6F8');
          cell.text.style = { typeface: spec.fontFamily, fontSize: el.fontSize ?? 26, color: r === 0 ? (el.headerColor ?? '#FFFFFF') : (el.bodyColor ?? '#152536'), bold: r === 0 };
        }
        summary.tables++;
      } else if (el.type === 'image') {
        check(typeof el.path === 'string' && typeof el.alt === 'string', `${label}: local image path and alt required`);
        check(!/^https?:/i.test(el.path), `${label}: stage remote images locally and cite the source`);
        const filename = path.resolve(specDir, el.path);
        const mime = { '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp' }[path.extname(filename).toLowerCase()];
        check(mime, `${label}: supported images are PNG, JPEG and WebP`);
        check(!(el.role === 'evidence' && el.fit === 'cover'), `${label}: evidence must use contain to preserve labels`);
        slide.images.add({ blob: new Uint8Array(await fs.readFile(filename)), contentType: mime, alt: el.alt, fit: el.fit ?? 'contain', position });
        summary.images++;
      } else throw new Error(`${label}: unsupported type ${el.type}`);
    }
    for (const link of page.connectors ?? []) {
      check(diagramNodes.has(link.from) && diagramNodes.has(link.to), `Slide ${index + 1}: connector endpoint not found`);
      check(link.from !== link.to, `Slide ${index + 1}: self connectors are not supported`);
      const sides = ['left','right','top','bottom'];
      check(sides.includes(link.fromSide) && sides.includes(link.toSide), `Slide ${index + 1}: connector sides required`);
      check(['straight','elbow'].includes(link.kind ?? 'straight'), `Slide ${index + 1}: unsupported connector kind`);
      slide.shapes.connect(diagramNodes.get(link.from), diagramNodes.get(link.to), {
        kind: link.kind ?? 'straight', fromSide: link.fromSide, toSide: link.toSide,
        line: { fill: link.color ?? '#334155', width: link.width ?? 2, style: link.style ?? 'solid' },
        head: { type: 'none' },
        tail: { type: link.arrow === false ? 'none' : 'arrow', width: 'med', length: 'med' },
      });
      summary.connectors++;
    }
    if (page.requireEditableText) check(summary.texts > 0, `Slide ${index + 1}: editable text required`);
    if (page.requireNativeChart) check(summary.charts > 0, `Slide ${index + 1}: native chart required`);
    if (page.requireNativeTable) check(summary.tables > 0, `Slide ${index + 1}: native table required`);
    const notes = [page.notes, ...(page.sources ?? []).map(s => `Source: ${s}`)].filter(Boolean).join('\n\n');
    if (notes) slide.speakerNotes.textFrame.setText(notes);
    counts.push(summary);
  }
  return { presentation, PresentationFile, counts, designReport: resolved.report };
}
export async function exportPreviews(presentation, directory) {
  await fs.mkdir(directory, { recursive: true });
  for (let i = 0; i < presentation.slides.items.length; i++) {
    const slide = presentation.slides.items[i];
    const png = await presentation.export({ slide, format: 'png', scale: 1 });
    await fs.writeFile(path.join(directory, `slide_${String(i + 1).padStart(2,'0')}.png`), new Uint8Array(await png.arrayBuffer()));
  }
}
async function main() {
  const args = process.argv.slice(2), opts = {};
  if (args.includes('--help')) { console.log('node build_editable_deck.mjs --spec deck.json --out draft.pptx [--module-root /path/to/node_modules] [--preview-dir previews]'); return; }
  for (let i = 0; i < args.length; i += 2) { check(['--spec','--out','--module-root','--preview-dir'].includes(args[i]) && args[i+1], `Unknown or incomplete argument: ${args[i]}`); opts[args[i]] = args[i+1]; }
  check(opts['--spec'] && opts['--out'], '--spec and --out required');
  const specPath = path.resolve(opts['--spec']), out = path.resolve(opts['--out']);
  try { await fs.access(out); throw new Error(`Output exists: ${out}. Choose a new filename.`); } catch (e) { if (e.code !== 'ENOENT') throw e; }
  const spec = JSON.parse((await fs.readFile(specPath,'utf8')).replace(/^\uFEFF/,''));
  const { presentation, PresentationFile, counts, designReport } = await buildDeck(spec, { specDir: path.dirname(specPath), moduleRoot: opts['--module-root'] });
  await fs.mkdir(path.dirname(out), { recursive:true });
  await (await PresentationFile.exportPptx(presentation)).save(out);
  if (opts['--preview-dir']) await exportPreviews(presentation, path.resolve(opts['--preview-dir']));
  console.log(JSON.stringify({ draft: out, slides: counts, designReport, status:'draft_requires_package_and_visual_QA' }, null, 2));
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main().catch(e => { console.error(e.message); process.exitCode = 1; });
