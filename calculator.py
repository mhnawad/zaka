from rules import fixed_shares

def calculate(data):
    estate = data["estate"]
    ratios = fixed_shares(data)

    used = sum(ratios.values())
    results = {}

    # Awl
    if used > 1:
        for k in ratios:
            ratios[k] /= used

    remaining = estate

    # Fixed shares
    for k, v in ratios.items():
        results[k] = estate * v
        remaining -= results[k]

    # If mother exists but was not allocated a fixed share (i.e., rules didn't give 1/6),
    # and there are no children, she takes one-third of the remaining after fixed shares.
    if data.get("mother") and "الأم" not in results:
        # allocate one-third of the remaining
        mother_amount = remaining * (1/3)
        results["الأم"] = mother_amount
        remaining -= mother_amount

    # Asaba (sons & daughters)
    units = data["sons"] * 2 + data["daughters"]
    if units > 0:
        unit_value = remaining / units
        if data["sons"]:
            results["الأبناء"] = data["sons"] * unit_value * 2
        if data["daughters"]:
            results["البنات"] = data["daughters"] * unit_value
        remaining = 0

    # If there are no children and father exists, father takes the remaining (residuary)
    if remaining > 0 and units == 0:
        if data.get("father"):
            results["الأب"] = results.get("الأب", 0) + remaining
            remaining = 0
        else:
            # Radd: distribute remaining proportionally among existing heirs
            total = sum(results.values())
            if total > 0:
                for k in list(results.keys()):
                    results[k] += (results[k] / total) * remaining
                remaining = 0

    return results
