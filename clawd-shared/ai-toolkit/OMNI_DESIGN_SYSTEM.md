# OMNI POOL BUILDERS — DESIGN SYSTEM
## HTML Email & DigiDoc Visual Reference

All templates must follow these patterns exactly. Table-based layout, inline styles only.

---

## COLOR PALETTE

| Token | Hex | Usage |
|-------|-----|-------|
| Forest Green (dark) | `#1A3512` | Gradient end, deep accents |
| Forest Green (mid) | `#2C4A1E` | Gradient start, primary green, CTA links |
| Green Accent | `#5A8C3F` | Secondary green highlights |
| Gold | `#C9A84C` | Section labels, accent borders, stars, badges |
| Gold (muted) | `#92740c` | Gold text on light backgrounds |
| Charcoal | `#1A1A1A` | Header/footer background, dark table headers |
| Navy Text | `#1e3a5f` | Primary text, headings, data values |
| Body Text | `#374151` | Paragraph text, notes |
| Gray Text | `#6b7280` | Secondary text, metadata |
| Light Gray Text | `#9ca3af` | Labels, captions, units |
| White | `#FFFFFF` | Body background, alternating rows |
| Off-White | `#F9FAFB` | Alternating rows, info bars |
| Light Border | `#E5E7EB` | Table borders, section dividers |
| Row Divider | `#F3F4F6` | Inner row borders |
| Blue Accent | `#4472C4` | Seasonal tip, schedule header |
| Blue Light BG | `#F0F7FF` | Seasonal tip background, LSI "before" |
| Blue Light Border | `#D4E4F7` | Blue section borders |
| Green Light BG | `#EBF5EB` | Next visit preview, LSI "after" |
| Green Light Border | `#C6DFC0` | Green section borders |
| Warm Cream | `#FFFDF5` | Pool birthday ribbon, issue flag bg |

---

## TYPOGRAPHY

| Element | Font Stack | Size | Weight | Other |
|---------|-----------|------|--------|-------|
| Body text | `'Lora',Georgia,'Times New Roman',serif` | 12-13px | normal | line-height: 1.7 |
| UI labels / section headers | `'Montserrat',Arial,Helvetica,sans-serif` | 9-10px | bold | letter-spacing: 2-4px, uppercase |
| Data values | `'Montserrat',Arial,Helvetica,sans-serif` | 12-14px | bold | — |
| Section titles | `'Lora',Georgia,serif` | 18px | normal | color: #1e3a5f |
| Small captions | `'Montserrat',Arial,Helvetica,sans-serif` | 8-9px | normal | color: #9ca3af |
| Customer name (proposals) | `'Mrs Saint Delafield',cursive` | 48px | normal | Only on proposals, not emails |

**Note:** Google Fonts (Lora, Montserrat) may not render in all email clients. The fallback stacks ensure graceful degradation.

---

## LAYOUT RULES

- **Max width:** 680px, centered with `margin: 0 auto`
- **Side padding:** 32px on all content sections
- **All layout is TABLE-BASED** — no div floats, no flexbox, no grid
- **Inline styles ONLY** — no `<style>` blocks, no external CSS
- **No JavaScript** — email clients strip it
- **Images:** Use `*logo*` merge tag, or host on tucsonpoolbuilders.com

---

## STRUCTURAL PATTERNS

### 1. GREEN ACCENT BAR (top of every template)
```html
<table style="background-color: #2C4A1E;" bgcolor="#2C4A1E" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 6px 0;">&nbsp;</td></tr></tbody>
</table>
```

