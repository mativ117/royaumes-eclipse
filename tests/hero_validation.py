"""Untrusted hero IDs must not resolve inherited properties or model-cache entries.

Runs the production validators and loader boundary in Node, without a browser,
WebGL, model downloads or rewriting release assets.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const root = process.argv[1];
const context = {
 localStorage: { getItem() { return null; }, setItem() {} },
 ROYAUMES_VERSION: 'audit', ROYAUMES_CHARACTER_DATA: {},
 fetchCalls: [],
 async fetch(url) { context.fetchCalls.push(url); return { ok: false }; },
 atob() { throw Error('An inherited embedded model must never be decoded'); },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(root + '/src/roster.js', 'utf8'), context);
const avatar = fs.readFileSync(root + '/src/authored-avatar.js', 'utf8');
vm.runInContext(avatar.slice(0, avatar.indexOf('async function prepareHeroSelection')), context);
const expedition = fs.readFileSync(root + '/src/expedition.js', 'utf8');
vm.runInContext(expedition.slice(expedition.indexOf('function readRun('), expedition.indexOf('async function continueRun(')), context);
context.RUN_KEY = 'audit-run';
context.baseWorld = { onGround: () => true };
context.ENCOUNTERS = [{ id: 'keeper' }];
context.LAMPS = ['ash', 'night', 'dawn'].map(id => ({ id }));
context.VALVES = ['a', 'b', 'c'].map(id => ({ id }));
const run = source => vm.runInContext(source, context);

function profile(hero) {
 return { version: 1, name: 'Voyageur', secret: [false, false, false], completed: [],
  journey: { level: 2, hero, boon: 'vigor', checkpoint: 1 } };
}
function refuge(hero) {
 return { version: '0.9', hero, boon: 'vigor', snapshot: {
  x: 0, z: 0, keys: [], completed: [], dead: [], trials: {
   escort: { waypoint: 0, done: false, x: 0, z: 0 },
   bells: { order: ['ash', 'night', 'dawn'], step: 0, done: false },
   forge: { valves: [] }, ritual: [],
  },
 } };
}

(async () => {
 const ids = run('Object.keys(HERO_DEFS)');
 assert.strictEqual(ids.length, 11);
 assert.strictEqual(run('Object.getPrototypeOf(avatarRuntime.heroes)'), null);
 assert.strictEqual(run('Object.getPrototypeOf(heroLoads)'), null);
 for (const hero of ids) {
  context.candidate = hero; context.profileCandidate = profile(hero);
  context.refugeCandidate = JSON.stringify(refuge(hero));
  assert.strictEqual(run('isHeroId(candidate)'), true);
  assert.strictEqual(run('validateProfile(profileCandidate).journey.hero'), hero);
  assert.strictEqual(run('readRun(refugeCandidate).hero'), hero);
  run('avatarRuntime.heroes[candidate]={id:candidate}');
  const cached = await run('ensureHeroModel(candidate)');
  assert.strictEqual(cached.id, hero);
 }
 assert.strictEqual(context.fetchCalls.length, 0);

 const invalid = ['constructor', '__proto__', 'toString', 'hasOwnProperty',
  'valueOf', '__defineGetter__', '../../secret', '', null, 42, {}, []];
 for (const hero of invalid) {
  context.candidate = hero; context.profileCandidate = profile(hero);
  context.refugeCandidate = JSON.stringify(refuge(hero));
  assert.strictEqual(run('isHeroId(candidate)'), false);
  assert.strictEqual(run('isMeleeHero(candidate)'), false);
  assert.strictEqual(run('isRifleHero(candidate)'), false);
  assert.strictEqual(run('validateProfile(profileCandidate).journey'), null);
  assert.strictEqual(run('readRun(refugeCandidate)'), null);
  await assert.rejects(run('ensureHeroModel(candidate)'), /Héros inconnu/);
 }
 assert.strictEqual(context.fetchCalls.length, 0, 'Invalid IDs must fail before fetching');

 // Byte limits alone do not prevent deeply nested valid JSON from breaking
 // a later snapshot clone. Production validators reject it without recursion.
 const deepProfile = profile('rempart'); let level = deepProfile;
 for (let i = 0; i < 40; i++) { level.extra = {}; level = level.extra; }
 context.profileCandidate = deepProfile;
 assert.throws(() => run('validateProfile(profileCandidate)'), /Sauvegarde incompatible/);
 const deepRefuge = refuge('rempart'); level = deepRefuge.snapshot.trials.forge;
 for (let i = 0; i < 40; i++) { level.extra = {}; level = level.extra; }
 context.refugeCandidate = JSON.stringify(deepRefuge);
 assert.strictEqual(run('readRun(refugeCandidate)'), null);
 context.profileCandidate = { ...profile('rempart'), extra: Array(9000).fill(0) };
 assert.throws(() => run('validateProfile(profileCandidate)'), /Sauvegarde incompatible/);

 // Forging an own model-cache entry does not make a non-roster ID legitimate.
 run('avatarRuntime.heroes.constructor={id:"forged"}');
 context.candidate = 'constructor';
 await assert.rejects(run('ensureHeroModel(candidate)'), /Héros inconnu/);

 // Even if an upstream caller changed a dictionary prototype, the loader must
 // ignore inherited avatar/promise/embedded-model entries for a valid hero ID.
 run('delete avatarRuntime.heroes.rempart;Object.setPrototypeOf(avatarRuntime.heroes,{rempart:{id:"inherited"}});Object.setPrototypeOf(heroLoads,{rempart:Promise.resolve({id:"inherited-promise"})})');
 context.ROYAUMES_CHARACTER_DATA = Object.create({ rempart: 'not-a-model' });
 await assert.rejects(run('ensureHeroModel("rempart")'), /Modèle indisponible/);
 assert.strictEqual(context.fetchCalls.length, 1);
 assert.strictEqual(context.fetchCalls[0], './assets/characters/rempart.glb?v=audit');
 assert.strictEqual(run('Object.hasOwn(heroLoads,"rempart")'), false,
  'Rejected loads must not leave an owned poisoned cache entry');
 console.log('PASS: eleven real roster IDs including the secret preserved; inherited, unknown and non-string IDs rejected by profile/refuge/loader boundaries; caches have null prototypes and ignore inherited entries; invalid IDs never fetch; deep or excessive save graphs rejected within bounded work. CPU-only.');
})().catch(error => { console.error(error); process.exitCode = 1; });
"""

subprocess.run(['node', '-e', PROGRAM, str(ROOT)], check=True, cwd=ROOT)
