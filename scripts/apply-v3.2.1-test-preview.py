from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

# Repair the malformed boundary left by the earlier migration script.
# The explicit leading semicolon makes the destructuring assignment a new statement.
source = source.replace(
    "catch{profile=null}[curriculum,units]=await Promise.all(",
    "catch{profile=null;}\n;[curriculum,units]=await Promise.all(",
)
source = source.replace(
    "catch{profile=null;}[curriculum,units]=await Promise.all(",
    "catch{profile=null;}\n;[curriculum,units]=await Promise.all(",
)

# Existing learners must start on Home so the persistent navigation is rendered.
source = source.replace(
    "if(!profile){view='onboarding'}else{state.learnerId=profile.id}",
    "view=profile?'home':'onboarding';if(profile)state.learnerId=profile.id",
)

# Developer Lab reviewed-question preview must be a single activity.
source = source.replace(
    "if(t.dataset.testScreen==='session'){try{start(2,'adaptive',true)}",
    "if(t.dataset.testScreen==='session'){try{start(.5,'adaptive',true)}",
)

path.write_text(source, encoding="utf-8")
