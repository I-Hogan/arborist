# Feedback UI Workflow Plan

This note outlines the intended feedback workflow for the Arborist web UI so the
UI, API, and file updates stay aligned with the project goals in `SEED.md`.

## Goals
- Allow users to submit feedback to the active project without editing files.
- Keep queued feedback visible and editable (clear or follow-up).
- Surface recent response summaries so users can track what Arborist did.

## Data Sources
- `arborist/feedback.md` holds queued feedback items for a project.
- `arborist/work_log.md` provides response summaries after work completes.

## API Plan
- `GET /api/feedback`: return active project info, queued feedback items, and
  recent response entries from the work log.
- `POST /api/feedback`: append a feedback item for the active project.
- `POST /api/feedback/clear`: clear queued feedback for the active project.
- `POST /api/feedback/follow-up`: append a follow-up feedback item that references
  a selected response entry.

## UI Plan
- Show active project name and queue status in the Feedback panel.
- Allow drafting feedback, submitting it, clearing the queue, and initiating a
  follow-up from a response entry.
- Display recent response summaries with timestamps and a follow-up action.
- Disable actions when no active project is selected or a request is in flight.
