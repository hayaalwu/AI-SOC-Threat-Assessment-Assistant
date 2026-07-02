import tempfile
import streamlit as st
from PIL import Image
from analyzer import analyze_soc_image
from analyzer import generate_soc_decision


# Configure the Streamlit page
st.set_page_config(page_title="AI SOC Threat Assessment Assistant", layout="wide")

# App title
st.title("AI SOC Threat Assessment Assistant")

# Short app description
st.write(
    "Upload a SOC/SIEM screenshot. "
    "The tool uses a Vision-Language Model to extract structured threat observations, "
    "then sends the structured output to the model again to generate a SOC decision."
)

# Upload image file
uploaded_file = st.file_uploader("Upload SOC screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Open the uploaded image and convert it to RGB
    image = Image.open(uploaded_file).convert("RGB")

    st.subheader("Image Input")
    st.image(image, use_container_width=True)

    if st.button("Analyze Image"):
        # Save the image temporarily so Ollama can read it by path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            image.save(temp_file.name)
            image_path = temp_file.name

        # Step 1: Analyze the image and generate structured output
        with st.spinner("Step 1: Analyzing image with Vision-Language Model..."):
            structured_output = analyze_soc_image(image_path)

        # Step 2: Generate a SOC decision from the structured output
        with st.spinner("Step 2: Generating SOC decision from structured output..."):
            decision_output = generate_soc_decision(structured_output)

        # Display the structured threat assessment
        st.subheader("Structured Output")
        st.json(structured_output)

        # Display the decision generated from the structured output
        st.subheader("Decision / Action")
        st.json(decision_output)

        # Display the final result in a simple readable format
        st.subheader("Final Result")
        st.info(
            f"SOC Status: {decision_output.get('overall_soc_status', 'Unknown')}. "
            f"{decision_output.get('recommended_action', 'Manual review is required.')}"
        )

else:
    # Show this message before the user uploads an image
    st.info("Please upload a SOC screenshot to start.")