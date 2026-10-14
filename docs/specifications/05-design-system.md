# 05 — Design System ("Concept B — Premium Executive")

| Field | Value |
|---|---|
| Status | DRAFT v0.1. The aesthetic direction is CONFIRMED (brief). All token values are PROPOSED. |
| Date | 2026-10-14 |
| Figma status | **No Figma assets exist yet.** Nothing in this document claims otherwise. |

## 1. Design principles
1. **Calm authority**: generous whitespace, few colours, confident typography. The UI should feel like a boardroom, not a dashboard toy.
2. **Gold is a signal, not a decoration**: reserve it for primary emphasis, executive identity accents and key status. Keep it to about 5% of the surface or less.
3. **Clarity of agency**: always make clear who is acting (a human vs. which executive) and whether an action is proposed, pending approval or done.
4. **Trust through evidence**: citations, sources and audit trails are visible.

## 2. Colour tokens (PROPOSED. Verify contrast in implementation.)

### Brand
| Token | Hex | Use |
|---|---|---|
| `navy-950` | `#0B1526` | App chrome (dark), sidebar background |
| `navy-900` | `#111F38` | Primary text on light surfaces; headers |
| `navy-800` | `#1A2C4E` | Hover states on dark surfaces |
| `navy-700` | `#243B66` | Primary button background |
| `navy-500` | `#3E5A8C` | Links, focus accents (light) |
| `navy-100` | `#E3E8F1` | Subtle navy tint backgrounds |
| `gold-600` | `#9C7A2E` | Gold text on light surfaces (meets AA for large text; check for small text) |
| `gold-500` | `#B8923A` | Primary accent, active nav indicator, key icons |
| `gold-300` | `#D9C08A` | Gold on navy (text/icons on `navy-950`) |
| `gold-100` | `#F4ECD9` | Highlight backgrounds (selected rows, callouts) |

### Warm neutrals
| Token | Hex | Use |
|---|---|---|
| `stone-0` | `#FFFFFF` | Cards |
| `stone-50` | `#FAF8F4` | App background (light) |
| `stone-100` | `#F2EEE7` | Secondary surfaces, table headers |
| `stone-200` | `#E5DFD4` | Borders |
| `stone-400` | `#B3AA9B` | Disabled, placeholder (decorative only, not body text) |
| `stone-600` | `#6E6557` | Secondary text |
| `stone-800` | `#3A342B` | Body text alternative |

### Semantic (muted to fit the palette)
| Token | Hex | Use |
|---|---|---|
| `success-600` | `#2F6B4F` | Success text/icons |
| `warning-600` | `#9A5B13` | Warnings, approval pending |
| `danger-600` | `#A23B3B` | Errors, deny, destructive |
| `info-600` | `#2D5D8A` | Info |
Each has a `-50` background tint.

### Executive identity accents
Because customers decide how many executives they have, identity accents come from a **palette of 10 muted hues**. The customer picks one, or one is auto-assigned to keep hues distinct within a Boardroom. Accents are used only for avatars, the boardroom speaker rail and thread markers, and always paired with the executive's name and avatar (never colour alone, since hues may repeat in large teams). The five standard templates get default hues and avatars once their roles are confirmed (OQ-003).

### Dark mode
PROPOSED for V1: a **light content area with a dark navy sidebar**. A full dark theme is NEEDS CLARIFICATION (OQ-035). Tokens are defined semantically (`--surface`, `--text-primary`, `--accent`) so a dark theme can be added later.

## 3. Typography
| Role | Typeface (PROPOSED) | Size / line-height | Weight |
|---|---|---|---|
| Display (page titles, executive names) | Serif, e.g. *Source Serif 4* or *Playfair Display* (licence check) | 32/40, 28/36 | 600 |
| Headings H1–H4 | Sans: *Inter* | 24/32, 20/28, 18/26, 16/24 | 600 |
| Body | *Inter* | 15/24 (default), 14/20 (dense) | 400 |
| Caption / meta | *Inter* | 12/16 | 500 |
| Mono (IDs, payloads) | *JetBrains Mono* | 13/20 | 400 |

The serif is used sparingly. It carries the "premium executive" tone; the sans carries usability.

## 4. Spacing, grid and layout
- 4 px base scale: 4, 8, 12, 16, 24, 32, 48, 64.
- Radius: 6 px (inputs, buttons), 10 px (cards), 16 px (modals). Avoid fully rounded "pill" buttons, except for tags.
- Elevation: 3 levels with soft, warm-tinted shadows. Prefer borders over heavy shadows.
- Layout shell: sidebar 248 px (collapsed 72) · content max-width 1280 · optional right context panel 360 (citations, case context, approval details).
- Grid: 12 columns on desktop, 8 on tablet, 4 on mobile. Gutter 24/16/16.

