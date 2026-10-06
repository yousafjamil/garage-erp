def customer_dashboard(data):
    data["transactions"].append({"label": "Garage", "items": ["Garage Vehicle", "Repair Job", "Vehicle Check-In"]})
    return data
