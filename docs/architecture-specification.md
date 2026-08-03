# Architecture Specification
Single-page TypeScript PWA. Layers: immutable curriculum JSON; learning-unit catalogue; adaptive activity generator; append-only study-event log; derived progress; local persistence; UI routes; service worker. Cloud sync can later replicate events without replacing the learner model.

Routes: Home, Learn, Unit lesson, Adaptive session, Feedback, Acronym trainer, Exam mode, Readiness dashboard, Memory bank, Data/backup.

Components are rendered as mobile-first views with touch targets, fixed bottom navigation, readable errors, and no horizontal layout dependency.
