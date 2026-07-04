# UI/UX Review — Chelsea Shoes

Reviewed: `base.html`, list pages (orders, staff, clients, suppliers, producement, material stock, sale, warehouse), detail pages (`order_read`, `producement_read`, `material_stock/read`), forms and partials.

---

## 1. Critical problems (fix first)

### 1.1 Flash messages are invisible on almost every page
`{% if messages %}` is rendered only in `login.html`, `orderDetails/detail_create.html`, and `material_stock/purchase_form.html`. But views call `messages.error/warning/success` in many other places (supplier delete, purchase stock errors, order detail warnings like "Material stock topilmadi", "yetarli emas"). On any other page the user gets **no feedback at all** — the action silently fails or succeeds.

**Fix:** render messages once in `base.html` (above `{% block content %}`) as dismissible Bootstrap alerts, then remove the per-page copies.

### 1.2 Two Bootstrap versions loaded at once
`base.html` loads the Sneat theme (Bootstrap 5) **and** `bootstrap/4.5.2/bootstrap.min.css` from CDN (line ~55). BS4 styles override BS5/theme styles unpredictably — this is a likely source of "broken-looking" spacing and form controls.

**Fix:** remove the Bootstrap 4.5.2 stylesheet. Also: Font Awesome is a `6.0.0-beta3` build and `login.html` uses `bootstrap@5.3.0-alpha1` — replace both with stable releases.

### 1.3 Delete actions use GET links
The delete modal confirms, but then navigates to `delete/<pk>` with a plain GET link. Destructive actions over GET can be triggered by prefetching/crawlers/history and have no CSRF protection.

**Fix:** submit a small POST form (with `{% csrf_token %}`) from the modal instead of following an `<a href>`.

### 1.4 Broken filter in Sale page
`templates/Sale/sale.html` line ~87: `{% if client == client.id %}` compares the loop variable with its own id — the selected client is never kept after filtering. Should be `{% if client_id == client.id %}` (and the view must pass `client_id`).

### 1.5 Shoe model image can crash the home page
`index.html` uses `{{ shoe_model.image.url }}` with no guard. If any model has no image, the whole page throws `ValueError`. Use `{% if shoe_model.image %}` with a placeholder image in `else`.

---

## 2. Consistency mistakes

### 2.1 Date formats are mixed everywhere
The project rule is `YYYY-MM-DD`, but today:
- `producement.html` shows deadline as `d.m.Y` and order date as `Y.m.d` in the *same cell block*;
- `orders.html` uses `d.m.Y`;
- `order_read.html` and material stock use `Y-m-d`;
- flatpickr inputs use `d m Y` (`"dd mm yyyy"` placeholder).

**Fix:** use `|date:"Y-m-d"` everywhere and switch flatpickr `dateFormat` to `Y-m-d` so what users type matches what they see in tables.

### 2.2 Hardcoded UI text (violates the system_variables rule)
- `producement_read.html` — entire page is hardcoded Uzbek: "Ish Tafsilotlari", "Xodim", "Miqdor", "Yangilash", "O'chirish", "Orqaga", etc.
- `login.html` — "Login", "Ism", "Parol", "Chelsea-shoes".
- `order_read.html` — "Juftiga" (line ~89), "Materiallar kiritilmagan." (line ~111).
- `pagination.html` / `orders.html` — aria-labels "Birinchi", "Oldingi", "Keyingi", "Oxirgi", "Sahifa navigatsiyasi".

**Fix:** move all of these into `config/system_variables.py`.

### 2.3 Row numbering restarts on every page
`orders.html` and the sklat-era tables use `{{ forloop.counter }}` for the ID column, so page 2 starts again at 1. Producement tables already do it right with `{{ forloop.counter0|add:page_obj.start_index }}` — apply the same pattern to orders, sale, clients, etc. (Or show the real database id, but pick one convention.)

### 2.4 Duplicated pagination markup
`orders.html` (and previously producement) contains a full inline copy of the pagination block even though `partials/pagination.html` exists. Replace the inline copies with the partial — one source of truth.

### 2.5 Action buttons differ per page
- Producement: icon-only buttons stacked **vertically** (`d-flex flex-column`), which makes rows very tall.
- Orders/suppliers: horizontal icon buttons.
- Some pages add text labels next to icons, some don't.

**Fix:** one convention — horizontal, icon-only `btn-sm` buttons with `title="..."` tooltips, in the same order everywhere (view / edit / delete).

### 2.6 Form controls: `form-control` vs `form-select`
Filter selects use `class="form-control"` on some pages (producement, sale) and `form-select` on others (warehouse, material stock). In Bootstrap 5 selects should be `form-select` (gives the dropdown arrow).

---

## 3. UX improvements (suggestions)

### 3.1 Filters take too much vertical space
Every list page opens with a large always-visible filter card titled with an `<h1>{{FILTER}}</h1>`. The actual page title is pushed below the fold.

