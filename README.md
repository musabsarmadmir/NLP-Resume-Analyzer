# Resume Analyzer

## Overview
This repository contains a Python-based ATS (Applicant Tracking System) Resume Analyzer that helps users evaluate and score resumes based on skills, education, and experience. The tool uses natural language processing techniques to extract key information from PDF resumes and provides an ATS compatibility score.

## Features
- Extract text from PDF resumes
- Identify skills, education, and experience sections
- Calculate ATS compatibility score based on keyword matching
- Display detailed analysis results
- Store analysis history in a SQLite database
- User-friendly graphical interface built with Tkinter

## Requirements

### Dependencies
- Python 3.6+
- Required Python packages:
  - `sqlite3` (included in Python standard library)
  - `tkinter` (included in Python standard library)
  - `PyPDF2` (v3.0.0+)
  - `nltk` (v3.8.1+)

### NLTK Data Packages
The following NLTK data packages are automatically downloaded during first-time use:
- `punkt` (tokenizer)
- `punkt_tab` (tokenizer extensions)
- `stopwords` (common English stopwords)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer
```

2. Install required packages:
```bash
pip install PyPDF2 nltk
```

3. Run the application:
```bash
python parser_nltk.py
```

## Usage

1. Launch the application by running `parser_nltk.py`
2. Click the "Browse" button to select a PDF resume file
3. Click "Analyze Resume" to process the resume
4. Review the analysis results in the displayed text area
5. Results are automatically saved to the database

## Sample Resumes

The repository includes three sample resumes optimized for high ATS scores:

1. `alex_rodriguez_software_engineer.pdf` - Scores ~95%
   - Strong emphasis on software engineering skills
   - Balanced experience across backend and frontend
   - Highlights experience with Python, Java, and JavaScript

2. `sarah_johnson_data_scientist.pdf` - Scores ~98%
   - Focuses on data science and machine learning skills
   - Strong academic background with PhD in Computer Science
   - Demonstrates expertise in NLP and Computer Vision

3. `jordan_patel_full_stack.pdf` - Scores ~92%
   - Highlights full stack development capabilities
   - Emphasizes cloud deployment and DevOps practices
   - Shows progression from backend to full stack development

## How the Scoring Works

The resume analyzer calculates scores based on three main categories:

1. **Skills (40%)**: 
   - Each detected skill contributes 2.5 points (max 40 points)
   - The tool looks for keywords like Python, Java, SQL, AWS, etc.

2. **Education (30%)**:
   - Each recognized education entry contributes 10 points (max 30 points)
   - Detects university names and degree types

3. **Experience (30%)**:
   - Each recognized job title contributes 5 points (max 30 points)
   - Identifies roles like Software Engineer, Data Scientist, etc.

## Database Structure

The analyzer stores resume analysis results in a SQLite database:

```
TABLE resume_scores
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- filename
- ats_score
- parsed_date
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- Job description matching capability
- Keyword optimization suggestions
- Support for additional file formats (.docx, .txt)
- Improved skill extraction with industry-specific dictionaries
- Resume formatting suggestions
- Export analysis results to PDF
- Advanced visualization of resume strengths and weaknesses

## License

This project is licensed under the MIT License - see the LICENSE file for details.
