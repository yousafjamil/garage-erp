# Print formats

Five formats, each with a **Garage** and a **Transport** layout chosen by the company's *Print Style*: Quotation Print, Tax Invoice Print,
Job Card Print, Statement Print, Receipt Print. Sources: `apps/garage_management/garage_management/print_formats/*.html`
(`_base.html` macros and CSS, `_tail.html` signatures and footer). `setup/print_formats.py` installs them on every `migrate`.

- Letterhead/footer images are per company (`public/images`, Letter Head records created by `setup/companies.py`).
- Company defaults editable in *Company*: bank details, quotation VAT wording, quotation note, invoice note.
- Page margins: top/bottom are fields on the Print Format record (8 / 64 mm, to leave room for the footer image); left/right are CSS (0, edge-to-edge letterhead). A CSS top/bottom margin would be counted twice and create a blank second page.
- Keep a document on one page: the invoice/quotation templates pad the table with blank rows (`fill`) depending on the number of lines.
- Check the output with `tests/simple_scenario.py` (writes PDFs to `/tmp/s_*.pdf`).
