---
name: frontend-design
description: Create distinctive, production-grade frontend UI with high design quality (web pages, landing pages, dashboards, marketing artifacts, app shells, and reusable components). Use when the user asks to design, redesign, style, or beautify any web UI (HTML/CSS, React/Vue, Tailwind, design systems) and needs polished, accessible, responsive code that avoids generic “AI slop” aesthetics. Do not use for backend-only tasks or non-UI requests.
---

Create distinctive, production-grade frontend interfaces that feel intentionally designed (not generic). Implement real working code with meticulous attention to typography, color, layout, motion, and micro-details.

## Workflow

1. Clarify context:
   - Purpose, audience, and content
   - Technical constraints (framework, build setup, performance, a11y, browser support)
   - Any brand guidelines (fonts, colors, tone, existing components)
2. Commit to a bold aesthetic direction:
   - Pick a clear tone (e.g., brutalist, editorial, luxury, playful, retro-futuristic, organic, industrial).
   - Define the “one memorable thing” (motif, layout idea, interaction, texture, type treatment).
   - Choose a palette and type pairing that fits the tone.
3. Implement working frontend code:
   - Match the user’s stack (HTML/CSS/JS, React, Vue, etc.).
   - Make it responsive, accessible, and production-grade.
   - Include concise usage/run instructions when needed.

## Aesthetic Checklist

- Typography:
  - Choose distinctive fonts; avoid defaulting to Inter/Roboto/Arial/system fonts.
  - Pair a characterful display face with a refined body face.
  - Use a consistent type scale; tune letter-spacing, line-height, and weights.
- Color & theme:
  - Commit to a cohesive palette; use CSS variables/tokens for consistency.
  - Prefer dominant surfaces + sharp accents over timid “evenly-distributed” colors.
- Motion:
  - Add a small number of high-impact moments (page-load orchestration, hover states, scroll reveals).
  - Prefer CSS-only solutions when possible; use a motion library only when it meaningfully helps.
- Spatial composition:
  - Avoid cookie-cutter layouts; use asymmetry, overlap, grid breaks, and intentional whitespace.
  - Use consistent spacing tokens and alignment rules.
- Backgrounds & micro-details:
  - Add atmosphere (gradient meshes, noise/grain, subtle patterns, layered transparencies).
  - Use shadows, borders, and textures that match the concept (not generic defaults).

## Anti-Patterns

- Avoid generic AI aesthetics: purple gradients on white, predictable component patterns, timid palettes, and “template vibes.”
- Avoid converging on the same trendy choices across generations; vary tone, palette, typography, and composition based on context.

## Attribution

Adapted from `anthropics/skills` `frontend-design` (Apache-2.0). Modified in this repo to fit local SkillOps conventions.
