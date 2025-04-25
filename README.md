# Resume Analyzer ATS

A comprehensive resume analysis application that uses Natural Language Processing (NLP) to parse resumes, extract key information, and provide an ATS (Applicant Tracking System) compatibility score.

## Features

- **User Authentication System**: Secure login and registration functionality
- **Resume PDF Parsing**: Extract text content from PDF resumes
- **Information Extraction**:
  - Skills detection with categorization (Technical, Soft, Domain)
  - Education history extraction
  - Work experience parsing
- **ATS Scoring**: Comprehensive scoring algorithm to evaluate resume compatibility with ATS systems
- **Modern GUI**: Clean and intuitive user interface built with CustomTkinter

## Requirements

- Python 3.6+
- Libraries:
  - `customtkinter`: For modern UI components
  - `sqlite3`: For database operations
  - `PyPDF2`: For PDF parsing
  - `nltk`: For natural language processing
  - `tkinter`: For GUI components

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-analyzer-ats.git
   cd resume-analyzer-ats
   ```

2. Install required packages:
   ```bash
   pip install customtkinter PyPDF2 nltk
   ```

3. Download required NLTK data:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

## Usage

Run the main application:

```bash
python main.py
```

### Authentication

1. Register with your name, age, email, and password
2. Login with your email and password

### Resume Analysis

1. Click "Browse" to select your resume PDF file
2. Click "Analyze Resume" to process the document
3. Review the analysis results, including:
   - ATS compatibility score
   - Extracted skills with categorization
   - Education history
   - Work experience details

## Project Structure

- **auth_system.py**: Handles user authentication and login UI
- **main.py**: Entry point for the application
- **new_parser.py**: Core resume parsing and analysis functionality

## Database Schema

The application uses SQLite with the following tables:

- **users**: User authentication data
- **resume_scores**: Overall resume analysis results
- **skills**: Extracted skills from resumes
- **education**: Education history from resumes
- **experience**: Work experience from resumes
- **resumes**: Main resume metadata and relationships

## How the ATS Score is Calculated

The ATS compatibility score is calculated based on:

- **Skills** (40%): Up to 40 points, with 2.5 points per skill (max 16 skills)
- **Education** (30%): Up to 30 points, with 10 points per education entry (max 3 entries)
- **Experience** (30%): Up to 30 points, with 10 points per experience entry (max 3 entries)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
