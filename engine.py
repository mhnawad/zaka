def has_descendants(d):
    return (
        d["sons"] or d["daughters"] or
        d["son_sons"] or d["son_daughters"]
    )

def calculate(data):
    estate = data["estate"]
    shares = {}
    fixed = 0

    # ===== الزوج =====
    if data["husband"]:
        s = 1/4 if has_descendants(data) else 1/2
        shares["الزوج"] = s
        fixed += s

    # ===== الزوجات =====
    if data["wives"] > 0:
        s = 1/8 if has_descendants(data) else 1/4
        shares["الزوجات"] = s
        fixed += s

    # ===== الأم =====
    if data["mother"]:
        if has_descendants(data) or data["brothers"] + data["sisters"] >= 2:
            s = 1/6
        else:
            s = 1/3
        shares["الأم"] = s
        fixed += s

    # ===== الجدة =====
    if data["grandmother"] and not data["mother"]:
        shares["الجدة"] = 1/6
        fixed += 1/6

    # ===== الأب =====
    father_asaba = False
    if data["father"]:
        if has_descendants(data):
            shares["الأب"] = 1/6
            fixed += 1/6
        else:
            father_asaba = True

    # ===== الإخوة لأم =====
    if not has_descendants(data) and not data["father"]:
        total = data["brothers_mother"] + data["sisters_mother"]
        if total == 1:
            shares["إخوة لأم"] = 1/6
            fixed += 1/6
        elif total > 1:
            shares["إخوة لأم"] = 1/3
            fixed += 1/3

    # ===== العَول =====
    if fixed > 1:
        for k in shares:
            shares[k] = shares[k] / fixed
        fixed = 1

    remainder = 1 - fixed

    # ===== الأب عصبة =====
    if father_asaba:
        shares["الأب"] = remainder
        remainder = 0

    # ===== الفروع عصبة =====
    units = (
        data["sons"] * 2 +
        data["daughters"] +
        data["son_sons"] * 2 +
        data["son_daughters"]
    )

    if units > 0:
        unit = remainder / units
        if data["sons"]:
            shares["الابن"] = unit * 2 * data["sons"]
        if data["daughters"]:
            shares["البنت"] = unit * data["daughters"]
        if data["son_sons"]:
            shares["ابن الابن"] = unit * 2 * data["son_sons"]
        if data["son_daughters"]:
            shares["بنت الابن"] = unit * data["son_daughters"]
        remainder = 0

    # ===== الإخوة عصبة (إن لم يوجد أب ولا فروع) =====
    if remainder > 0 and not has_descendants(data) and not data["father"]:
        units = data["brothers"] * 2 + data["sisters"]
        if units:
            unit = remainder / units
            if data["brothers"]:
                shares["الأخ"] = unit * 2 * data["brothers"]
            if data["sisters"]:
                shares["الأخت"] = unit * data["sisters"]
            remainder = 0

    # ===== الرد =====
    if remainder > 0:
        total = sum(shares.values())
        for k in shares:
            shares[k] += shares[k] / total * remainder

    return {k: round(v * estate, 2) for k, v in shares.items()}
