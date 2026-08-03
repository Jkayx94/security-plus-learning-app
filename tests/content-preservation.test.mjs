import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => JSON.parse(fs.readFileSync(path, 'utf8'));

const curriculum = read('src/data/sy0-701-curriculum-v1.2.json');
const units = read('src/data/sy0-701-learning-units-v1.2.json');
const lessons = read('src/data/prototype-lessons-unit-1.1.json');
const questions = read('src/data/prototype-question-bank-unit-1.1.json');

const records = curriculum.records ?? [];
const assessable = records.filter(record => record.recordClass === 'assessable_concept');
const acronyms = records.filter(record => record.recordClass === 'acronym');
const recordIds = records.map(record => record.conceptId);
const recordIdSet = new Set(recordIds);

test('approved curriculum inventory is preserved', () => {
  assert.equal(assessable.length, 578, 'The approved assessable-concept inventory changed');
  assert.equal(acronyms.length, 336, 'The approved acronym inventory changed');
  assert.equal(units.learningUnits?.length, 101, 'The approved learning-unit inventory changed');
  assert.equal(recordIdSet.size, recordIds.length, 'Duplicate curriculum concept IDs were introduced');
});

test('every learning-unit mapping resolves to the approved curriculum', () => {
  const unitIds = new Set();
  const mappedAssessable = new Set();

  for (const unit of units.learningUnits ?? []) {
    assert.ok(unit.unitId, 'A learning unit has no unitId');
    assert.ok(!unitIds.has(unit.unitId), `Duplicate learning-unit ID: ${unit.unitId}`);
    unitIds.add(unit.unitId);

    assert.ok(Array.isArray(unit.conceptIds) && unit.conceptIds.length > 0, `${unit.unitId} has no concepts`);

    for (const conceptId of unit.conceptIds) {
      assert.ok(recordIdSet.has(conceptId), `${unit.unitId} maps missing concept ${conceptId}`);
      mappedAssessable.add(conceptId);
    }

    for (const mapping of unit.acronymMappings ?? []) {
      assert.ok(recordIdSet.has(mapping.acronymId), `${unit.unitId} maps missing acronym ${mapping.acronymId}`);
    }
  }

  for (const concept of assessable) {
    assert.ok(mappedAssessable.has(concept.conceptId), `Assessable concept is no longer mapped: ${concept.conceptId}`);
  }
});

test('approved prototype lesson and question material is retained', () => {
  assert.equal(lessons.lessons?.length, 2, 'The two approved Unit 1.1 lessons were not retained');
  assert.equal(questions.questions?.length, 30, 'The 30 approved Unit 1.1 questions were not retained');

  const lessonUnits = new Set((lessons.lessons ?? []).map(lesson => lesson.unitId));
  assert.deepEqual([...lessonUnits].sort(), ['UNIT-1.1-01', 'UNIT-1.1-02']);

  for (const question of questions.questions ?? []) {
    assert.ok(question.questionId, 'A prototype question has no questionId');
    assert.ok(Array.isArray(question.answerOptions), `${question.questionId} has no answer options`);
    assert.ok(question.answerOptions.includes(question.correctAnswer), `${question.questionId} has an invalid correct-answer mapping`);

    for (const conceptId of question.conceptIds ?? []) {
      assert.ok(recordIdSet.has(conceptId), `${question.questionId} maps missing concept ${conceptId}`);
    }
  }
});