### 2. DARK HEADER WITH LOGO
```html
<table style="background-color: #1A1A1A; border-bottom: 3px solid #C9A84C;" bgcolor="#1A1A1A" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody>
<tr><td style="padding: 24px 32px 8px;" align="center">
<div style="margin-bottom: 8px;">*logo*</div>
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 10px; letter-spacing: 4px; color: #c9a84c; margin-bottom: 6px;">TEMPLATE TITLE HERE</div>
</td></tr>
<tr><td style="padding: 0 32px 16px;">
<table width="100%" cellspacing="0" cellpadding="0"><tbody><tr>
<td style="padding-top: 10px; text-align: center; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #6b7280; letter-spacing: 1px;">*address*</td>
</tr></tbody></table>
</td></tr>
</tbody>
</table>
```

### 3. SECTION LABEL (gold, uppercase, spaced)
```html
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 10px; letter-spacing: 3px; color: #c9a84c; margin-bottom: 6px;">SECTION NAME</div>
```

### 4. SECTION TITLE (larger, navy)
```html
<div style="font-size: 18px; color: #1e3a5f; margin-bottom: 4px;">Section Title</div>
```

### 5. DATA TABLE WITH DARK HEADER
```html
<table style="border: 1px solid #E5E7EB;" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody>
<tr style="background-color: #1A1A1A;" bgcolor="#1A1A1A">
<td style="padding: 8px 12px; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 10px; font-weight: bold; color: #ffffff; letter-spacing: 1px;">COLUMN</td>
<!-- more columns -->
</tr>
<tr style="background-color: #FFFFFF;" bgcolor="#FFFFFF">
<td style="padding: 10px 12px; font-size: 12px; color: #1e3a5f; border-bottom: 1px solid #F3F4F6;">Row data</td>
</tr>
<tr style="background-color: #F9FAFB;" bgcolor="#F9FAFB">
<td style="padding: 10px 12px; font-size: 12px; color: #1e3a5f; border-bottom: 1px solid #F3F4F6;">Alternating row</td>
</tr>
</tbody>
</table>
```

### 6. HIGHLIGHTED CALLOUT BOX (gold border — for warnings, flags)
```html
<table style="border: 2px solid #C9A84C; background-color: #FFFDF5;" bgcolor="#FFFDF5" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 14px 16px;">
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 10px; letter-spacing: 2px; color: #92740c; font-weight: bold; margin-bottom: 4px;">&#x26A0; CALLOUT TITLE</div>
<div style="font-size: 13px; color: #1e3a5f; font-weight: bold;">Content here</div>
</td></tr></tbody>
</table>
```

### 7. INFO BOX WITH LEFT ACCENT (green = positive, blue = info)
```html
<!-- Green (next steps, positive) -->
<div style="padding: 14px 16px; background-color: #EBF5EB; border: 1px solid #C6DFC0; border-left: 3px solid #2C4A1E; font-size: 13px; color: #374151; line-height: 1.7;">Content</div>

<!-- Blue (tips, informational) -->
<table style="background-color: #F0F7FF; border: 1px solid #D4E4F7; border-left: 4px solid #4472C4;" bgcolor="#F0F7FF" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 14px 16px;">
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; letter-spacing: 2px; color: #4472c4; font-weight: bold; margin-bottom: 6px;">INFO LABEL</div>
<div style="font-size: 12px; color: #374151; line-height: 1.6;">Content</div>
</td></tr></tbody>
</table>

<!-- Gold ribbon (special, celebratory) -->
<table style="background-color: #FFFDF5; border-left: 4px solid #C9A84C;" bgcolor="#FFFDF5" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 10px 14px;">
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 10px; font-weight: bold; color: #92740c; letter-spacing: 1px;">RIBBON TEXT</div>
</td></tr></tbody>
</table>
```

### 8. CTA BLOCK (call to action)
```html
<table style="background-color: #F9FAFB; border: 1px solid #E5E7EB;" bgcolor="#F9FAFB" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 16px; text-align: center;">
<div style="font-size: 13px; color: #374151; line-height: 1.6;">If you have any questions, just <strong>text/call the office <a href="tel:5202228503" style="color: #2C4A1E; text-decoration: none; font-weight: bold;">520-222-8503</a></strong> or reply to this email!</div>
</td></tr></tbody>
</table>
```

