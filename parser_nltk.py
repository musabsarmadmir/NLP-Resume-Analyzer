import os
import re
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import nltk; from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK data (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    def __init__(self):
        # Initialize database
        self.init_db()
        
        # Initialize NLTK
        self.stop_words = set(stopwords.words('english'))
        
        # Create UI
        self.create_ui()
    
    def init_db(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('resume_analyzer.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            password TEXT
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_scores (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            filename TEXT,
            ats_score REAL,
            parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        self.conn.commit()
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def parse_resume(self, text):
        """Parse resume text using NLTK"""
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        
        # Extract skills
        skills = self.extract_skills(filtered_tokens, text.lower())
        
        # Extract education
        education = self.extract_education(text)
        
        # Extract experience
        experience = self.extract_experience(text)
        
        return {
            "skills": skills,
            "education": education,
            "experience": experience
        }
    
    def extract_skills(self, tokens, text):
        """Extract skills from resume"""
        # Common skills to look for (can be expanded)
        skills_list = [
            "python", "java", "javascript", "html", "css", "sql", "nosql", 
            "react", "angular", "vue", "node", "express", "django", "flask",
            "aws", "azure", "gcp", "docker", "kubernetes", "git", "agile",
            "scrum", "machine learning", "data analysis", "data science",
            "tensorflow", "pytorch", "nlp", "computer vision"
        ]
        
        skills_found = []
        
        for skill in skills_list:
            if skill in tokens or re.search(r'\b' + re.escape(skill) + r'\b', text):
                skills_found.append(skill)
        
        return skills_found
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        #School Name Patterns college, university, etc.
        education_patterns = [
        r'(?i)(?:Bachelor|BS|BA|Master|MS|MA|PhD|Doctorate|Associate)(?:\s+of\s+|\s+in\s+|\s+)(?:Science|Arts|Engineering|Business|Administration|Computer Science|Information Technology|Financial Technology|Data Science)',
        r'(?i)(?:University|College|Institute|School) of [\w\s]+',
        r'(?i)(?:FAST|FAST-NUCES|National University of Computer and Emerging Sciences)(?:[- ](?:Islamabad|Lahore|Karachi|Peshawar|Chiniot-Faisalabad|Faisalabad))?',
        r'(?i)Foundation for Advancement of Science and Technology'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text)
            education.extend(matches)
        
        return education
    
    def extract_experience(self, text):
        experience = []
        
        job_titles = [
            r'(?i)(?:Senior|Junior|Lead|Principal)?\s*(?:Software|Systems|Data|Full Stack|Frontend|Backend|Web|Mobile|Cloud|DevOps|QA|Test)\s*(?:Engineer|Developer|Architect|Analyst|Scientist)',
            r'(?i)(?:Project|Product|Program)\s*Manager',
            r'(?i)(?:Director|VP|CTO|CEO|CIO|COO)'
        ]
        
        for pattern in job_titles:
            matches = re.findall(pattern, text)
            experience.extend(matches)
        
        return experience
    
    def calculate_ats_score(self, parsed_data, job_description=None):
        
        score = 0
        max_score = 100
        
        # Score: Skills (up to 40 points), 1 Skill = 2.5 points, max 16 skills = 40 points
        skills_count = len(parsed_data["skills"])
        skills_score = min(skills_count * 2.5, 40)
        score += skills_score
        
        # Score: Education (up to 30 points), 1 Education = 10 points, max 3 educations = 30 points(Bachelor, Master, PhD)
        education_count = len(parsed_data["education"])
        education_score = min(education_count * 10, 30)
        score += education_score
        
        # Score: Experience (up to 30 points), 1 Experience = 5 points, max 6 experiences = 30 points
        # (Internship, Junior, Senior, Lead, Principal, etc.)
        experience_count = len(parsed_data["experience"])
        experience_score = min(experience_count * 5, 30)
        score += experience_score
        
        return (score / max_score) * 100
    
    def save_results(self, filename, ats_score, user_id=1):
        try:
            self.cursor.execute(
                "INSERT INTO resume_scores (user_id, filename, ats_score) VALUES (?, ?, ?)",
                (user_id, filename, ats_score)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select Resume PDF",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        
        if filename:
            self.file_path.set(filename)
    
    def process_resume(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Select a PDF file.")
            return
        if not file_path.lower().endswith('.pdf'):
            messagebox.showerror("Error", "Only PDF files are supported")
            return
        
        if not os.path.isfile(file_path):
            messagebox.showerror("Error", "File not found")
            return
        text = self.extract_text_from_pdf(file_path)
        
        if not text:
            messagebox.showerror("Error", "Could not extract text from the PDF")
            return
        
        # Parse resume
        parsed_data = self.parse_resume(text)
        
        # Calculate ATS score
        ats_score = self.calculate_ats_score(parsed_data)
        
        # Save results
        filename = os.path.basename(file_path)
        saved = self.save_results(filename, ats_score)
        
        # Display results
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"ATS Score: {ats_score:.2f}%\n\n")
        
        self.result_text.insert(tk.END, "Skills Found:\n")
        for skill in parsed_data["skills"]:
            self.result_text.insert(tk.END, f"- {skill}\n")
        
        self.result_text.insert(tk.END, "\nEducation:\n")
        for edu in parsed_data["education"]:
            self.result_text.insert(tk.END, f"- {edu}\n")
        
        self.result_text.insert(tk.END, "\nExperience:\n")
        for exp in parsed_data["experience"]:
            self.result_text.insert(tk.END, f"- {exp}\n")
        
        if saved:
            messagebox.showinfo("Success", f"Resume analyzed and saved with ATS score: {ats_score:.2f}%")
    
    def create_ui(self):
        """Create the Tkinter UI"""
        self.root = tk.Tk()
        self.root.title("Resume Analyzer")
        self.root.geometry("800x600")
        
        # Style
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path = tk.StringVar()
        
        ttk.Label(file_frame, text="Select Resume PDF:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        # Process button
        ttk.Button(main_frame, text="Analyze Resume", command=self.process_resume).pack(pady=10)
        
        # Results area
        result_frame = ttk.LabelFrame(main_frame, text="Analysis Results")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.root.mainloop()

if __name__ == "__main__":
    parser = ResumeParser()