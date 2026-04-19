# visual-design Specification

## Purpose
Define the visual language of the TokenAIzer dashboard. All frontend
components SHALL follow these guidelines. This spec is the single
source of truth for aesthetic decisions.

## Reference
The visual style is inspired by Linear (linear.app). The goal is a
focused, dark, typographically precise interface that communicates
technical data with clarity and elegance.

## Color System

### Base palette
- Background primary:     #0a0a0a  (page background)
- Background secondary:   #111111  (card surfaces)
- Background tertiary:    #1a1a1a  (elevated elements, dropdowns)
- Background hover:       #222222  (interactive hover states)
- Border subtle:          #1f1f1f  (card borders, dividers)
- Border default:         #2a2a2a  (inputs, active borders)

### Text
- Text primary:           #ededed  (main content, metric values)
- Text secondary:         #888888  (labels, captions, descriptions)
- Text tertiary:          #555555  (placeholders, disabled)

### Accent (Linear purple)
- Accent primary:         #5e6ad2  (active states, highlights)
- Accent hover:           #6b78e5  (hover on accent elements)
- Accent subtle:          #1e2040  (accent backgrounds, glow base)
- Accent glow:            rgba(94, 106, 210, 0.15) (power button glow)

### Semantic
- Success:                #4caf7d  (positive values)
- Warning:                #e5a03a  (moderate usage)
- Danger:                 #e5534b  (high usage, errors)

## Typography

### Font stack
Primary: 'Geist', 'Inter', system-ui, sans-serif
Mono:    'Geist Mono', 'JetBrains Mono', monospace

Load Geist from: https://vercel.com/font (open source, same font
Linear-adjacent interfaces use). Fall back to Inter from Google Fonts.

### Scale
- Metric value (large):  48px / weight 600 / text-primary / letter-spacing -0.03em
- Metric value (medium): 32px / weight 600 / text-primary / letter-spacing -0.02em
- Metric label:          11px / weight 500 / text-secondary / uppercase / letter-spacing 0.08em
- Section heading:       13px / weight 500 / text-primary
- Body:                  14px / weight 400 / text-secondary / line-height 1.6
- Caption:               12px / weight 400 / text-tertiary

### Rules
- Metric values and labels MUST have high contrast between them.
  Value: text-primary at large size. Label: text-secondary at small size.
- Never use font-weight above 600.
- Numbers in metrics use tabular figures: font-variant-numeric: tabular-nums

## Layout

### Grid
- Max content width: 1200px, centered, padding 0 24px
- Card grid: CSS Grid, repeat(auto-fit, minmax(280px, 1fr)), gap 12px
- Section spacing: 32px between major sections

### Cards
- Background: #111111
- Border: 0.5px solid #1f1f1f
- Border radius: 8px
- Padding: 20px 24px
- No box-shadow — elevation is communicated through background color difference only

### Power button
- Shape: circle, 56px diameter
- Background idle:   #1a1a1a
- Background active: #1e2040
- Border idle:       1px solid #2a2a2a
- Border active:     1px solid #5e6ad2
- Icon:              SVG power symbol, 22px, color matches border
- Glow active:       box-shadow: 0 0 0 4px rgba(94,106,210,0.15),
                                 0 0 16px rgba(94,106,210,0.2)
- Transition:        all 200ms ease

### Settings panel
- Trigger: small gear icon button, top-right corner of dashboard header
- Panel: absolute positioned, background #1a1a1a, border 0.5px solid #2a2a2a,
  border-radius 8px, padding 16px, min-width 220px
- Animation: fade + translateY(-4px) → translateY(0), 150ms ease
- Each setting row: label left (13px text-secondary) + control right

## Chart (Chart.js)

### Style
- Background: transparent
- Grid lines: #1f1f1f, 1px
- Axis labels: #555555, 11px
- No chart border

### Series colors
- Input tokens:   #5e6ad2 (accent primary)
- Output tokens:  #4caf7d (success green)
- Thinking tokens:#e5a03a (warning amber)
- Cache tokens:   #888888 (text secondary)

### Line style
- Line width: 1.5px
- Point radius: 0 (no dots on line)
- Point hover radius: 4px
- Fill: gradient from series color at 0.15 opacity to transparent

### Tooltip
- Background: #1a1a1a
- Border: 0.5px solid #2a2a2a
- Border radius: 6px
- Font: 12px, text-primary
- Padding: 8px 12px

## Animations

### Number count-up
When a metric value updates, animate from old value to new value
over 400ms using an easing function (easeOutCubic). Use a Svelte
tweened store for this.

### Chart update
Chart.js built-in animation, duration 300ms, easing 'easeOutQuart'.
Disable animation only on initial render to avoid flash.

### Transitions
- Page load: stagger cards with 50ms delay between each,
  translateY(8px) → translateY(0) + opacity 0 → 1, 300ms ease
- Settings panel: 150ms ease, fade + slight upward movement
- Status indicator: color transition 200ms ease

## Components

### Metric card
Structure:
  - Label (top): 11px uppercase text-secondary
  - Value (middle): 48px weight-600 text-primary tabular-nums
  - Subvalue (bottom, optional): 13px text-secondary

### Status indicator
Small circle, 8px diameter, positioned next to power button label.
- Idle:    background #555555
- Active:  background #4caf7d, box-shadow: 0 0 6px rgba(76,175,125,0.5)
- Pulse animation when active: scale 1 → 1.3 → 1, 2s infinite

### Model badge
Pill shape, background #1a1a1a, border 0.5px solid #2a2a2a,
padding 3px 8px, font 11px text-secondary, border-radius 4px.