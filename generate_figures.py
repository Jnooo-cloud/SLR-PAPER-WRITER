import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_figures():
    # Create images directory
    if not os.path.exists("images"):
        os.makedirs("images")

    # Load data
    try:
        df = pd.read_csv("slr_results_final.csv")
    except FileNotFoundError:
        print("Error: slr_results_final.csv not found.")
        return

    # Set style
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 12, 'font.family': 'sans-serif'})

    # --- Figure 1: Publications by Year ---
    plt.figure(figsize=(10, 6))
    year_counts = df['Year'].value_counts().sort_index()
    sns.barplot(x=year_counts.index, y=year_counts.values, palette="viridis")
    plt.title("Distribution of Included Studies by Year", fontsize=16)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Number of Studies", fontsize=14)
    plt.tight_layout()
    plt.savefig("images/figure_1_year_distribution.png", dpi=300)
    print("Generated images/figure_1_year_distribution.png")
    plt.close()

    # --- Figure 2: Mechanism Distribution ---
    # Assuming 'Mechanism' column exists. If not, we might need to infer or skip.
    # Let's check columns. If 'Mechanism' is missing, we skip.
    if 'Mechanism' in df.columns:
        plt.figure(figsize=(8, 8))
        mech_counts = df['Mechanism'].value_counts()
        plt.pie(mech_counts.values, labels=mech_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
        plt.title("Distribution of Self-Improvement Mechanisms", fontsize=16)
        plt.tight_layout()
        plt.savefig("images/figure_2_mechanism_distribution.png", dpi=300)
        print("Generated images/figure_2_mechanism_distribution.png")
        plt.close()
    else:
        print("Warning: 'Mechanism' column not found. Skipping Figure 2.")

    # --- Figure 3: Venue Distribution (Top 10) ---
    if 'Venue' in df.columns:
        plt.figure(figsize=(12, 8))
        venue_counts = df['Venue'].value_counts().head(10)
        sns.barplot(y=venue_counts.index, x=venue_counts.values, palette="rocket")
        plt.title("Top Venues for LLM Self-Improvement Research", fontsize=16)
        plt.xlabel("Number of Studies", fontsize=14)
        plt.ylabel("Venue", fontsize=14)
        plt.tight_layout()
        plt.savefig("images/figure_3_venue_distribution.png", dpi=300)
        print("Generated images/figure_3_venue_distribution.png")
        plt.close()

if __name__ == "__main__":
    generate_figures()
