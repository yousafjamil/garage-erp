# Print formats

Six formats ship with the system: Garage Quotation, Garage Tax Invoice, Garage Job Card, Garage Vehicle Inspection,
Garage Vehicle Check-In, Garage Payment Receipt. Source: `apps/garage_management/garage_management/print_formats/*.html`
(shared style in `_style.html`, footer in `_tail.html`), installed by `setup/print_formats.py` on every `migrate`.

**Client-editable without code:** Garage Settings (titles, terms, bank details, notes, colours, letterhead images).

**Layout changes:** *Printing → Print Format → (format) → Menu → Duplicate*, edit the HTML, Save, pick it in the document's Print menu.
Copies live in the site database only; ask the developer to put a final version in the repo so every install gets it.
Page margins are set in `_style.html` (`.print-format { margin-... }`): the header/footer images run edge to edge, so left/right margins are 0 and
the content area has its own padding. The PDF engine (wkhtmltopdf) reads those margins from that CSS rule.