**Suggestions:**
- Make the filter card collapsible (Bootstrap collapse, collapsed by default; auto-expand when filters are active).
- The page should start with the entity title (`{{ORDERS}}`, `{{PRODUCEMENT}}` …) + "create" button; filter comes second.
- `<h1>` for "Filter" is wrong semantically — the page title should be the only `h1`.

### 3.2 Filters should indicate they are active
After filtering there is no visual hint that a filter is applied (other than reading each input). Show a badge like "3 ta filtr faol" on the filter toggle, or a highlighted "Tozalash" button when `request.GET` has values.

### 3.3 Auto-submit selects
For select-based filters, submitting on `change` (or at least keeping the Filter button sticky) saves a click. Keep the explicit button for text inputs.

### 3.4 Status change without feedback or undo
The inline status `<select>` on orders/producement posts immediately via `fetch`. On failure it only `alert()`s and the select keeps the wrong value (the tracked `previousStatus` is never restored). On success there is a subtle green border for 800ms.

**Fix:** restore `previousStatus` on failure; consider a toast for success. Also consider confirming when switching **to COMPLETED**, since that triggers stock releases and cannot be casually undone.

### 3.5 Non-functional navbar search
The search input in the top navbar does nothing. Either remove it or wire it to a real global search. A dead search box erodes trust in the whole UI.

### 3.6 Disabled placeholder menu items
INCOME / DEBTS / EXPENSES appear in the sidebar as permanently disabled items. If they are not coming soon, remove them; if they are, add a small "tez orada" badge so it reads as intentional.

### 3.7 Delete confirmation is generic
The modal always says the same text. Include the entity name ("JAHONGIR ALIYEV buyurtmasi o'chirilsinmi?") by passing a `data-item-label` alongside `data-delete-url` — prevents deleting the wrong row from a long table.

### 3.8 Tables on mobile
Only some tables are wrapped in `.table-responsive` (orders yes, producement's main table no). Wrap all of them; the producement table with its multi-line cells overflows badly on narrow screens.

### 3.9 Empty states
"{{PRODUCEMENT}} {{NO_DATA}}" as a single table row is fine, but for first-time-use pages (no data at all, no filters) a friendlier empty state with a direct "create" button link would help onboarding.

### 3.10 Producement create flow
The chained forms (Lazir→Kroy etc.) auto-fill and lock order/model — good. Two improvements:
- When the previous-producement select is empty (no Kroy work exists), the form gives a validation error only after submit. Show an inline hint immediately ("Avval Kroy ishini yarating").
- The readonly-locked selects look identical to editable ones until clicked. The `.readonly` gray style exists in `producement_create.html` — apply it in updates too, and add a small lock icon.

---

## 4. Accessibility

1. **Zoom is blocked**: `viewport` meta has `user-scalable=no, maximum-scale=1.0`. Remove those — users must be able to pinch-zoom, and it harms nothing on desktop.
2. Icon-only buttons have no accessible name — add `title` + `aria-label` (e.g. `aria-label="{{DELETE}}"`).
3. Color-only status distinction (green/red badges for IN/OUT, balance colors) — fine, but keep the text label too (currently done — keep it that way).
4. `lang="en"` on `<html>` while the UI is Uzbek — set `lang="uz"`.

---

## 5. Dead code / cleanup

- `templates/producement/producement_create_demo.html` — not referenced by any view (views render `producement_create.html` / `producement_update.html`). Delete it.
- `index.html` — large commented-out jQuery block (total-quantity) and commented markup; remove.
- `orders.html` — commented-out prev/next status `<td>` block; remove.
- `base.html` — empty `<style>` tag in head, GitHub buttons script (`buttons.github.io`) that serves no purpose, and `dashboards-analytics.js` + ApexCharts loaded on **every** page though no page renders charts. Trim these; they slow every page load.
- Duplicate `{{ order_details|json_script }}` / demo JS patterns between `_producement_form_scripts.html` and the demo template — keep only the partial.

---

## 6. Quick-win priority order

| # | Item | Effort | Impact |
|---|------|--------|--------|
| 1 | Render messages in `base.html` | XS | High — users finally see errors |
| 2 | Remove Bootstrap 4.5.2 CSS | XS | High — fixes subtle styling breakage |
| 3 | Unify dates to `Y-m-d` (incl. flatpickr) | S | High — rule compliance + clarity |
| 4 | Fix Sale client filter bug | XS | Medium |
| 5 | Guard shoe model image + placeholder | XS | Medium — prevents 500 |
| 6 | Delete via POST forms | S | Medium — safety |
| 7 | Move hardcoded texts to `system_variables.py` | S | Medium — rule compliance |
| 8 | Collapsible filters + proper page titles | M | Medium — big visual win |
| 9 | Consistent action buttons + `form-select` | S | Low-Medium |
| 10 | Remove dead code / unused scripts | S | Low — performance, hygiene |
