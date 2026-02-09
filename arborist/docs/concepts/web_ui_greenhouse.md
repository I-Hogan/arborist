# Web UI Greenhouse Refresh Plan

This document captures the plan for refreshing the Arborist web UI to match the
requested ChatGPT-like layout while keeping the implementation lightweight.

## Goals
- Present a slim right-side projects bar with an outlined active project.
- Replace the save state panel with a single save state button.
- Update copy to "Arborist Greenhouse".
- Maintain a clean, modern layout and keep the UI responsive.

## Approach
1. Update `web_ui/src/pages/index.astro` to establish a two-column layout: main content on
   the left and a slim projects sidebar on the right. Move the save state button
   into the header region so it is no longer its own panel.
2. Refresh `web_ui/public/styles.css` with a neutral, ChatGPT-like palette, new
   typography, and simplified project list styling. Active projects should be
   indicated by a clear outline.
3. Adjust `web_ui/public/app.js` to remove the active project toggle control. Set the
   active project via list item interaction and update busy-state disabling for
   the new controls.
4. Verify responsive behavior at narrow widths and keep the animation/styling
   lightweight.
