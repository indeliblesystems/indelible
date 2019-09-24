"""Aggregate orders into daily revenue."""

from indelible_log import Cmd

def sync(orders, daily_revenue):
    """Update daily_revenue totals to reflect any orders changed since the last
    time we ran."""

    # Sync the current daily_revenue log locally.
    latest = {}
    version_diff = daily_revenue.version_diff(from_version=0)
    current_daily_revenue_version = version_diff.to_version
    for change in version_diff.changes():
        entry = change["entry"]
        latest[entry["key"]] = entry["value"]
    if "orders_version" not in latest:
        orders_starting_point = 0
    else:
        orders_starting_point = int(latest["orders_version"])

    # For each changed order, figure how much daily revenue is changed.
    adjustments = {}
    print("daily_revenue last processed orders to source version %d" % orders_starting_point)
    orders_version_diff = orders.version_diff(orders_starting_point)
    if orders_starting_point == orders_version_diff.to_version:
        print("no new orders, nothing to do")
        return
    for change in orders_version_diff.changes():
        entry = change["entry"]
        order_key = entry["key"]
        order = entry["value"]
        if "date" not in order:
            raise ValueError("order '%s' does not contain a date" % order_key)
        date = order["date"]
        if date not in adjustments:
            adjustments[date] = 0
        if "revenue" not in order:
            raise ValueError("order '%s' does not contain a revenue value" % order_key)
        revenue = order["revenue"]
        if change["change"] == "Add":
            adjustment = revenue
        elif change["change"] == "Remove":
            adjustment = -revenue
        print("order %s represents an adjustment of revenue for %s by %d" % 
            (order_key, date, adjustment))
        adjustments[date] += adjustment

    # Persist the totals.
    commands = [
        Cmd.ExpectVersion(current_daily_revenue_version),
        Cmd.Upsert("orders_version", orders_version_diff.to_version)
    ]
    for date in adjustments:
        if date in latest:
            new = latest[date] + adjustments[date]
        else:
            new = adjustments[date]
        commands.append(Cmd.Upsert(date, new))
    daily_revenue.update(commands)

    print("daily_revenue log now reflects orders up to source version %d"\
          % orders_version_diff.to_version)
