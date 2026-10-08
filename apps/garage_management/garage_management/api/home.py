GARAGE_HOME = "desk/garage-management/garage"


def get_home(user):
    """Signed-in users land on the Garage page instead of the app launcher."""
    return GARAGE_HOME if user and user != "Guest" else None