## 5. Shared components (inventory to build in Figma and code)
| Group | Components |
|---|---|
| Foundations | Colour, type, spacing, icon set (outline, 1.5 px stroke, e.g. Lucide), elevation |
| Actions | Button (primary navy, accent gold-outline, secondary, ghost, destructive; sizes S/M/L; loading), Icon button, Split button |
| Inputs | Text, textarea, select, combobox, multi-select, date/time, toggle, checkbox, radio, file drop zone, rich-text editor, slider |
| Navigation | Sidebar, top bar with org switcher, breadcrumbs, tabs, command palette, pagination |
| Data display | Table (sortable, selectable, sticky header, responsive → cards), list, card, stat tile, badge/status pill, avatar (human/executive variants), timeline, kanban column/card, calendar |
| AI-specific | Chat message (human/executive/system/tool), streaming indicator, citation chip + source popover, proposed-action card (task/decision/approval), tool-execution status row, boardroom speaker rail, "insufficient evidence" notice |
| Governance | Approval card, payload diff viewer, policy rule row, effect badge (Allow/Approval/Deny) |
| Feedback | Toast, inline alert, banner (billing/entitlement), empty state, skeleton, progress, error panel with correlation ID |
| Overlays | Modal, drawer/sheet, popover, tooltip, confirm dialog (destructive variant requires typing a name) |

## 6. Patterns
- **Forms**: labels above fields, helper text below, validation on blur and on submit, error text in `danger-600` plus an icon. Primary action at bottom-right on desktop, full-width on mobile. Unsaved-change guard.
- **Tables**: dense mode toggle, column visibility, saved filters (V1.1), row actions in a kebab menu, bulk actions bar.
- **Cards**: header (title + meta), body, footer actions. An executive card has a gold hairline top border.
- **Notifications**: toasts for transient results (auto-dismiss 5 s, except errors). Notification centre for persistent events. Banners for org-wide states (past due, integration needs re-auth).
- **AI agency markers**: every executive message shows the executive's avatar, name and role. Tool actions show "Proposed", "Awaiting approval", "Executed" or "Denied" with icons.

## 7. Accessibility (WCAG 2.2 AA target)
- Contrast: body text ≥ 4.5:1, large text and UI components ≥ 3:1. Gold on white fails for small text, so use `gold-600` or navy instead.
- Focus: a visible 2 px focus ring (`navy-500` on light, `gold-300` on dark) that is never removed.
- Full keyboard operation, including the boardroom and kanban (with keyboard alternatives to drag).
- Streaming chat regions use `aria-live="polite"`, throttled so they don't flood screen readers.
- Colour is never the sole carrier of meaning (status pills include text).
- Respect `prefers-reduced-motion`.
- Minimum target size of 24×24 px (aim for 44×44 on touch).

## 8. Responsive behaviour
See spec 04 §0. Additional rules: the boardroom on mobile shows one speaker at a time with a participant sheet; the approval diff viewer stacks; the editor toolbar collapses into an overflow menu.

## 9. Figma deliverables required (NOT YET CREATED)
| # | Deliverable | Status |
|---|---|---|
| F-1 | Foundations page (colour, type, spacing, elevation, icons) as Figma variables, light (+ dark if approved) | Not started |
| F-2 | Component library with variants and states (§5) | Not started |
| F-3 | Layout templates: app shell, list page, detail page, settings page, chat/office, boardroom | Not started |
| F-4 | High-fidelity screens for the approved inventory (desktop + mobile for core flows) | Not started; depends on OQ-002 |
| F-5 | Prototype of key journeys: onboarding, office chat, boardroom, approval | Not started |
| F-6 | Executive identity set: avatars for the five standard templates + a generic avatar library and the 10-hue accent palette for custom executives | Not started; depends on OQ-003 |
| F-7 | Handoff notes / Code Connect mapping to code components | Not started |

**Ownership (CONFIRMED, SOW §2 and §6):** the contractor (us) produces F-1…F-7 as **editable Figma source with assets**, including a **clickable critical-flow prototype** (F-5). All designs belong to AdvoLevel on payment. Files should live in an AdvoLevel-controlled Figma workspace, or be transferred to one at handover. Font licences (e.g. any commercial serif) must be disclosed as third-party licences. Prototype critical flows (PROPOSED for reconciliation): onboarding, executive office chat, boardroom, approval decision, Content Factory intake → publish, subscription checkout.
