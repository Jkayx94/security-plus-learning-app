# Storage and Migration Specification
Local storage key: `security-plus-mastery-state`. Schema 2.0.0 preserves learner ID and matching curriculum IDs. Prototype key `security-plus-prototype-progress-v1` and earlier mastery key are detected and migrated. Unknown IDs are ignored; missing current IDs start unseen. Existing evidence is retained; no evidence is fabricated.
