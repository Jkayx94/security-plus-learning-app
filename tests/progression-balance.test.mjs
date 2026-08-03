import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {bossResult,answerReward,shieldTier,resetTestMode,reducedMotionCss} from '../scripts/progression-rules.mjs';

test('one boss question cannot defeat a boss',()=>{const r=bossResult('unit',1,1,false);assert.equal(r.complete,false);assert.equal(r.passed,false);assert.equal(r.reward,0)});
test('rewards issue only after full battle and pass threshold',()=>{assert.equal(bossResult('unit',5,6,false).reward,0);assert.equal(bossResult('unit',5,7,false).reward,15)});
test('boss rewards cannot be claimed twice',()=>{assert.equal(bossResult('domain',10,12,false).reward,85);assert.equal(bossResult('domain',10,12,true).reward,0)});
test('high tier shields require substantial evidence',()=>{assert.equal(shieldTier({understood:5,retained:0,bosses:0,domainBosses:0,firstAttemptAccuracy:100,examReady:0,finalBoss:false}),'Basic');assert.equal(shieldTier({understood:100,retained:40,bosses:3,domainBosses:0,firstAttemptAccuracy:75,examReady:0,finalBoss:false}),'Gold');assert.equal(shieldTier({understood:500,retained:350,bosses:10,domainBosses:3,firstAttemptAccuracy:80,examReady:499,finalBoss:true}),'Diamond')});
test('test mode does not change real rewards or mastery inputs',()=>{const r=answerReward({correct:true,firstAttempt:true,confident:true,previousStage:'introduced',newStage:'understood',testOnly:true});assert.deepEqual(r,{xp:0,coins:0,testCoins:1})});
test('test reset removes only test coins and unlocks',()=>{const real={xp:100,coins:12,mastery:55};const out=resetTestMode(real,{enabled:true,coins:999,unlockedCosmetics:['all']});assert.deepEqual(out.real,real);assert.equal(out.test.coins,0);assert.deepEqual(out.test.unlockedCosmetics,[])});
test('reduced-motion mode removes nonessential animations',()=>{const css=fs.readFileSync(new URL('../src/styles.css',import.meta.url),'utf8');assert.equal(reducedMotionCss(css),true)});
test('coin rewards are idempotent after replay',()=>{const first=answerReward({correct:true,firstAttempt:true,confident:true,previousStage:'introduced',newStage:'understood',alreadyRewarded:false});const replay=answerReward({correct:true,firstAttempt:true,confident:true,previousStage:'introduced',newStage:'understood',alreadyRewarded:true});assert.equal(first.coins,2);assert.equal(replay.coins,0)});
