
import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader

# Set up Streamlit app
st.title("File Text Extractor")

# Upload file
uploaded_file = st.file_uploader("Upload a .pdf, .docx, or .txt file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    
    # Close the file before loading
    file_extension = os.path.splitext(uploaded_file.name)[1]
    extracted_text = ""

    # Define loader based on file type
    try:
        if file_extension == ".pdf":
            loader = PyMuPDFLoader(temp_file_path)
            output_suffix = "_PyMuPDFLoader.txt"
        elif file_extension in [".docx", ".doc"]:
            loader = Docx2txtLoader(temp_file_path)
            output_suffix = "_Docx2txtLoader.txt"
        elif file_extension == ".txt":
            # Use TextLoader if it works; if not, fall back to direct reading
            try:
                loader = TextLoader(temp_file_path)
                docs = loader.load()
                extracted_text = "\n".join([doc.page_content for doc in docs])
            except Exception as e:
                st.warning(f"TextLoader encountered an issue: {e}. Using direct file read.")
                with open(temp_file_path, "r", encoding="utf-8") as file:
                    extracted_text = file.read()
            output_suffix = "_TextLoader.txt"
        else:
            st.error("Unsupported file format.")
            st.stop()

        if not extracted_text:  # Only load if TextLoader failed
            docs = loader.load()
            extracted_text = "\n".join([doc.page_content for doc in docs])

        # Display the extracted text
        st.subheader("Extracted Text")
        st.text_area("Content", extracted_text, height=300)

        # Provide option to download the extracted text
        text_filename = os.path.splitext(uploaded_file.name)[0] + output_suffix
        st.download_button(
            label="Download Extracted Text",
            data=extracted_text,
            file_name=text_filename,
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"Error processing file: {e}")
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)
else:
    st.info("Please upload a file to continue.")
