import base64
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas


def main():
    # Initialize session state
    if "button_id" not in st.session_state:
        st.session_state["button_id"] = ""
    if "color_to_label" not in st.session_state:
        st.session_state["color_to_label"] = {}

    PAGES = {"Projet": full_app}
    page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    PAGES[page]()


def _get_image_url(uploaded_file):
    """
    Convert an uploaded file to a data URI for use as a background_image in st_canvas.
    """
    img_bytes = uploaded_file.read()
    mime = uploaded_file.type  # e.g. 'image/png'
    b64 = base64.b64encode(img_bytes).decode()
    return f"data:{mime};base64,{b64}"


def full_app():
    st.sidebar.header("Configuration")

    icon_dict = {
        "transform": "Move",
        "freedraw":  "Pencil",
        "line":      "Line",
        "rect":      "Rectangle",
        "circle":    "Cercle",
        "polygon":   "Polygon",
        "point":     "Point",
    }

    if "drawing_mode" not in st.session_state:
        st.session_state.drawing_mode = "freedraw"

    transform_col = st.sidebar.columns(1, gap="small")[0]
    if transform_col.button(
        icon_dict['transform'],
        key="btn_transform",
        use_container_width=True
    ):
        st.session_state.drawing_mode = 'transform'

    other = [m for m in icon_dict if m != 'transform']
    for i in range(0, len(other), 3):
        cols = st.sidebar.columns(3, gap="small")
        for mode, col in zip(other[i:i+3], cols):
            if col.button(
                icon_dict[mode],
                key=f"btn_{mode}",
                use_container_width=True
            ):
                st.session_state.drawing_mode = mode

    drawing_mode = st.session_state.drawing_mode

    stroke_width = st.sidebar.slider("Stroke width:", 1, 25, 3)
    if drawing_mode == "point":
        point_display_radius = st.sidebar.slider("Point display radius:", 1, 25, 3)
    else:
        point_display_radius = 0

    color_col1, color_col2 = st.sidebar.columns(2, gap="small")
    stroke_color = color_col1.color_picker("Stroke color:")
    bg_color = color_col2.color_picker("Background color:", "#eee")

    bg_file = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
    realtime_update = st.sidebar.checkbox("Update in realtime", True)
    display_toolbar = st.sidebar.checkbox("Display toolbar", True)

    # Convert uploaded file to data URI or PIL.Image
    bg_arg = None
    if bg_file:
        try:
            bg_arg = _get_image_url(bg_file)
        except Exception:
            bg_arg = Image.open(bg_file)

    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=bg_arg,
        update_streamlit=realtime_update,
        height=400,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius,
        display_toolbar=display_toolbar,
        key="full_app",
    )

    # Display results
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=["object"]).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Streamlit mini figma",
        page_icon=":pencil2:"
    )
    # st.title("Mini figma")
    st.sidebar.subheader("Draft")
    main()