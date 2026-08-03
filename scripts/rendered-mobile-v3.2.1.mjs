import {chromium} from 'playwright';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';

const origin='http://127.0.0.1:4173';
const profile=JSON.stringify({id:'QA-LOCAL',name:'QA Learner',examDate:null,createdAt:new Date().toISOString()});
const server=spawn(process.execPath,['scripts/serve-dist.mjs'],{stdio:'inherit'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function waitForServer(timeoutMs=15000){
 const deadline=Date.now()+timeoutMs;
 while(Date.now()<deadline){
  try{const response=await fetch(origin,{cache:'no-store'});if(response.ok)return}
  catch{}
  await sleep(150);
 }
 throw new Error('Timed out waiting for the dist server');
}

try{
 await waitForServer();
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({
  viewport:{width:360,height:800},
  isMobile:true,
  hasTouch:true,
  reducedMotion:'reduce',
  storageState:{cookies:[],origins:[{origin,localStorage:[{name:'security-plus-learner-profile',value:profile}]}]}
 });
 const page=await context.newPage();
 const browserErrors=[];
 page.on('pageerror',error=>browserErrors.push(String(error)));
 page.on('console',message=>{if(message.type()==='error')browserErrors.push(message.text())});
 await page.goto(`${origin}/`,{waitUntil:'networkidle'});
 await page.getByRole('heading',{name:/Welcome back, QA Learner\./}).waitFor({state:'visible',timeout:15000});
 assert.deepEqual(browserErrors,[],`Browser errors during startup: ${browserErrors.join(' | ')}`);

 const moreControl=page.locator('nav [data-nav="more"]');
 await moreControl.waitFor({state:'visible'});
 await moreControl.click();
 await page.getByRole('heading',{name:'More'}).waitFor();
 await page.getByRole('button',{name:/About and version/}).click();
 await page.getByText('Tap the version five times to enable local testing tools.').waitFor();
 const version=page.getByRole('button',{name:/Version 3\.2\.1/});
 for(let i=0;i<4;i++)await version.tap();
 await assert.rejects(()=>page.locator('#test-code').waitFor({timeout:250}));
 await version.tap();
 await page.locator('#test-code').waitFor();
 await page.locator('#test-code').fill('wrong');
 await page.getByRole('button',{name:'Enable Test Mode'}).click();
 assert.equal(await page.getByText('TEST MODE',{exact:true}).count(),0);
 await page.locator('#test-code').fill('JAKE-SECPLUS-TEST');
 await page.getByRole('button',{name:'Enable Test Mode'}).click();
 await page.getByRole('heading',{name:'Developer Lab'}).waitFor();
 await page.getByText('TEST MODE',{exact:true}).first().waitFor();
 await page.getByRole('button',{name:'UNLOCK EVERYTHING FOR TESTING'}).click();
 await page.getByText(/Test coins:\s*Unlimited/).waitFor();
 await page.getByRole('button',{name:'Multiple queued notifications'}).click();
 assert.equal(await page.locator('.appNotification').count(),1);
 await page.locator('.appNotification button[aria-label="Close notification"]').click();
 assert.equal(await page.locator('.appNotification').count(),1);
 await page.waitForTimeout(3700);
 assert.ok((await page.locator('.appNotification').count())<=1);

 await page.getByRole('button',{name:'Start reviewed question'}).click();
 await page.getByRole('button',{name:'Report question'}).click();
 await page.getByRole('button',{name:'Save report'}).click();
 await page.locator('.appNotification').waitFor();
 await page.locator('.answers button').first().click();
 const submit=page.getByRole('button',{name:'Submit answer'});
 assert.equal(await submit.isEnabled(),true);
 await submit.click();
 await page.getByRole('button',{name:'Fairly sure'}).click();
 await page.locator('.appNotification').waitFor();
 const continueButton=page.getByRole('button',{name:'Continue'});
 assert.equal(await continueButton.isEnabled(),true);
 await continueButton.click();

 await page.locator('nav [data-nav="more"]').click();
 await page.getByRole('button',{name:/Developer Lab/}).waitFor();
 await page.getByRole('button',{name:/Cosmetics/}).click();
 await page.getByText('TEST PREVIEW',{exact:true}).waitFor();
 await page.getByRole('button',{name:/Equip|Unlock/}).first().click();
 await page.getByText(/Test cosmetic equipped/).waitFor();
 await page.locator('nav [data-nav="more"]').click();
 await page.getByRole('button',{name:/Developer Lab/}).click();
 await page.getByRole('button',{name:'Any Unit Boss'}).click();
 await page.getByText(/Boss battle/).waitFor();
 const bodyWidth=await page.evaluate(()=>document.body.scrollWidth);
 const viewportWidth=await page.evaluate(()=>document.documentElement.clientWidth);
 assert.ok(bodyWidth<=viewportWidth,'horizontal scrolling detected');
 await page.getByText('TEST MODE',{exact:true}).first().click();
 await page.getByRole('button',{name:'Exit Test Mode'}).click();
 await page.getByRole('heading',{name:'About'}).waitFor();
 assert.equal(await page.getByText('TEST MODE',{exact:true}).count(),0);
 await context.close();
 await browser.close();
 console.log('RENDERED MOBILE AUDIT PASSED: startup, More, Test Mode, notifications, Submit and Continue verified.');
} finally {
 server.kill('SIGTERM');
}
