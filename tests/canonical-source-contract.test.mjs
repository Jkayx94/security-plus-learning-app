import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const workflow = fs.readFileSync('.github/workflows/deploy-pages.yml', 'utf8');
const app = fs.readFileSync('src/app.ts', 'utf8');
const styles = fs.readFileSync('src/styles.css', 'utf8');

test('CI builds canonical source without repair scripts or generated commits', () => {
  assert.doesNotMatch(workflow, /apply-v3\.2\.1|source fixes|python3 scripts\/apply-/i);
  assert.doesNotMatch(workflow, /git commit -m "Apply Test Mode boss, cosmetic and theme corrections"/);
  assert.match(workflow, /git diff --exit-code -- .*src/);
  assert.match(workflow, /git diff --exit-code -- .*tests/);
  assert.match(workflow, /git diff --exit-code -- .*scripts/);
});

test('course storage and content loaders remain stable', () => {
  assert.match(app, /KEY='security-plus-mastery-state'/);
  assert.match(app, /loadContentPack/);
  assert.match(app, /sy0-701-curriculum-v1\.2\.json/);
  assert.match(app, /sy0-701-learning-units-v1\.2\.json/);
});

test('every catalogue theme has an explicit rendered selector', () => {
  for (const theme of ['theme-blue', 'theme-purple', 'theme-green', 'theme-oled']) {
    assert.match(app, new RegExp(`['\"]${theme}['\"]`), `${theme} must remain in the catalogue`);
    assert.ok(styles.includes(`data-theme="${theme}"`), `${theme} must have explicit CSS`);
  }
});

test('boss and Test Mode regression contracts remain present', () => {
  assert.match(app, /bossCorrect/);
  assert.match(app, /FINISH MODE ARMED/);
  assert.match(app, /FINAL STRIKE CONFIRMED/);
  assert.match(app, /Test cosmetic equipped/);
  assert.match(app, /testOnly/);
});
