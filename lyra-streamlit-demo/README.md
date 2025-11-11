# Lyra Streamlit Demo

## Overview
Lyra is an AI-powered study assistant designed to provide personalized learning support. This application leverages advanced AI functionalities to help users understand their course materials, track their learning progress, and prepare for exams through interactive quizzes.

## Project Structure
```
lyra-streamlit-demo
├── src
│   ├── app.py            # Main entry point for the Streamlit application
│   ├── lyra_ai.py        # Core AI functionalities
│   ├── vector_store.py    # Manages vector store for text embeddings
│   ├── quiz.py           # Handles quiz functionalities
│   └── utils.py          # Utility functions for various operations
├── .streamlit
│   └── config.toml       # Configuration settings for Streamlit
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── .gitignore             # Files to ignore by Git
└── README.md              # Project documentation
```

## Setup Instructions

1. **Install Dependencies**: 
   Ensure all dependencies listed in `requirements.txt` are installed. You can do this by running:
   ```
   pip install -r requirements.txt
   ```

2. **Run Locally**: 
   Test the application locally by navigating to the `src` directory and running:
   ```
   streamlit run app.py
   ```

3. **Docker Deployment**: 
   If using Docker, build the Docker image with the command:
   ```
   docker build -t lyra-streamlit-demo .
   ```
   Then run it using:
   ```
   docker run -p 8501:8501 lyra-streamlit-demo
   ```

4. **Streamlit Sharing**: 
   Alternatively, you can deploy the app on Streamlit Sharing by pushing your code to a GitHub repository and linking it to Streamlit Sharing.

5. **Access the App**: 
   Once deployed, access the app via the provided URL (e.g., `http://localhost:8501` for local runs or the URL provided by Streamlit Sharing).

## Usage Guidelines
- Upload your course materials in `.txt` format to get started.
- Use the Q&A mode to ask questions about your course material.
- Generate practice quizzes to prepare for exams.
- Track your learning progress and identify knowledge gaps.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.