### 9. PHOTO SECTION (5 slots per category using upload type 31)
```html
<div style="border: 1px solid #E5E7EB; padding: 10px; text-align: center;">
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; letter-spacing: 2px; color: #9ca3af; margin-bottom: 8px;">CATEGORY NAME</div>
<div style="max-width: 600px; overflow: hidden; margin: 0 auto;">*uploaded-docs-type-31* *uploaded-docs-type-31* *uploaded-docs-type-31* *uploaded-docs-type-31* *uploaded-docs-type-31*</div>
</div>
```

### 10. LICENSE/COMPLIANCE BLOCK (customer-facing templates)
```html
<table style="background-color: #F9FAFB; border-bottom: 2px solid #E5E7EB;" bgcolor="#F9FAFB" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 16px 32px;">
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; letter-spacing: 2px; color: #c9a84c; margin-bottom: 8px;">FULLY LICENSED &bull; BONDED &bull; INSURED</div>
<div style="font-size: 10px; color: #6b7280; line-height: 1.5; margin-bottom: 8px;"><strong style="color: #1e3a5f;">Consumer Awareness Note:</strong> Unlicensed work may lack insurance, risking your protection. We&rsquo;re authorized by the Arizona Registrar of Contractors for all listed work, ensuring compliance and full coverage.</div>
<table border="0" width="100%" cellspacing="0" cellpadding="0"><tbody>
<tr>
<td style="padding: 2px 0; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #374151;" width="50%">#282151: KA-5 Pool Contractor</td>
<td style="padding: 2px 0; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #374151;" width="50%">#326882: CR-21 Hardscaping/Masonry</td>
</tr>
<tr>
<td style="padding: 2px 0; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #374151;">#350879: CR-37 Ramada, Pergola &amp; Canopies</td>
<td style="padding: 2px 0; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #374151;">#353526: CR-14 Fencing</td>
</tr>
<tr>
<td style="padding: 2px 0; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #374151;" colspan="2">#339947: CR-37 Gas Lines/Plumbing</td>
</tr>
</tbody></table>
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; font-weight: bold; color: #2C4A1E; margin-top: 6px; font-style: italic;">Choose our licensed, insured expertise</div>
</td></tr></tbody>
</table>
```

### 11. FOOTER (every template)
```html
<table style="margin-top: 24px; background-color: #2C4A1E;" bgcolor="#2C4A1E" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 4px 0;">&nbsp;</td></tr></tbody>
</table>
<table style="background-color: #1A1A1A; border-top: 3px solid #C9A84C;" bgcolor="#1A1A1A" border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 20px 32px;" align="center">
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 11px; font-weight: bold; color: #ffffff; margin-bottom: 4px;">Omni Pool Builders &amp; Design LLC</div>
<div style="font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 10px; color: #6b7280;">6640 N. Oracle Rd. Suite 130 &nbsp;|&nbsp; Tucson, AZ 85704 &nbsp;|&nbsp; (520) 222-8503</div>
<div style="margin-top: 8px; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #c9a84c; letter-spacing: 1px;">LICENSED &bull; BONDED &bull; INSURED</div>
<div style="margin-top: 4px; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 8px; color: #888888; line-height: 1.5;">ROC #282151 KA-5 &bull; ROC #326882 CR-21 &bull; ROC #350879 CR-37 &bull; ROC #353526 CR-14 &bull; ROC #339947 CR-37</div>
<div style="margin-top: 6px; font-family: 'Montserrat',Arial,Helvetica,sans-serif; font-size: 9px; color: #888888;">We built your pool. We maintain your pool. That&rsquo;s the Omni difference.</div>
</td></tr></tbody>
</table>
```

---

## TEMPLATE SKELETON (copy this to start any new template)

