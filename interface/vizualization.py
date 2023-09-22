import gradio as gr
import pandas as pd
import matplotlib

matplotlib.use("agg")
from matplotlib import pyplot as plt
import requests


def read_distrubtion_per_source():
    url = "http://127.0.0.1:8000/articles/get-distribution-fake-real-per-source"
    response = requests.get(url)
    return response.json()


def plot_distribution(df, metadata_element):
    fig = plt.figure(figsize=(10, 6))
    select_fake_data = f"sum_of_fake_{metadata_element.lower()}"
    select_real_data = f"sum_of_real_{metadata_element.lower()}"
    plt.bar(
        df["article_source"],
        df[select_fake_data],
        label=f"Fake {metadata_element}",
        alpha=0.7,
    )
    plt.bar(
        df["article_source"],
        df[select_real_data],
        bottom=df[select_fake_data],
        label=f"Real {metadata_element}",
        alpha=0.7,
    )
    plt.xlabel("Article Source")
    plt.ylabel(f"Number of {metadata_element}")
    plt.title("Distribution of Fake and Real Titles per Article Source")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    return fig


def make_plot(metadata_to_display):
    return plot_distribution(data, metadata_to_display)


def launch_web_interface():
    with gr.Blocks() as dashboard:
        button = gr.Radio(
            label="Metadata Element",
            choices=["Titles", "Descriptions", "Contents"],
            value="Titles",
        )
        plot = gr.Plot(label="Plot")
        button.change(make_plot, inputs=[button], outputs=[plot])
    dashboard.launch()


if __name__ == "__main__":
    request_data = read_distrubtion_per_source()
    data = pd.DataFrame(request_data)
    launch_web_interface()
