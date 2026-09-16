---
version: alpha
name: TaxEaseLK
description: >-
  Visual foundation for TaxEaseLK — a clean, soft, information-dense finance SaaS
  with one confident blue brand accent and a disciplined five-colour status system.
omitted:
  - Layout & Spacing   # TODO — spacing scale, grid & alignment not yet documented
  - Responsiveness     # TODO — breakpoints & responsive rules not yet documented

colors:
  # Brand — tailwind.config.ts (sampled from Figma)
  brand-navy: "#161950"        # dark hero/auth panel, logo wordmark, emphasis numbers
  brand-blue: "#155DFC"        # primary accent: buttons, active nav, links, focus ring
  brand-blue-dark: "#1E3FAE"   # primary-button hover
  brand-bg: "#EBF9FF"          # app content background
  surface: "#FFFFFF"           # card / panel / body background
  # Neutrals — Tailwind gray scale, used verbatim
  text-strong: "#111827"       # gray-900 — headings & values
  text: "#374151"              # gray-700 — body & labels
  text-muted: "#6B7280"        # gray-500 — secondary / hints
  text-faint: "#9CA3AF"        # gray-400 — meta / micro-labels
  border: "#F3F4F6"            # gray-100 — hairline panel borders
  border-strong: "#D1D5DB"     # gray-300 — input borders
  # Status — saturated foreground + soft tint, one pair per meaning
  success: "#16A34A"
  success-bg: "#DCFCE7"
  warning: "#D97706"
  warning-bg: "#FEF3C7"
  critical: "#DC2626"
  critical-bg: "#FEE2E2"
  info: "#2563EB"
  info-bg: "#DBEAFE"
  pending: "#7C3AED"
  pending-bg: "#EDE9FE"

typography:
  # No web font — Tailwind default system-ui sans stack, antialiased.
  display:  { fontFamily: system-ui, fontSize: 1.875rem, fontWeight: 800 }              # text-3xl — hero / loading
  h1:       { fontFamily: system-ui, fontSize: 1.5rem,   fontWeight: 700 }              # text-2xl — stat / metric values
  h2:       { fontFamily: system-ui, fontSize: 1rem,     fontWeight: 700 }              # text-base — modal / section titles
  body:     { fontFamily: system-ui, fontSize: 0.875rem, fontWeight: 400 }              # text-sm — dominant body size
  label:    { fontFamily: system-ui, fontSize: 0.875rem, fontWeight: 500 }              # text-sm — field labels
  caption:  { fontFamily: system-ui, fontSize: 0.75rem,  fontWeight: 400 }              # text-xs — hints, badges
  overline: { fontFamily: system-ui, fontSize: 0.6875rem, fontWeight: 600, letterSpacing: 0.05em }  # text-[11px] uppercase micro-labels
  mono:     { fontFamily: ui-monospace, fontSize: 0.75rem }                             # reference codes (REQ-…)

rounded:
  control: 8px     # rounded-lg — buttons, inputs, selects
  card: 12px       # rounded-card — panels, modals
  pill: 9999px     # rounded-full — badges, progress bars

components:
  button-primary:   { backgroundColor: "{colors.brand-blue}", textColor: "{colors.surface}", rounded: "{rounded.control}", typography: "{typography.label}" }
  button-secondary: { backgroundColor: "{colors.surface}", textColor: "{colors.text}", rounded: "{rounded.control}" }
  card:             { backgroundColor: "{colors.surface}", rounded: "{rounded.card}" }
  input:            { backgroundColor: "{colors.surface}", textColor: "{colors.text-strong}", rounded: "{rounded.control}" }
  badge:            { rounded: "{rounded.pill}", typography: "{typography.caption}" }
  toast:            { rounded: "{rounded.control}" }
---

## Overview

TaxEaseLK is a clean, soft, information-dense finance SaaS. The palette is gray-dominant
neutrals under a single confident blue brand accent (`brand-blue`), with a restrained
five-colour semantic status system. Everything is softly rounded, bordered with hairline
grays, and lifted by a barely-there shadow — flat and professional, never heavy.

## Colors

- **Brand blue `#155DFC`** carries every primary action: buttons, active nav, links,
  focus rings. Hover deepens to `brand-blue-dark`. **Navy `#161950`** anchors the
  hero/auth panel and logo wordmark. **`brand-bg` `#EBF9FF`** tints the app content area;
  panels sit on white `surface`.
- **Neutrals** are the Tailwind gray scale: `text-strong` for headings/values down to
  `text-faint` for meta, with `border`/`border-strong` hairlines.
- **Status** uses one `{colour}` + `{colour}-bg` pair per meaning: success (green),
  warning (amber), critical (red), info (blue), pending (violet). Pills render as a soft
  `-bg` tint with the saturated foreground as text.
- Signature move: **soft tinted surfaces** (`success-bg`, `warning-bg`, `info-bg`, …) for
  gentle status chips; saturated fills are reserved for solid buttons and progress bars.
- _Known drift (cleanup TODO):_ status **pills** use these `status.*` tokens, but some
  inline text, bars, icon chips and toasts reach for Tailwind's stock `emerald`/`amber`/
  `red`/`blue-50` families for the same meanings. Consolidate onto the tokens above.

## Typography

No web font is loaded — the app renders in the system-ui sans stack, `antialiased`. Type
runs small and dense: `body`/`caption` (text-sm/xs) dominate, with `bold`/`extrabold`
reserved for numbers and titles. Uppercase `overline` micro-labels and `mono` reference
codes add finance-app texture. Base body text colour is a deep indigo `#2323a1` (globals.css),
though components usually override to the gray `text-*` tokens.

## Elevation & Depth

Deliberately minimal. Panels use `shadow-card` (`0 1px 2px rgba(16,24,40,0.05)`) — almost
flat. Only floating toasts lift higher (`shadow-lg`). Modals dim the page with a `black/50`
scrim behind a white `rounded-card` panel.

## Components

- **Button** — `rounded-control`, `text-sm font-semibold`. Primary = solid `brand-blue`
  (hover `brand-blue-dark`); secondary = white with a `border-strong` outline; plus
  success/danger (solid status) and ghost variants.
- **Card** — white, `rounded-card`, hairline `border`, soft `shadow-card`.
- **Input / Select** — white, `rounded-control`, `border-strong`; focus = 1px `brand-blue`
  ring + brand-blue border (the app-wide focus convention).
- **Badge** — fully-rounded pill, `caption` type, tone-driven `-bg` tint + foreground.
- **Toast** — tinted bordered card (success green / error red), `shadow-lg`, lucide icon.
- **Icons** — lucide-react throughout; default `h-4 w-4`, `h-3 w-3` inside badges.

## Do's and Don'ts

- **Do** use `brand-blue` as the only brand accent; keep it for primary/active/interactive.
- **Do** express status through the `status` token pairs (tint background + saturated text).
- **Do** keep surfaces soft: `rounded-card` panels, hairline gray borders, `shadow-card`.
- **Don't** introduce a second web font or a competing accent colour.
- **Don't** use heavy shadows or hard borders — the aesthetic is flat and quiet.
- **Don't** hardcode hex values in components; reference these tokens (or their Tailwind
  equivalents) instead.
