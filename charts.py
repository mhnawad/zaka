# charts.py
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib import rcParams

rcParams["font.family"] = "DejaVu Sans"

def ar(text):
    """Fix Arabic shaping + RTL"""
    return get_display(arabic_reshaper.reshape(text))

def generate_pie_chart(results, filename="chart.png"):
    labels = [ar(k) for k in results.keys()]
    sizes = list(results.values())

    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90
    )
    plt.title(ar("توزيع التركة"))
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
