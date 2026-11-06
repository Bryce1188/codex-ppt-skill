#!/usr/bin/env node
/** Resolve reusable design defaults and reject unexplained drift. No slide runtime needed. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { isDeepStrictEqual } from 'node:util';
import { pathToFileURL } from 'node:url';

function check(ok, message) { if (!ok) throw new Error(message); }
const justified = value => typeof value === 'string' && value.trim().length > 0;

export function applyDesignProfile(input, profile) {
  check(profile?.schemaVersion === 1 && justified(profile.id) && justified(profile.version), 'Design profile: schemaVersion 1, id and version required');
  check(justified(profile.fontFamily) && profile.slideSize?.width > 0 && profile.slideSize?.height > 0, 'Design profile: font and slideSize required');
  check(profile.backgrounds?.content && profile.textStyles?.title && profile.textStyles?.body, 'Design profile: content background, title and body styles required');
  const spec = structuredClone(input), exceptions = [];
  function merge(base, item, label) {
    const changes = Object.keys(base).filter(key => Object.hasOwn(item, key) && !isDeepStrictEqual(item[key], base[key]));
    if (changes.length) {
      check(justified(item.designException), label + ': design drift in ' + changes.join(', ') + '; give a designException or change the shared profile');
      exceptions.push({ location: label, fields: changes, reason: item.designException });
    }
    return { ...structuredClone(base), ...item };
  }
  if (spec.fontFamily !== undefined) check(spec.fontFamily === profile.fontFamily, 'Design profile: fontFamily differs from shared profile');
  if (spec.slideSize !== undefined) check(isDeepStrictEqual(spec.slideSize, profile.slideSize), 'Design profile: slideSize differs from shared profile');
  spec.fontFamily = profile.fontFamily;
  spec.slideSize = structuredClone(profile.slideSize);
  check(Array.isArray(spec.slides) && spec.slides.length, 'Design profile: slides required');
  for (const [index, page] of spec.slides.entries()) {
    const label = 'Slide ' + (index + 1);
    const role = page.backgroundRole ?? 'content';
    check(Object.hasOwn(profile.backgrounds, role), label + ': unknown backgroundRole ' + role);
    if (role !== 'content') check(page.kind === 'cover' || page.kind === 'section', label + ': alternate background requires cover or section kind');
    const merged = merge({ background: profile.backgrounds[role] }, page, label);
    page.background = merged.background;
    let titleCount = 0;
    page.elements = (page.elements ?? []).map((element, ei) => {
      const elLabel = label + ', element ' + (ei + 1);
      let base;
      if (element.type === 'text' || element.type === 'shape') {
        const styles = element.type === 'text' ? profile.textStyles : profile.shapeStyles;
        check(element.styleRole && Object.hasOwn(styles ?? {}, element.styleRole), elLabel + ': known styleRole required');
        base = styles[element.styleRole];
        if (element.type === 'text' && element.styleRole === 'title') titleCount++;
        for (const [key, value] of Object.entries(element.textStyle ?? {})) {
          const expected = key === 'typeface' ? profile.fontFamily : base[key];
          if (expected !== undefined && !isDeepStrictEqual(value, expected)) {
            check(justified(element.designException), elLabel + ': textStyle bypasses shared ' + key);
            exceptions.push({ location: elLabel, fields: ['textStyle.' + key], reason: element.designException });
          }
        }
      } else if (element.type === 'table') base = profile.tableStyle ?? {};
      else if (element.type === 'chart') {
        base = profile.chartStyle ?? {};
        const data = spec.data?.[element.dataKey];
        if (data?.series && profile.chartPalette?.length) data.series = data.series.map((series, si) => merge(
          { fill: profile.chartPalette[si % profile.chartPalette.length] },
          series, elLabel + ', series ' + (si + 1)
        ));
      }
      else if (element.type === 'image') base = { fit: 'contain' };
      else base = {};
      return merge(base, element, elLabel);
    });
    check(titleCount === 1, label + ': exactly one title styleRole required');
    page.connectors = (page.connectors ?? []).map((link, li) => merge(profile.connectorStyle ?? {}, link, label + ', connector ' + (li + 1)));
  }
  return { spec, report: { passed: true, profileId: profile.id, profileVersion: profile.version, slideCount: spec.slides.length, exceptions, scope: 'Authored design defaults and declared exceptions only; final rendering and visual review still required.' } };
}

export async function resolveDesignProfile(spec, specDir = '.') {
  if (!spec?.designProfile) return { spec, report: null };
  const profile = typeof spec.designProfile === 'string'
    ? JSON.parse((await fs.readFile(path.resolve(specDir, spec.designProfile), 'utf8')).replace(/^\uFEFF/, ''))
    : spec.designProfile;
  return applyDesignProfile(spec, profile);
}

async function main() {
  const args = process.argv.slice(2), specArg = args.indexOf('--spec'), reportArg = args.indexOf('--report');
  check(specArg >= 0 && args[specArg + 1], 'Usage: node design_profile.mjs --spec deck.json [--report report.json]');
  const filename = path.resolve(args[specArg + 1]);
  const input = JSON.parse((await fs.readFile(filename, 'utf8')).replace(/^\uFEFF/, ''));
  check(input.designProfile, 'No designProfile specified; this check cannot assert a shared visual system');
  const { report } = await resolveDesignProfile(input, path.dirname(filename));
  if (reportArg >= 0) {
    check(args[reportArg + 1], '--report requires a path');
    await fs.writeFile(path.resolve(args[reportArg + 1]), JSON.stringify(report, null, 2));
  }
  console.log(JSON.stringify(report, null, 2));
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main().catch(error => { console.error(error.message); process.exitCode = 1; });
