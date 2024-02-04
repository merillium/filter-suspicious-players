import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_model_threshold_plots(
    BASE_FILE_NAME,
    MODEL_PLOTS_FOLDER,
    train_threshold_list,
    train_accuracy_list,
    train_number_of_flagged_players,
    best_threshold,
    time_control,
    rating_bin_key,
):
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
    if not os.path.exists(MODEL_PLOTS_FOLDER):
        os.mkdir(MODEL_PLOTS_FOLDER)
    fig.write_html(
        f"{MODEL_PLOTS_FOLDER}/{BASE_FILE_NAME}_model_thresholds_{time_control}_{rating_bin_key}.html"
    )
