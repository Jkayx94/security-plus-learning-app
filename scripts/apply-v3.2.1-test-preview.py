from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

boot = r'''async function boot(){
  try {
    try {
      profile = JSON.parse(localStorage.getItem(PROFILE_KEY) || 'null');
    } catch {
      profile = null;
    }

    [curriculum, units] = await Promise.all([
      fetch('./data/sy0-701-curriculum-v1.2.json').then(r => {
        if (!r.ok) throw Error('curriculum');
        return r.json();
      }),
      fetch('./data/sy0-701-learning-units-v1.2.json').then(r => {
        if (!r.ok) throw Error('units');
        return r.json();
      })
    ]);

    contentPack = loadContentPack();
    records = curriculum.records;
    concepts = records.filter((r:any) => r.recordClass === 'assessable_concept');
    acronyms = records.filter((r:any) => r.recordClass === 'acronym');
    assessable = [...concepts, ...acronyms];

    if (concepts.length !== 578 || acronyms.length !== 336 || units.learningUnits.length !== 101) {
      throw Error('Approved data counts failed validation');
    }

    const stored = localStorage.getItem(KEY)
      || localStorage.getItem('security-plus-prototype-progress-v1')
      || localStorage.getItem('security-plus-mastery-state-v1');

    state = ensureV3(migrate(JSON.parse(stored || 'null')));
    view = profile ? 'home' : 'onboarding';
    if (profile) state.learnerId = profile.id;

    if (stored && !localStorage.getItem(KEY)) {
      state.events.push(emit('schema_migrated', [], {from:'prototype-v1', to:'3.0.0'}));
      save();
    }

    render();

    if ('serviceWorker' in navigator) {
      addEventListener('load', () => navigator.serviceWorker.register('./sw.js').then(reg => {
        reg.addEventListener('updatefound', () => {
          const worker = reg.installing;
          if (worker) worker.addEventListener('statechange', () => {
            if (worker.state === 'installed' && navigator.serviceWorker.controller) {
              updateAvailable = true;
              toast('Update available');
            }
          });
        });
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          notify('Update completed', `Updated to v${APP_VERSION}`, 'update', 4000);
        });
      }).catch(console.error));
    }
  } catch (err) {
    app.innerHTML = `<main class="shell"><section class="card error"><h1>Learning data could not load</h1><p>${esc(err)}</p><p>Check that the curriculum and learning-unit JSON files were deployed.</p></section></main>`;
  }
}
boot();'''

source, count = re.subn(
    r"async function boot\(\)\{.*?\nboot\(\);",
    boot,
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("Could not locate exactly one boot function to replace")

source = source.replace(
    "if(t.dataset.testScreen==='session'){try{start(2,'adaptive',true)}",
    "if(t.dataset.testScreen==='session'){try{start(.5,'adaptive',true)}",
)

path.write_text(source, encoding="utf-8")
