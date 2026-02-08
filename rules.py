def fixed_shares(data):
    shares = {}

    # Husband
    if data["husband"]:
        shares["الزوج"] = 0.25 if (data["sons"] or data["daughters"]) else 0.5

    # Wives
    if data["wives"] > 0:
        shares["الزوجات"] = 0.125 if (data["sons"] or data["daughters"]) else 0.25

    # Mother
    if data["mother"]:
        # mother takes 1/6 as a fixed share when there are children or 2+ siblings
        if data["sons"] or data["daughters"] or (data["brothers"] + data["sisters"] >= 2):
            shares["الأم"] = 1/6
        # otherwise mother's one-third is handled later (one-third of remaining after fixed shares)

    # Father: fixed 1/6 only if there are children (otherwise residuary)
    if data["father"] and (data["sons"] or data["daughters"]):
        shares["الأب"] = 1/6

    return shares