```html
<div style="max-width: 680px; margin: 0 auto; font-family: 'Lora',Georgia,'Times New Roman',serif; color: #1a1a1a; background: #FFFFFF;">

<!-- GREEN ACCENT BAR -->
[paste pattern #1]

<!-- HEADER -->
[paste pattern #2 — change TEMPLATE TITLE]

<!-- LICENSE BLOCK (customer-facing only) -->
[paste pattern #10]

<!-- INTRO -->
<table border="0" width="100%" cellspacing="0" cellpadding="0">
<tbody><tr><td style="padding: 20px 32px;">
<div style="font-size: 16px; font-weight: bold; color: #1e3a5f; margin-bottom: 8px;">Subject Line / Heading</div>
<div style="font-size: 13px; color: #374151; line-height: 1.7;">Body text explaining the purpose of this communication.</div>
</td></tr></tbody>
</table>

<!-- CONTENT SECTIONS -->
[build sections using patterns #3-9 as needed]

<!-- CTA -->
[paste pattern #8]

<!-- FOOTER -->
[paste pattern #11]

</div>
```

---

## DO's AND DON'Ts

**DO:**
- Use table-based layout exclusively
- Use inline styles on every element
- Use `&amp;` `&ndash;` `&mdash;` `&rsquo;` for special characters
- Use `&#x26A0;` for the warning symbol (⚠)
- Alternate row backgrounds: #FFFFFF / #F9FAFB
- Keep max-width: 680px
- Test by pasting into TinyMCE source code editor

**DON'T:**
- Use `<div>` for layout (use `<table>`)
- Use `<style>` blocks or external CSS
- Use JavaScript
- Use tildes (~) in email templates
- Use `&x26A0;` (missing #) — must be `&#x26A0;`
- Hardcode data that should come from merge fields
- Forget the 3px gold border under the header
- Use `background:` shorthand — always use `background-color:`
- Use `linear-gradient()` in emails — Gmail strips it entirely
- Forget `bgcolor` HTML attributes on `<table>`, `<tr>`, and `<td>` elements

---

## EMAIL CLIENT BACKGROUND COLOR RULES (CRITICAL)

Gmail, Outlook, and many email clients **strip CSS `background` and `background-color` properties** from rendered HTML. The fix is to ALWAYS add the `bgcolor` HTML attribute alongside the inline style.

### The Rule: ALWAYS use BOTH
```html
<!-- WRONG — Gmail strips this -->
<table style="background: #1A1A1A;">

<!-- WRONG — background shorthand can be stripped -->
<table style="background: #1A1A1A;" bgcolor="#1A1A1A">

<!-- CORRECT — background-color + bgcolor -->
<table style="background-color: #1A1A1A;" bgcolor="#1A1A1A">
```

### Gradient Fallback
CSS gradients (`linear-gradient`) are NOT supported in email clients. Use a solid fallback:
```html
<!-- WRONG — gradient stripped, shows nothing -->
<table style="background: linear-gradient(135deg,#2C4A1E 0%,#1A3512 100%);">

<!-- CORRECT — solid color with bgcolor fallback -->
<table style="background-color: #2C4A1E;" bgcolor="#2C4A1E">
```

### Apply bgcolor to ALL colored elements
```html
<!-- Tables -->
<table style="background-color: #1A1A1A;" bgcolor="#1A1A1A">

<!-- Table rows -->
<tr style="background-color: #F9FAFB;" bgcolor="#F9FAFB">

<!-- Table cells -->
<td style="background-color: #EBF5EB;" bgcolor="#EBF5EB">
```

### Checklist Before Sending Any Email Template
- [ ] Zero instances of `background:` shorthand (must be `background-color:`)
- [ ] Zero instances of `linear-gradient` (use solid color fallback)
- [ ] Every `<table>` with a background has `bgcolor` attribute
- [ ] Every `<tr>` with a background has `bgcolor` attribute  
- [ ] Every `<td>` with a background has `bgcolor` attribute
- [ ] Test in Gmail, Outlook, and Apple Mail before going live
