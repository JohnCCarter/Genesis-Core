"""
Visualization utilities for model comparison and champion selection.

Provides radar charts and other visualizations to compare models across
multiple performance dimensions.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def create_radar_chart(
    models_data: dict[str, dict[str, float]],
    metrics: list[str],
    output_path: Path | None = None,
    title: str = "Model Comparison",
    figsize: tuple[int, int] = (12, 8),
) -> plt.Figure:
    """
    Create radar chart comparing multiple models across metrics.

    Args:
        models_data: Dict mapping model names to their metric values
        metrics: List of metric names to display
        output_path: Optional path to save figure
        title: Chart title
        figsize: Figure size (width, height)

    Returns:
        Matplotlib Figure object

    Example:
        >>> models = {
        ...     "model_a": {"auc": 0.8, "sharpe": 1.5, "profit": 2.0},
        ...     "model_b": {"auc": 0.75, "sharpe": 1.2, "profit": 1.8}
        ... }
        >>> fig = create_radar_chart(models, ["auc", "sharpe", "profit"])
    """
    num_models = len(models_data)
    num_metrics = len(metrics)

    if num_models == 0:
        raise ValueError("No models to visualize")
    if num_metrics < 3:
        raise ValueError("Need at least 3 metrics for radar chart")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": "polar"})

    # Angles for each metric
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    # Colors for different models
    colors = plt.cm.Set2(np.linspace(0, 1, num_models))

    # Plot each model
    for idx, (model_name, metrics_dict) in enumerate(models_data.items()):
        # Extract values for specified metrics
        values = [metrics_dict.get(metric, 0.0) for metric in metrics]
        values += values[:1]  # Complete the circle

        # Plot
        ax.plot(
            angles,
            values,
            "o-",
            linewidth=2,
            label=model_name,
            color=colors[idx],
            markersize=8,
        )
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, size=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], size=8)
    ax.set_title(title, size=14, weight="bold", pad=20)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def create_comparison_bars(
    ranking_df: pd.DataFrame,
    metric_columns: list[str],
    output_path: Path | None = None,
    title: str = "Model Metrics Comparison",
    figsize: tuple[int, int] = (14, 8),
) -> plt.Figure:
    """
    Create grouped bar chart comparing models across metrics.

    Args:
        ranking_df: DataFrame with model rankings and metrics
        metric_columns: List of metric column names to compare
        output_path: Optional path to save figure
        title: Chart title
        figsize: Figure size (width, height)

    Returns:
        Matplotlib Figure object
    """
    if len(ranking_df) == 0:
        raise ValueError("Empty ranking DataFrame")

    num_models = len(ranking_df)
    num_metrics = len(metric_columns)

    # Create figure with subplots
    fig, axes = plt.subplots(1, num_metrics, figsize=figsize, sharey=True)

    if num_metrics == 1:
        axes = [axes]

    # Color map
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, num_models))

    for idx, metric in enumerate(metric_columns):
        ax = axes[idx]

        # Get values
        models = ranking_df["model"].tolist()
        values = ranking_df[metric].tolist()

        # Create bars
        bars = ax.bar(range(num_models), values, color=colors, alpha=0.8, edgecolor="black")

        # Customize
        ax.set_title(metric.replace("_", " ").title(), fontsize=11, weight="bold")
        ax.set_xticks(range(num_models))
        ax.set_xticklabels(models, rotation=45, ha="right", fontsize=9)
        ax.grid(True, axis="y", linestyle="--", alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, values, strict=True):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    # Overall title
    fig.suptitle(title, fontsize=14, weight="bold", y=1.02)
    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def create_champion_summary(
    ranking_df: pd.DataFrame,
    weights: dict[str, float],
    champion_name: str,
    output_path: Path | None = None,
    figsize: tuple[int, int] = (14, 10),
) -> plt.Figure:
    """
    Create comprehensive summary visualization for champion selection.

    Combines radar chart and bar charts in a single figure.

    Args:
        ranking_df: DataFrame with model rankings
        weights: Dict of metric weights used
        champion_name: Name of the winning champion
        output_path: Optional path to save figure
        figsize: Figure size (width, height)

    Returns:
        Matplotlib Figure object
    """
    if len(ranking_df) == 0:
        raise ValueError("Empty ranking DataFrame")

    # Create figure with custom layout
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1], hspace=0.3, wspace=0.3)

    # 1. Radar chart (top-left, spans 2 columns)
    ax_radar = fig.add_subplot(gs[0, :], projection="polar")

    # Prepare data for radar chart (normalized metrics)
    metrics_for_radar = list(weights.keys())
    num_metrics = len(metrics_for_radar)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]

    colors = plt.cm.Set2(np.linspace(0, 1, len(ranking_df)))

    for idx, row in ranking_df.iterrows():
        model_name = row["model"]
        values = [row[metric] for metric in metrics_for_radar]

        # Normalize values to 0-1 for radar
        # (assuming they're already in reasonable ranges)
        values += values[:1]

        is_champion = model_name == champion_name
        linewidth = 3 if is_champion else 1.5
        alpha_fill = 0.3 if is_champion else 0.1
        markersize = 10 if is_champion else 6

        ax_radar.plot(
            angles,
            values,
            "o-",
            linewidth=linewidth,
            label=model_name,
            color=colors[idx],
            markersize=markersize,
        )
        ax_radar.fill(angles, values, alpha=alpha_fill, color=colors[idx])

    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels([m.replace("_", " ").title() for m in metrics_for_radar], size=9)
    ax_radar.set_title("Performance Across All Metrics", size=12, weight="bold", pad=15)
    ax_radar.grid(True, linestyle="--", alpha=0.7)
    ax_radar.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=9)

    # 2. Total scores bar chart (bottom-left)
    ax_scores = fig.add_subplot(gs[1, 0])

    models = ranking_df["model"].tolist()
    scores = ranking_df["total_score"].tolist()
    colors_scores = ["gold" if m == champion_name else "skyblue" for m in models]

    bars = ax_scores.barh(
        range(len(models)), scores, color=colors_scores, alpha=0.8, edgecolor="black"
    )
    ax_scores.set_yticks(range(len(models)))
    ax_scores.set_yticklabels(models, fontsize=9)
    ax_scores.set_xlabel("Total Score (0-10)", fontsize=10)
    ax_scores.set_title("Overall Ranking", size=11, weight="bold")
    ax_scores.grid(True, axis="x", linestyle="--", alpha=0.3)
    ax_scores.set_xlim(0, 10)

    # Add score labels
    for bar, score in zip(bars, scores, strict=True):
        width = bar.get_width()
        ax_scores.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f"  {score:.2f}",
            ha="left",
            va="center",
            fontsize=9,
            weight="bold",
        )

    # 3. Weights pie chart (bottom-right)
    ax_weights = fig.add_subplot(gs[1, 1])

    weight_labels = [m.replace("_", " ").title() for m in weights.keys()]
    weight_values = list(weights.values())
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(weights)))

    wedges, texts, autotexts = ax_weights.pie(
        weight_values,
        labels=weight_labels,
        autopct="%1.0f%%",
        startangle=90,
        colors=colors_pie,
        textprops={"fontsize": 9},
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_weight("bold")

    ax_weights.set_title("Evaluation Weights", size=11, weight="bold")

    # Overall title
    fig.suptitle(
        f"🏆 Champion Selection Report - Winner: {champion_name}",
        fontsize=15,
        weight="bold",
        y=0.98,
    )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def create_metric_heatmap(
    ranking_df: pd.DataFrame,
    metric_columns: list[str],
    output_path: Path | None = None,
    title: str = "Model Metrics Heatmap",
    figsize: tuple[int, int] = (12, 6),
) -> plt.Figure:
    """
    Create heatmap showing all models and metrics.

    Args:
        ranking_df: DataFrame with model rankings
        metric_columns: List of metric columns to include
        output_path: Optional path to save figure
        title: Chart title
        figsize: Figure size (width, height)

    Returns:
        Matplotlib Figure object
    """
    if len(ranking_df) == 0:
        raise ValueError("Empty ranking DataFrame")

    # Extract data
    models = ranking_df["model"].tolist()
    data = ranking_df[metric_columns].values

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    im = ax.imshow(data, cmap="YlGnBu", aspect="auto", vmin=0, vmax=1)

    # Customize
    ax.set_xticks(range(len(metric_columns)))
    ax.set_xticklabels(
        [m.replace("_", " ").title() for m in metric_columns], rotation=45, ha="right"
    )
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models)
    ax.set_title(title, fontsize=13, weight="bold", pad=15)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Normalized Value", rotation=270, labelpad=20)

    # Add text annotations
    for i in range(len(models)):
        for j in range(len(metric_columns)):
            ax.text(
                j,
                i,
                f"{data[i, j]:.2f}",
                ha="center",
                va="center",
                color="white" if data[i, j] > 0.5 else "black",
                fontsize=9,
            )

    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig
