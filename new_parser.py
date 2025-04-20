import os
import re
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import nltk; from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# NLTK Data Packs (needed for tokenization and stopwords)
# Download punkt and stopwords if not already available
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
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.init_db()
        self.stop_words = set(stopwords.words('english'))
        self.create_ui()

    def init_db(self):
        self.conn = sqlite3.connect('resumes_analyzer_ATS.db')
        self.cursor = self.conn.cursor()
        
        # Create resume_scores table (enhanced)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_scores (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            job_description_id INTEGER NULL,
            filename TEXT,
            ats_score REAL,
            resume_text TEXT,
            parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id)
        )
        ''')
        
        # Create job_descriptions table (removed description field)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            company TEXT,
            required_skills TEXT,
            preferred_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create skills table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER,
            skill_name TEXT,
            category TEXT,
            relevance_score INTEGER DEFAULT 0,
            FOREIGN KEY (resume_id) REFERENCES resume_scores (id)
        )
        ''')
        
        # Create education table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER,
            institution TEXT,
            degree TEXT,
            field_of_study TEXT,
            start_date TEXT,
            end_date TEXT,
            gpa REAL,
            FOREIGN KEY (resume_id) REFERENCES resume_scores (id)
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER,
            company TEXT,
            position TEXT,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT,
            responsibilities TEXT,
            FOREIGN KEY (resume_id) REFERENCES resume_scores (id)
        )
        ''')
        
        self.conn.commit()
    
    def extract_text_from_pdf(self, pdf_path):
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
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords
        filtered_tokens = [word for word in tokens if word is not None and word.isalnum() and word not in self.stop_words]
        
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
        skills_list = [
            "Python", "Java", "Javascript", "HTML", "CSS", "SQL", "NoSQL", 
            "React", "Angular", "Vue", "Node", "Express", "Django", "Flask",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Agile",
            "Scrum", "Machine Learning", "Data Analysis", "Data Science",
            "TensorFlow", "PyTorch", "NLP", "Computer Vision"
        ]
        
        # Categorize skills
        technical_skills = [
            "Python", "Java", "Javascript", "HTML", "CSS", "SQL", "NoSQL", 
            "React", "Angular", "Vue", "Node", "Express", "Django", "Flask",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git"
        ]
        
        soft_skills = [
            "Communication", "Leadership", "Teamwork", "Problem Solving",
            "Critical Thinking", "Time Management", "Adaptability"
        ]
        
        domain_skills = [
            "Machine Learning", "Data Analysis", "Data Science",
            "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Agile",
            "Scrum"
        ]
        
        skills_found = []
        
        for skill in skills_list:
            if skill in tokens or re.search(r'\b' + re.escape(skill) + r'\b', text):
                # Determine category
                category = "Technical"
                if skill in soft_skills:
                    category = "Soft"
                elif skill in domain_skills:
                    category = "Domain"
                
                skills_found.append({
                    "name": skill,
                    "category": category,
                    "relevance_score": 0  # Will be updated if job description is provided
                })
        
        return skills_found
    
    def extract_education(self, text):
        education = []
        
        # School Name Patterns college, university, etc.
        education_patterns = [
            r'(?i)(?:Bachelor|BS|BA|Master|MS|MA|PhD|Doctorate|Associate)(?:\s+of\s+|\s+in\s+|\s+)(?:Science|Arts|Engineering|Business|Administration|Computer Science|Information Technology|Financial Technology|Data Science)',
            r'(?i)(?:University|College|Institute|School) of [\w\s]+',
            r'(?i)(?:FAST|FAST-NUCES|National University of Computer and Emerging Sciences)(?:[- ](?:Islamabad|Lahore|Karachi|Peshawar|Chiniot-Faisalabad|Faisalabad))?',
            r'(?i)Foundation for Advancement of Science and Technology',
            r'(?i)(?:High School|Secondary School|School) of [\w\s]+'
        ]
        
        # Date patterns
        date_pattern = r'(?i)(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4} - (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4} - Present|\d{4} - \d{4}|\d{4} - Present'
        
        # GPA pattern
        gpa_pattern = r'GPA:? \d+\.\d+|\d+\.\d+/\d+\.\d+ GPA'
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                edu_entry = {
                    "institution": match,
                    "degree": "",
                    "field_of_study": "",
                    "start_date": "",
                    "end_date": "",
                    "gpa": None
                }
                
                # Try to find degree and field near this institution
                degree_match = re.search(r'(?i)(?:Bachelor|BS|BA|Master|MS|MA|PhD|Doctorate|Associate)(?:\s+of\s+|\s+in\s+|\s+)(?:Science|Arts|Engineering|Business|Administration|Computer Science|Information Technology|Financial Technology|Data Science)', text[max(0, text.find(match)-100):text.find(match)+len(match)+100])
                if degree_match:
                    edu_entry["degree"] = degree_match.group(0)
                
                # Try to find dates
                date_match = re.search(date_pattern, text[max(0, text.find(match)-100):text.find(match)+len(match)+100])
                if date_match:
                    dates = date_match.group(0).split(' - ')
                    if len(dates) == 2:
                        edu_entry["start_date"] = dates[0]
                        edu_entry["end_date"] = dates[1]
                
                # Try to find GPA
                gpa_match = re.search(gpa_pattern, text[max(0, text.find(match)-100):text.find(match)+len(match)+100])
                if gpa_match:
                    gpa_text = gpa_match.group(0)
                    gpa_value = re.search(r'\d+\.\d+', gpa_text)
                    if gpa_value:
                        edu_entry["gpa"] = float(gpa_value.group(0))
                
                education.append(edu_entry)
        
        return education
    
    def extract_experience(self, text):
        experience = []
        
        job_titles = [
            r'(?i)(?:Senior|Junior|Lead|Principal)?\s*(?:Software|Systems|Data|Full Stack|Frontend|Backend|Web|Mobile|Cloud|DevOps|QA|Test)\s*(?:Engineer|Developer|Architect|Analyst|Scientist)',
            r'(?i)(?:Project|Product|Program)\s*Manager',
            r'(?i)(?:Director|VP|CTO|CEO|CIO|COO)'
        ]
        
        # Company pattern
        company_pattern = r'(?i)(?:at|for|with) ([\w\s]+)'
        
        # Date pattern
        date_pattern = r'(?i)(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4} - (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4} - Present|\d{4} - \d{4}|\d{4} - Present'
        
        for pattern in job_titles:
            matches = re.findall(pattern, text)
            for match in matches:
                exp_entry = {
                    "position": match,
                    "company": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "description": "",
                    "responsibilities": ""
                }
                
                # Try to find company near this position
                company_match = re.search(company_pattern, text[max(0, text.find(match)-50):text.find(match)+len(match)+100])
                if company_match and len(company_match.groups()) > 0:
                    exp_entry["company"] = company_match.group(1)
                
                # Try to find dates
                date_match = re.search(date_pattern, text[max(0, text.find(match)-100):text.find(match)+len(match)+100])
                if date_match:
                    dates = date_match.group(0).split(' - ')
                    if len(dates) == 2:
                        exp_entry["start_date"] = dates[0]
                        exp_entry["end_date"] = dates[1]
                
                # Extract a snippet of text around the job title as description
                start_idx = max(0, text.find(match) - 50)
                end_idx = min(len(text), text.find(match) + len(match) + 200)
                exp_entry["description"] = text[start_idx:end_idx].strip()
                
                # Extract responsibilities (bullet points after job title)
                resp_pattern = r'(?:•|\*|\-|\d+\.)\s*([\w\s\.,;:]+)'
                resp_matches = re.findall(resp_pattern, text[text.find(match):text.find(match)+500])
                if resp_matches:
                    exp_entry["responsibilities"] = "; ".join(resp_matches)
                
                experience.append(exp_entry)
        
        return experience
    
    def get_job_descriptions(self):
        """Get all job descriptions for the current user"""
        try:
            self.cursor.execute(
                "SELECT id, title, company FROM job_descriptions WHERE user_id = ? ORDER BY created_at DESC",
                (self.user_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching job descriptions: {e}")
            return []
    
    def get_job_description(self, job_id):
        """Get a specific job description"""
        try:
            self.cursor.execute(
                "SELECT * FROM job_descriptions WHERE id = ?",
                (job_id,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching job description: {e}")
            return None
    
    def save_job_description(self, title, company, required_skills, preferred_skills):
        """Save a new job description"""
        try:
            self.cursor.execute(
                """INSERT INTO job_descriptions 
                   (user_id, title, company, required_skills, preferred_skills) 
                   VALUES (?, ?, ?, ?, ?)""",
                (self.user_id, title, company, required_skills, preferred_skills)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error saving job description: {e}")
            return None
    
    def calculate_ats_score(self, parsed_data, job_description=None):
        score = 0
        max_score = 100
        
        # If job description is provided, use it for more accurate scoring
        if job_description:
            # Extract required and preferred skills from job description
            # Indices adjusted after removing description field
            # Now: index 4 = required_skills, index 5 = preferred_skills
            required_skills = job_description[4].split(',') if job_description[4] else []
            preferred_skills = job_description[5].split(',') if job_description[5] else []
            
            # Calculate skill match score (up to 40 points)
            skill_names = [skill["name"] for skill in parsed_data["skills"]]
            required_matches = sum(1 for skill in required_skills if any(re.search(r'\b' + re.escape(skill.strip()) + r'\b', s, re.IGNORECASE) for s in skill_names))
            preferred_matches = sum(1 for skill in preferred_skills if any(re.search(r'\b' + re.escape(skill.strip()) + r'\b', s, re.IGNORECASE) for s in skill_names))
            
            # Update relevance scores for skills
            for skill in parsed_data["skills"]:
                if any(re.search(r'\b' + re.escape(skill["name"]) + r'\b', s, re.IGNORECASE) for s in required_skills):
                    skill["relevance_score"] = 3  # High relevance
                elif any(re.search(r'\b' + re.escape(skill["name"]) + r'\b', s, re.IGNORECASE) for s in preferred_skills):
                    skill["relevance_score"] = 2  # Medium relevance
                else:
                    skill["relevance_score"] = 1  # Low relevance
            
            # Calculate required skills percentage match
            required_percentage = required_matches / len(required_skills) if required_skills else 1
            preferred_percentage = preferred_matches / len(preferred_skills) if preferred_skills else 1
            
            # Weight required skills more heavily
            skills_score = (required_percentage * 30) + (preferred_percentage * 10)
            skills_score = min(skills_score, 40)
            
            # Education score (up to 30 points)
            education_count = len(parsed_data["education"])
            education_score = min(education_count * 10, 30)
            
            # Experience score (up to 30 points)
            experience_count = len(parsed_data["experience"])
            experience_score = min(experience_count * 5, 30)
            
            score = skills_score + education_score + experience_score
        else:
            # Use the original scoring method if no job description is provided
            # Score: Skills (up to 40 points), 1 Skill = 2.5 points, max 16 skills = 40 points
            skills_count = len(parsed_data["skills"])
            skills_score = min(skills_count * 2.5, 40)
            score += skills_score
            
            # Score: Education (up to 30 points), 1 Education = 10 points, max 3 educations = 30 points
            education_count = len(parsed_data["education"])
            education_score = min(education_count * 10, 30)
            score += education_score
            
            # Experience score (up to 30 points), 1 Experience = 5 points, max 6 experiences = 30 points
            experience_count = len(parsed_data["experience"])
            experience_score = min(experience_count * 5, 30)
            score += experience_score
        
        return (score / max_score) * 100
    
    def save_results(self, filename, ats_score, parsed_data, resume_text, job_description_id=None):
        try:
            # Begin transaction
            self.conn.execute("BEGIN TRANSACTION")
            
            # Insert into resume_scores table
            self.cursor.execute(
                """INSERT INTO resume_scores 
                   (user_id, job_description_id, filename, ats_score, resume_text) 
                   VALUES (?, ?, ?, ?, ?)""",
                (self.user_id, job_description_id, filename, ats_score, resume_text)
            )
            
            resume_id = self.cursor.lastrowid
            
            # Insert skills
            for skill in parsed_data["skills"]:
                self.cursor.execute(
                    """INSERT INTO skills 
                       (resume_id, skill_name, category, relevance_score) 
                       VALUES (?, ?, ?, ?)""",
                    (resume_id, skill["name"], skill["category"], skill["relevance_score"])
                )
            
            # Insert education
            for edu in parsed_data["education"]:
                self.cursor.execute(
                    """INSERT INTO education 
                       (resume_id, institution, degree, field_of_study, start_date, end_date, gpa) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (resume_id, edu["institution"], edu["degree"], edu["field_of_study"], 
                     edu["start_date"], edu["end_date"], edu["gpa"])
                )
            
            # Insert experience
            for exp in parsed_data["experience"]:
                self.cursor.execute(
                    """INSERT INTO experience 
                       (resume_id, company, position, location, start_date, end_date, description, responsibilities) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (resume_id, exp["company"], exp["position"], exp["location"], 
                     exp["start_date"], exp["end_date"], exp["description"], exp["responsibilities"])
                )
            
            # Commit transaction
            self.conn.commit()
            return True
        except Exception as e:
            # Rollback in case of error
            self.conn.rollback()
            print(f"Error saving results: {e}")
            return False
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select Resume. Only PDF files are supported",
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
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(file_path)
        
        if not text:
            messagebox.showerror("Error", "Could not extract text from the PDF")
            return
        
        # Parse resume
        parsed_data = self.parse_resume(text)
        
        # Get selected job description if any
        job_description = None
        job_description_id = None
        if hasattr(self, 'job_var') and self.job_var.get() != "None":
            job_id = int(self.job_var.get().split(':')[0])
            job_description = self.get_job_description(job_id)
            job_description_id = job_id
        
        # Calculate ATS score
        ats_score = self.calculate_ats_score(parsed_data, job_description)
        
        # Save results
        filename = os.path.basename(file_path)
        saved = self.save_results(filename, ats_score, parsed_data, text, job_description_id)
        
        # Display results
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"ATS Score: {ats_score:.2f}%\n\n")
        
        self.result_text.insert(tk.END, "Skills Found:\n")
        for skill in parsed_data["skills"]:
            relevance = ""
            if skill["relevance_score"] == 3:
                relevance = " (High Relevance)"
            elif skill["relevance_score"] == 2:
                relevance = " (Medium Relevance)"
            
            self.result_text.insert(tk.END, f"- {skill['name']} [{skill['category']}]{relevance}\n")
        
        self.result_text.insert(tk.END, "\nEducation:\n")
        for edu in parsed_data["education"]:
            edu_str = f"- {edu['institution']}"
            if edu["degree"]:
                edu_str += f", {edu['degree']}"
            if edu["start_date"] or edu["end_date"]:
                edu_str += f" ({edu['start_date']} - {edu['end_date']})"
            if edu["gpa"]:
                edu_str += f", GPA: {edu['gpa']}"
            self.result_text.insert(tk.END, f"{edu_str}\n")
        
        self.result_text.insert(tk.END, "\nExperience:\n")
        for exp in parsed_data["experience"]:
            exp_str = f"- {exp['position']}"
            if exp["company"]:
                exp_str += f" at {exp['company']}"
            if exp["start_date"] or exp["end_date"]:
                exp_str += f" ({exp['start_date']} - {exp['end_date']})"
            self.result_text.insert(tk.END, f"{exp_str}\n")
            if exp["responsibilities"]:
                self.result_text.insert(tk.END, f"  Responsibilities: {exp['responsibilities']}\n")
        
        if saved:
            messagebox.showinfo("Success", f"Resume analyzed, ATS score: {ats_score:.2f}%")
    
    def add_job_description(self):
        """Open a dialog to add a new job description"""
        job_window = tk.Toplevel(self.root)
        job_window.title("Add Job Description")
        job_window.geometry("600x400")
        
        # Job title
        ttk.Label(job_window, text="Job Title:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        title_entry = ttk.Entry(job_window, width=50)
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Company
        ttk.Label(job_window, text="Company:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        company_entry = ttk.Entry(job_window, width=50)
        company_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Required Skills
        ttk.Label(job_window, text="Required Skills:").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
        ttk.Label(job_window, text="(comma separated)").grid(row=2, column=0, sticky="sw", padx=10)
        required_skills_text = tk.Text(job_window, width=50, height=3)
        required_skills_text.grid(row=2, column=1, padx=10, pady=5)
        
        # Preferred Skills
        ttk.Label(job_window, text="Preferred Skills:").grid(row=3, column=0, sticky="nw", padx=10, pady=5)
        ttk.Label(job_window, text="(comma separated)").grid(row=3, column=0, sticky="sw", padx=10)
        preferred_skills_text = tk.Text(job_window, width=50, height=3)
        preferred_skills_text.grid(row=3, column=1, padx=10, pady=5)
        
        # Save button
        def save_job():
            title = title_entry.get()
            company = company_entry.get()
            required_skills = required_skills_text.get(1.0, tk.END)
            preferred_skills = preferred_skills_text.get(1.0, tk.END)
            
            if not title:
                messagebox.showerror("Error", "Job title is required")
                return
            
            job_id = self.save_job_description(title, company, required_skills, preferred_skills)
            if job_id:
                messagebox.showinfo("Success", "Job description saved successfully")
                job_window.destroy()
                # Refresh job descriptions dropdown
                self.load_job_descriptions()
            else:
                messagebox.showerror("Error", "Failed to save job description")
        
        ttk.Button(job_window, text="Save", command=save_job).grid(row=4, column=1, sticky="e", padx=10, pady=20)
    
    def load_job_descriptions(self):
        """Load job descriptions into the dropdown"""
        if hasattr(self, 'job_dropdown'):
            # Get job descriptions
            job_descriptions = self.get_job_descriptions()
            
            # Update dropdown values
            job_options = ["None"] + [f"{job[0]}: {job[1]} - {job[2]}" for job in job_descriptions]
            self.job_dropdown['values'] = job_options
            
            # Set to None by default
            self.job_var.set(job_options[0])
    
    def create_ui(self):
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
        
        # Job description selection
        job_frame = ttk.Frame(main_frame)
        job_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(job_frame, text="Select Job Description:").pack(side=tk.LEFT, padx=5)
        
        self.job_var = tk.StringVar()
        self.job_dropdown = ttk.Combobox(job_frame, textvariable=self.job_var, width=40)
        self.job_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Load job descriptions
        self.load_job_descriptions()
        
        ttk.Button(job_frame, text="Add New", command=self.add_job_description).pack(side=tk.LEFT, padx=5)
        
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