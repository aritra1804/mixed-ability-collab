import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_velocity_distribution_with_thresholds(gaze_csv_path, thresholds=[0.1, 0.15, 0.2, 0.3]):
    """
    Plots histogram of gaze velocity and overlays multiple threshold lines.
    """
    # Load gaze data
    df = pd.read_csv(gaze_csv_path)

    # Compute velocity if not already present
    if 'velocity' not in df.columns:
        df['dx'] = df['x'].diff()
        df['dy'] = df['y'].diff()
        df['dt'] = df['timestamp'].diff()
        df['velocity'] = (df['dx']**2 + df['dy']**2)**0.5 / df['dt']
        df['velocity'].fillna(0, inplace=True)

    # Plot histogram and KDE
    plt.figure(figsize=(12, 6))
    sns.histplot(df['velocity'], bins=100, kde=True, color='blue', alpha=0.6)

    # Add vertical lines for each threshold
    for v in thresholds:
        plt.axvline(v, linestyle='-', linewidth=2, label=f'Threshold = {v}')

    plt.title('Velocity Distribution of Gaze Data with Multiple Thresholds')
    plt.xlabel('Velocity (Normalized units / sec)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.show()


def fixation_counts_by_threshold(gaze_csv_path, thresholds=[0.1, 0.15, 0.2, 0.3]):
    df = pd.read_csv(gaze_csv_path)

    if 'velocity' not in df.columns:
        df['dx'] = df['x'].diff()
        df['dy'] = df['y'].diff()
        df['dt'] = df['timestamp'].diff()
        df['velocity'] = (df['dx']**2 + df['dy']**2)**0.5 / df['dt']
        df['velocity'].fillna(0, inplace=True)

    print("Fixation Counts at Different Thresholds:\n")

    for v in thresholds:
        fixations = df[df['velocity'] < v]
        print(f"Threshold = {v} → Fixation Points: {len(fixations)} / {len(df)} total")



plot_velocity_distribution_with_thresholds("output/gaze_data_20250415_123855.csv")

fixation_counts_by_threshold("output/gaze_data_20250415_123855.csv")
