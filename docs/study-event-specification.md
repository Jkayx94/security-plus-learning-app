# Study Event Specification
Events are append-only and include eventId, schemaVersion, timestamp, learnerId, type, conceptIds, optional unitId and payload. Events cover sessions, introductions, answers, confidence, hints, teaching branches, notes, memory cues, imports and migrations. Progress is a derived cache and can be reconstructed from events.
