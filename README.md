# Paper2Blog 📚 ➡️ 📝

A modern web application that transforms academic papers into engaging blog posts using AI. Paper2Blog leverages advanced language and vision models to create accessible, well-structured blog content while maintaining academic accuracy.

## Features ✨

- **PDF Processing**: Upload academic papers in PDF format
- **Intelligent Content Generation**: Converts academic content into engaging blog posts
- **Image Handling**: Automatically extracts and captions figures from papers
- **Bilingual Support**: Generate content in English or Chinese
- **Modern UI**: Clean, responsive interface with Material-UI components
- **Markdown Output**: Well-formatted blog posts with proper image placement

## Tech Stack 🛠️

### Backend

- **Framework**: FastAPI
- **Language Models**: OpenAI GPT-4
- **PDF Processing**: PyPDF2
- **Vision Processing**: Transformers
- **Language**: Python 3.11+

### Frontend

- **Framework**: React
- **UI Library**: Material-UI (MUI)
- **File Upload**: react-dropzone
- **Markdown Rendering**: react-markdown
- **Styling**: CSS-in-JS with MUI theme

## Installation 🚀

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/paper2blog.git
cd paper2blog

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e ".[dev]"
```

### Using pip (when published)
```bash
pip install paper2blog
```

## Development Setup 🛠️

1. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run Tests**
   ```bash
   pytest
   ```

3. **Code Formatting**
   ```bash
   # Format code
   black .
   
   # Sort imports
   isort .
   
   # Check style
   flake8
   ```

## Setup 🚀

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/Paper2Blog.git
   cd Paper2Blog
   ```

2. **Backend Setup**

   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment variables
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings

   OPENAI_API_KEY=**
   OPENAI_API_BASE=**
   OPEN_MODEL=gpt-4o-mini
   ```

3. **Frontend Setup**

   ```bash
   cd frontend
   npm install
   ```

4. **Start the Application**

   ```bash
   # Terminal 1: Start backend server
   uvicorn main:app --reload

   # Terminal 2: Start frontend development server
   cd frontend
   npm start
   ```

5. **Access the Application**

   - Open [http://localhost:3000](http://localhost:3000) in your browser

6. **Marker Server**
   - Start the marker server with `marker_server --port 8024`

## Environment Variables 🔑

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1  # Or your custom API endpoint
```

## Usage 📖

1. **Upload Paper**

   - Drag and drop a PDF file or click to select
   - Alternatively, paste a URL to the paper

2. **Select Language**

   - Choose between English and Chinese for the output

3. **Generate Blog**

   - Click "Convert" to process the paper
   - The app will generate a blog post with:
     - Engaging title
     - Well-structured content
     - Properly placed figures with captions
     - Summary section
     - Relevant tags

4. **Export**
   - Copy the generated markdown
   - Use in your preferred blogging platform

## Development 👩‍💻

### Project Structure

```
Paper2Blog/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main application component
│   │   └── index.css      # Global styles
├── paper2blog/            # Backend modules
│   ├── __init__.py
│   ├── llm_handler.py     # LLM integration
│   └── models.py          # Data models
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

### Adding New Features

1. Backend: Add new endpoints in `main.py`
2. LLM: Modify prompts in `llm_handler.py`
3. Frontend: Update components in `frontend/src`

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- OpenAI for GPT models
- Hugging Face for Transformers
- FastAPI team
- React and Material-UI communities
