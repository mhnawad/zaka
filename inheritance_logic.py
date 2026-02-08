from arabic_reshaper import reshape
from bidi.algorithm import get_display


def ar(text):
    """Display Arabic text correctly with reshaping and bidirectional support"""
    reshaped = reshape(text)
    return get_display(reshaped)


def calculate_inheritance(data):
    """
    Calculate Islamic inheritance distribution according to Sharia rules.
    
    Args:
        data: Dictionary with keys:
            - estate: Total amount to distribute
            - deceased_gender: 'ذكر' (male) or 'أنثى' (female)
            - husband: boolean
            - wives: number of wives
            - father: boolean
            - mother: boolean
            - sons: number of sons
            - daughters: number of daughters
            - brothers: number of brothers
            - sisters: number of sisters
            - grandfather: boolean
            - grandmother: boolean
            - halfbrothers_father: number of half-brothers from father
            - halfsisters_father: number of half-sisters from father
    
    Returns:
        Tuple of (shares_dict, explanation_list) where:
        - shares_dict: {heir_name: amount}
        - explanation_list: list of explanation strings with Quranic verses
    """
    
    shares = {}
    explanation = []
    estate = float(data.get('estate', 0))
    
    # Extract heir counts
    wives = int(data.get('wives', 0))
    husband = bool(data.get('husband', False))
    father = bool(data.get('father', False))
    mother = bool(data.get('mother', False))
    sons = int(data.get('sons', 0))
    daughters = int(data.get('daughters', 0))
    brothers = int(data.get('brothers', 0))
    sisters = int(data.get('sisters', 0))
    grandfather = bool(data.get('grandfather', False))
    grandmother = bool(data.get('grandmother', False))
    halfbrothers_father = int(data.get('halfbrothers_father', 0))
    halfsisters_father = int(data.get('halfsisters_father', 0))
    
    has_children = sons > 0 or daughters > 0
    has_siblings = brothers + sisters > 0
    
    explanation.append("📖 تفاصيل الحساب والآيات القرآنية:")
    explanation.append(f"💰 قيمة التركة الكاملة: {estate:,.2f}")
    explanation.append("=" * 50)
    
    # ==================== SPOUSE ====================
    if husband:
        if has_children:
            share = estate * (1 / 4)
            verse = "﴿فَلَكُمُ الرُّبُعُ مِمَّا تَرَكْنَ إِن كَانَ لَهُنَّ وَلَدٌ﴾ (النساء 12)"
            desc = "الربع (1/4)"
        else:
            share = estate * (1 / 2)
            verse = "﴿فَلَكُمْ نِصْفُ مَا تَرَكَ أَزْوَاجُكُمْ إِن لَّمْ يَكُن لَّهُنَّ وَلَدٌ﴾ (النساء 12)"
            desc = "النصف (1/2)"
        
        shares["الزوج"] = share
        explanation.append("")
        explanation.append(f"👨 الزوج: {desc} = {share:,.2f}")
        explanation.append(f"قال الله تعالى: {verse}")
    
    elif wives > 0:
        if has_children:
            share_total = estate * (1 / 8)
            verse = "﴿فَإِن كَانَ لَكُمْ وَلَدٌ فَلَهُنَّ الثُّمُنُ مِمَّا تَرَكْتُمْ﴾ (النساء 12)"
            desc = "الثمن (1/8)"
        else:
            share_total = estate * (1 / 4)
            verse = "﴿وَلَهُنَّ الرُّبُعُ مِمَّا تَرَكْتُمْ إِن لَّمْ يَكُن لَكُمْ وَلَدٌ﴾ (النساء 12)"
            desc = "الربع (1/4)"
        
        share_each = share_total / wives
        shares[f"الزوجات ({wives})"] = share_total
        explanation.append("")
        explanation.append(f"👩 الزوجات ({wives}): {desc} = {share_total:,.2f}")
        explanation.append(f"لكل زوجة: {share_each:,.2f}")
        explanation.append(f"قال الله تعالى: {verse}")
    
    # ==================== MOTHER ====================
    if mother:
        if has_children or has_siblings:
            # Mother gets 1/6 when children exist or 2+ siblings
            share = estate * (1 / 6)
            if has_children:
                verse = "﴿وَلِأَبَوَيْهِ لِكُلِّ وَاحِدٍ مِّنْهُمَا السُّدُسُ مِمَّا تَرَكَ إِن كَانَ لَهُ وَلَدٌ﴾ (النساء 11)"
            else:
                verse = "﴿فَإِن كَانَ لَهُ إِخْوَةٌ فَلِأُمِّهِ السُّدُسُ﴾ (النساء 11)"
            desc = "السدس (1/6)"
            shares["الأم"] = share
        else:
            # Mother gets 1/3 of remaining when no children and no siblings
            # This is calculated after spouse shares
            pass
    
    # ==================== FATHER ====================
    if father:
        if has_children:
            share = estate * (1 / 6)
            verse = "﴿وَلِأَبَوَيْهِ لِكُلِّ وَاحِدٍ مِّنْهُمَا السُّدُسُ مِمَّا تَرَكَ إِن كَانَ لَهُ وَلَدٌ﴾ (النساء 11)"
            desc = "السدس (1/6)"
            shares["الأب"] = share
            explanation.append("")
            explanation.append(f"👨 الأب: {desc} = {share:,.2f}")
            explanation.append(f"قال الله تعالى: {verse}")
        # Father becomes residuary when no children - will handle this after calculating other shares
    
    # Calculate amount already assigned to fixed share heirs
    assigned_total = sum(shares.values())
    remaining = estate - assigned_total
    
    # ==================== MOTHER (remaining case) ====================
    if mother and not has_children and not has_siblings:
        # Mother gets 1/3 of remaining (after spouse's fixed share)
        mother_share = remaining * (1 / 3)
        shares["الأم"] = mother_share
        explanation.append("")
        explanation.append(f"👩 الأم: الثلث من الباقي (1/3 من {remaining:,.2f}) = {mother_share:,.2f}")
        explanation.append("﴿فَإِن لَّمْ يَكُن لَّهُ وَلَدٌ وَوَرِثَهُ أَبَوَاهُ فَلِأُمِّهِ الثُّلُثُ﴾ (النساء 11)")
        remaining -= mother_share
    
    # ==================== CHILDREN (Asaba - تعصيب) ====================
    if has_children:
        # Children remain after fixed shares for parents/spouse
        # Calculate remaining for asaba distribution
        remaining_for_asaba = estate
        for heir, amount in shares.items():
            remaining_for_asaba -= amount
        
        # Distribute to children using 2:1 ratio for males
        total_units = sons * 2 + daughters
        if total_units > 0:
            unit_value = remaining_for_asaba / total_units
            
            if sons > 0:
                sons_share = unit_value * 2 * sons
                shares[f"الأبناء الذكور ({sons})"] = sons_share
                explanation.append("")
                explanation.append(f"👦 الأبناء الذكور ({sons}): تعصيب = {sons_share:,.2f}")
                explanation.append("لكل ابن ذكر حظ يساوي حظ أنثيين")
                explanation.append("﴿لِلذَّكَرِ مِثْلُ حَظِّ الْأُنثَيَيْنِ﴾ (النساء 11)")
            
            if daughters > 0:
                daughters_share = unit_value * daughters
                shares[f"البنات ({daughters})"] = daughters_share
                explanation.append("")
                explanation.append(f"👧 البنات ({daughters}): تعصيب = {daughters_share:,.2f}")
                explanation.append(f"لكل بنت: {unit_value:,.2f}")
                explanation.append("﴿لِلذَّكَرِ مِثْلُ حَظِّ الْأُنثَيَيْنِ﴾ (النساء 11)")
    
    # ==================== FATHER (Asaba - تعصيب when no children) ====================
    if father and not has_children:
        # Recalculate remaining after all fixed shares
        remaining_for_father = estate - sum(shares.values())
        if remaining_for_father > 0:
            shares["الأب"] = remaining_for_father
            explanation.append("")
            explanation.append(f"👨 الأب: تعصيب (الباقي) = {remaining_for_father:,.2f}")
            explanation.append("الأب يأخذ الباقي من التركة (تعصيب)")
            explanation.append("﴿يُوصِيكُمُ اللَّهُ فِي أَوْلَادِكُمْ﴾ (النساء 11)")
    
    # ==================== SIBLINGS (Kalala - كلالة) ====================
    if not father and not has_children and has_siblings:
        remaining_for_siblings = estate - sum(shares.values())
        
        if remaining_for_siblings > 0:
            # Brothers get 2x sisters (same 2:1 ratio)
            total_units = brothers * 2 + sisters
            if total_units > 0:
                unit_value = remaining_for_siblings / total_units
                
                if brothers > 0:
                    brothers_share = unit_value * 2 * brothers
                    shares[f"الإخوة ({brothers})"] = brothers_share
                    explanation.append("")
                    explanation.append(f"👨 الإخوة ({brothers}): كلالة = {brothers_share:,.2f}")
                    explanation.append("﴿وَإِن كَانَ رَجُلٌ يُورَثُ كَلَالَةً﴾ (النساء 12)")
                
                if sisters > 0:
                    sisters_share = unit_value * sisters
                    shares[f"الأخوات ({sisters})"] = sisters_share
                    explanation.append("")
                    explanation.append(f"👩 الأخوات ({sisters}): كلالة = {sisters_share:,.2f}")
                    explanation.append("﴿وَإِن كَانَ رَجُلٌ يُورَثُ كَلَالَةً﴾ (النساء 12)")
    
    # ==================== GRANDPARENTS & HALF-SIBLINGS ====================
    # (These would follow if mother/father not present, but simplified here)
    # Grandfather inherits as residuary if no father
    # Grandmother gets 1/6 if no mother and certain conditions
    # Half-siblings from father side only inherit if no full siblings and no father
    
    if grandfather and not father and not has_children:
        remaining_for_grandfather = estate - sum(shares.values())
        if remaining_for_grandfather > 0:
            shares["الجد"] = remaining_for_grandfather
            explanation.append("")
            explanation.append(f"👨 الجد: تعصيب (الباقي) = {remaining_for_grandfather:,.2f}")
    
    if grandmother and not mother and not has_children:
        # Grandmother gets 1/6 in certain conditions
        grandmother_share = estate * (1 / 6)
        shares["الجدة"] = grandmother_share
        explanation.append("")
        explanation.append(f"👵 الجدة: السدس (1/6) = {grandmother_share:,.2f}")
    
    # ==================== SUMMARY ====================
    explanation.append("")
    explanation.append("=" * 50)
    explanation.append("📊 ملخص التوزيع:")
    explanation.append("")
    
    total_distributed = sum(shares.values())
    for heir, amount in shares.items():
        percentage = (amount / estate * 100) if estate > 0 else 0
        explanation.append(f"{heir}: {amount:,.2f} ({percentage:.1f}%)")
    
    explanation.append("")
    explanation.append(f"إجمالي التوزيع: {total_distributed:,.2f}")
    
    if abs(total_distributed - estate) > 0.01:
        remaining_amount = estate - total_distributed
        explanation.append(f"⚠️ الباقي: {remaining_amount:,.2f}")
    
    return (shares, explanation)
