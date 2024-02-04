import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_model_threshold_plots(
    base_file_name,
    model_plots_folder,
    train_threshold_list,
    train_accuracy_list,
    train_number_of_flagged_players,
    best_threshold,
    time_control,
    rating_bin_key,
):
    """Generate model threshold plots showing accuracy and number of players vs model threshold(s)."""

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=train_threshold_list, y=train_accuracy_list, name="Accuracy vs Threshold"
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=train_threshold_list,
            y=train_number_of_flagged_players,
            name="Number of Flagged Players",
        ),
        secondary_y=True,
    )
    fig.add_vline(
        x=best_threshold,
        line_width=2,
        line_dash="dash",
        line_color="green",
        annotation_text="Best Threshold",
    )
    fig.update_layout(
        title=f"Accuracy vs Threshold for {time_control}: Rating Bin {rating_bin_key}",
        xaxis_title="Threshold",
        yaxis_title="Accuracy",
        yaxis2_title="Number of Flagged Players",
        yaxis_range=[0, 1],
    )
    if not os.path.exists(model_plots_folder):
        os.mkdir(model_plots_folder)
    fig.write_html(
        f"{model_plots_folder}/{base_file_name}_model_thresholds_{time_control}_{rating_bin_key}.html"
    )
