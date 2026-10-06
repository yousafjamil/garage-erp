"""Development-only helpers (not run automatically)."""
import frappe


def configure_dev_mailpit():
    """Route outgoing mail to the local Mailpit container (UI: http://localhost:8026)."""
    name = "Local Mailpit"
    doc = frappe.get_doc("Email Account", name) if frappe.db.exists("Email Account", name) else frappe.new_doc("Email Account")
    doc.update({"email_account_name": name, "email_id": "garage@garage.localhost", "enable_outgoing": 1,
                "default_outgoing": 1, "smtp_server": "mailpit", "smtp_port": 1025, "use_tls": 0, "use_ssl": 0,
                "no_smtp_authentication": 1, "always_use_account_email_id_as_sender": 1})
    doc.save(ignore_permissions=True)
    frappe.db.commit()
