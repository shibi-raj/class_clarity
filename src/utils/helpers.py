# Example: date formatting, sorting by priority
def sort_events_by_priority(events):
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    return sorted(events, key=lambda x: priority_order.get(x.get("priority", "Low")))