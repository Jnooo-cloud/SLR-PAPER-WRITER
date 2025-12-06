import json
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_mechanism_figure():
    if not os.path.exists("images"):
        os.makedirs("images")

    try:
        with open("slr_extracted_data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: slr_extracted_data.json not found.")
        return

    mechanisms = []
    for item in data:
        try:
            mech_type = item.get("data", {}).get("mechanism", {}).get("type", "Unknown")
            mechanisms.append(mech_type)
        except:
            continue

    if not mechanisms:
        print("No mechanism data found.")
        return

    # Count frequencies
    from collections import Counter
    counts = Counter(mechanisms)
    
    labels = list(counts.keys())
    sizes = list(counts.values())

    # Plot
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title("Distribution of Self-Improvement Mechanisms", fontsize=16)
    plt.tight_layout()
    plt.savefig("images/figure_2_mechanism_distribution.png", dpi=300)
    print("Generated images/figure_2_mechanism_distribution.png")
    plt.close()

if __name__ == "__main__":
    generate_mechanism_figure()
