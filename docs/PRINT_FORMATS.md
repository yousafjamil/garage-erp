# Print formats

Five formats, each with a **Garage** and a **Transport** layout chosen by the company's *Print Style*: Quotation Print, Tax Invoice Print,
Job Card Print, Statement Print, Receipt Print. Sources: `apps/garage_management/garage_management/print_formats/*.html`
(`_base.html` macros and CSS, `_tail.html` signatures and footer). `setup/print_formats.py` installs them on every `migrate`.

- Letterhead/footer images are per company (`public/images`, Letter Head records created by `setup/companies.py`).
- Company defaults editable in *Company*: bank details, quotation VAT wording, quotation note, invoice note.
- Page margins: top/bottom are fields on the Print Format record (8 / 64 mm, to leave room for the footer image); left/right are CSS (0, edge-to-edge letterhead). A CSS top/bottom margin would be counted twice and create a blank second page.
- Keep a document on one page: the invoice/quotation templates pad the table with blank rows (`fill`) depending on the number of lines.
- Check the output with `tests/simple_scenario.py` (writes PDFs to `/tmp/s_*.pdf`).

## PDF engine (wkhtmltopdf is deprecated in Frappe 17)
All five formats use **Chrome** (`pdf_generator = chrome`, headless Chromium that ships in the ERPNext image; `chromium_path` is set in `common_site_config.json`).
- Chrome takes the letterhead from `#header-html` and the footer from `#footer-html`, so they repeat on every page of a long document and the top margin is 0. `_base.html` writes the letterhead into `#header-html` only when the engine is Chrome (it reads `frappe.form_dict.pdf_generator`), and inline otherwise.
- Frappe's `download_pdf` endpoint ignores the format's own setting unless `pdf_generator` is passed; our *Download PDF* button passes the format's engine.
- Chrome needs memory (about 1 GB free) and stalls after 2-3 PDFs in the free 512 MB Render demo. With `LITE=1` the start-up step `setup.install.refresh_ui` switches the formats back to wkhtmltopdf (top margin 8 mm). Both engines were checked: every sample document prints on one page.
