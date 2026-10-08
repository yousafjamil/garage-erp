GARAGE_HOME = "desk/garage-management/garage"
MY_JOBS = "desk/repair-job"
OFFICE_ROLES = {"Garage Owner", "Garage Manager", "Receptionist", "System Manager", "Accounts User", "Accounts Manager"}


def get_home(user):
    """Signed-in users land on the Garage page; technicians land straight on their job list."""
    import frappe
    if not user or user == "Guest":
        return None
    roles = set(frappe.get_roles(user))
    return MY_JOBS if "Technician" in roles and not roles & OFFICE_ROLES else GARAGE_HOME
