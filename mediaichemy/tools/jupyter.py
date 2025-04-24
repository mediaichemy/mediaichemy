import ipywidgets as widgets
from IPython.display import display
from typing import List, Dict
import logging
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import random

# Initialize logger
logger = logging.getLogger(__name__)


def display_ideas(ideas: List[Dict]) -> List[Dict[str, widgets.Checkbox]]:
    """
    Displays widgets for selecting ideas and their languages.

    Args:
        ideas (List[Dict]): A list of ideas to display.

    Returns:
        List[Dict[str, widgets.Checkbox]]: A list of dictionaries containing the main checkbox and language checkboxes.
    """
    selection_widgets: List[Dict[str, widgets.Checkbox]] = []
    container = widgets.VBox()

    for i, idea in enumerate(ideas):
        details_html = ""
        for key, value in idea.items():
            if key == "section" and isinstance(value, list):
                # Special handling for section array with timing data
                sections_html = "<br>".join([
                    f"[{s.get('start', 'N/A')}-{s.get('end', 'N/A')}] {s.get('text', '')}" 
                    for s in value
                ])
                value = sections_html
            elif isinstance(value, dict):
                value = "<br>".join(f"{k}: {v}" for k, v in value.items())
            elif isinstance(value, list) and value and not isinstance(value[0], dict):
                value = ", ".join(map(str, value))
            else:
                value = str(value)
            details_html += (f"<p><strong>{key.capitalize()}"
                             f":</strong><br>{value}</p>")

        idea_html = widgets.HTML(
            value=(
                f"<div style='padding: 10px; border: 1px solid #ccc;"
                " margin-bottom: 10px; "
                f"border-radius: 5px; background-color: #f9f9f9;'>"
                f"<h4 style='margin: 0;'>Idea {i + 1}</h4>"
                f"{details_html}"
                f"</div>"
            )
        )

        checkbox = widgets.Checkbox(
            value=False,
            description="",
            disabled=False,
            indent=False,
            layout=widgets.Layout(width="20px", height="20px")
        )

        styled_checkbox = widgets.HBox(
            [
                checkbox,
                widgets.HTML(
                    value=(
                        "<div style='background-color: #f3e8ff; "
                        "color: #5a189a; "
                        "font-size: 18px; padding: 5px 10px; "
                        "border-radius: 5px;'>"
                        "Generate Content"
                        "</div>"
                    )
                ),
            ],
            layout=widgets.Layout(align_items="center",
                                  justify_content="center", margin="10px")
        )

        idea_widget = widgets.VBox(
            [styled_checkbox, idea_html],
            layout=widgets.Layout(align_items="center", margin="10px")
        )

        language_checkboxes = {}
        if "languages" in idea and isinstance(idea["languages"], list):
            language_checkboxes_container = widgets.VBox(
                layout=widgets.Layout(margin="10px")
            )
            language_checkboxes_label = widgets.HTML(
                value="<strong>Select Languages:</strong>"
            )
            language_checkboxes_widgets = []
            for language in idea["languages"]:
                language_checkbox = widgets.Checkbox(
                    value=False,
                    description=language,
                    disabled=False,
                    indent=False,
                    layout=widgets.Layout(width="auto")
                )
                language_checkboxes[language] = language_checkbox
                language_checkboxes_widgets.append(language_checkbox)

            (language_checkboxes_container
                .children) = ([language_checkboxes_label] +
                              language_checkboxes_widgets)
            container.children += (idea_widget,
                                   language_checkboxes_container)
        else:
            container.children += (idea_widget,)

        selection_widgets.append({"main_checkbox":
                                  checkbox,
                                  "language_checkboxes":
                                  language_checkboxes})

    display(container)
    return selection_widgets


def select_ideas(
    ideas: List[Dict],
    selection_widgets: List[Dict[str, widgets.Checkbox]]
) -> List[Dict]:
    """
    Filters ideas based on selected checkboxes.

    Args:
        ideas (List[Dict]): The list of ideas to filter.
        selection_widgets (List[Dict[str, widgets.Checkbox]]):
        List of dictionaries containing the main checkbox and language checkboxes.

    Returns:
        List[Dict]: A list of selected ideas with filtered languages.
    """
    selected_ideas = []

    for idea, widgets_dict in zip(ideas, selection_widgets):
        if widgets_dict["main_checkbox"].value:
            # Check if this idea has language checkboxes
            if widgets_dict["language_checkboxes"]:
                selected_languages = [
                    lang for lang,
                    checkbox in widgets_dict["language_checkboxes"].items()
                    if checkbox.value
                ]

                # If no languages are selected but the main checkbox is, 
                # include all available languages
                if not selected_languages and "languages" in idea:
                    selected_languages = idea["languages"]

                filtered_idea = idea.copy()
                for key, value in filtered_idea.items():
                    if isinstance(value, dict):
                        filtered_idea[key] = {
                            lang: text for lang, text in value.items()
                            if lang in selected_languages
                        }

                if "languages" in filtered_idea and isinstance(
                        filtered_idea["languages"], list):
                    filtered_idea["languages"] = [
                        lang for lang in filtered_idea["languages"]
                        if lang in selected_languages
                    ]

                selected_ideas.append(filtered_idea)
            else:
                # For ideas without language checkboxes, just include the entire idea
                selected_ideas.append(idea.copy())

    return selected_ideas


def show_font_samples(sample_text="AaBbCcDd 123 !?", num_fonts=None, font_size=16):
    """
    Displays visual samples of available fonts with their names.

    Parameters:
    -----------
    sample_text : str
        Text to display in each font sample
    num_fonts : int
        Number of fonts to display (set to None to show all fonts)
    font_size : int
        Size of the font in the sample
    """

    # Get all font files on the system
    font_files = fm.findSystemFonts()
    font_props = []

    # Extract font properties
    for font_file in font_files:
        try:
            font = fm.FontProperties(fname=font_file)
            name = font.get_name()
            if name:  # Some fonts might not have names
                font_props.append((name, font))
        except Exception:
            continue

    # Sort by name and limit to num_fonts if specified
    font_props = sorted(font_props, key=lambda x: x[0])
    if num_fonts is not None and num_fonts < len(font_props):
        # Get a random sample if there are too many
        font_props = random.sample(font_props, num_fonts)

    # Set up the plot
    n_fonts = len(font_props)
    cols = 2
    rows = int(np.ceil(n_fonts / cols))

    fig, axs = plt.subplots(rows, cols, figsize=(14, rows * 1.5))
    fig.suptitle("Font Samples", fontsize=16)
    axs = axs.flatten()

    # Display each font
    for i, (name, font) in enumerate(font_props):
        if i < len(axs):
            ax = axs[i]
            ax.text(0.5, 0.5, sample_text, fontproperties=font, fontsize=font_size,
                    ha='center', va='center')
            ax.set_title(name, fontsize=10)
            ax.axis('off')

    # Hide unused subplots
    for i in range(n_fonts, len(axs)):
        axs[i].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust layout to make room for suptitle
    plt.show()

    return [name for name, _ in font_props]
