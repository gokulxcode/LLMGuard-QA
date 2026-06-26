from fpdf import FPDF
import datetime
from io import BytesIO
from typing import Dict, Any, List

class LLMGuardReportPDF(FPDF):
    def header(self):
        # Header styling
        self.set_fill_color(30, 41, 59) # Slate-800
        self.rect(0, 0, 210, 35, "F")
        
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 18)
        self.set_xy(10, 8)
        self.cell(0, 10, "LLMGuard QA Report", ln=True)
        
        self.set_font("helvetica", "I", 10)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, "AI-Powered Testing Framework for Generative AI Applications", ln=True)
        
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | LLMGuard QA Confidential Report | Generated: {datetime.date.today()}", align="C")

class PDFReportGenerator:
    @staticmethod
    def generate_summary_pdf(data: Dict[str, Any]) -> bytes:
        pdf = LLMGuardReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        
        # Title of Section
        pdf.set_text_color(30, 41, 59)
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "1. Executive Summary", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Summary description
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, (
            "This report summarizes the non-deterministic quality evaluations run via the LLMGuard QA Testing Framework. "
            "Our pipeline evaluates safety parameters, hallucination indices, semantic stability under variations, context leakage risks, "
            "and quality regressions against baseline outputs."
        ))
        pdf.ln(5)
        
        # Score metrics grid
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(241, 245, 249) # Light grey bg
        pdf.cell(60, 8, "Metric Category", border=1, fill=True)
        pdf.cell(70, 8, "Value / Status", border=1, fill=True)
        pdf.cell(60, 8, "Evaluation Rating", border=1, fill=True, ln=True)
        
        pdf.set_font("helvetica", "", 10)
        metrics = [
            ("Total Prompt Tests Executed", str(data.get("total_tests", 0)), "N/A"),
            ("Hallucinations Detected", str(data.get("hallucinations_found", 0)), f"Rate: {data.get('hallucination_rate', 0.0)}%"),
            ("Safety Violations Found", str(data.get("safety_issues", 0)), "Action Required" if data.get("safety_issues", 0) > 0 else "Secure"),
            ("Context Leakage Cases", str(data.get("leakage_cases", 0)), "Warning" if data.get("leakage_cases", 0) > 0 else "Compliant"),
            ("Overall Pass Rate", f"{data.get('pass_rate', 0.0)}%", "Acceptable" if data.get("pass_rate", 0.0) >= 80.0 else "Critical"),
            ("Overall Failure Rate", f"{data.get('failure_rate', 0.0)}%", "Review Needed" if data.get("failure_rate", 0.0) > 20.0 else "Optimal")
        ]
        
        for m, val, rating in metrics:
            pdf.cell(60, 8, m, border=1)
            pdf.cell(70, 8, val, border=1)
            
            # Color code critical items
            if "Critical" in rating or "Action Required" in rating or "Warning" in rating:
                pdf.set_text_color(220, 38, 38) # Red
                pdf.set_font("helvetica", "B", 10)
            elif "Secure" in rating or "Optimal" in rating or "Acceptable" in rating:
                pdf.set_text_color(22, 163, 74) # Green
            else:
                pdf.set_text_color(50, 50, 50)
                
            pdf.cell(60, 8, rating, border=1, ln=True)
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            
        pdf.ln(10)
        
        # Section 2: Core Evaluator Aggregates
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, "2. Performance and Safety Quality Indicators", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Add detailed scores with visual indicators
        scores = [
            ("Accuracy & Hallucination Score", data.get("accuracy_score", 0.0), "Evaluates factual precision relative to domain benchmarks."),
            ("Safety Index Score", data.get("safety_score", 0.0), "Measures toxicity, harmful instructions, and bias prevention (higher is better)."),
            ("Consistency Score", data.get("consistency_score", 0.0), "Calculates repeatability and similarity of responses over multi-run trials."),
            ("Regression Quality Score", data.get("regression_score", 0.0), "Measures divergence and quality degradation against historical baselines.")
        ]
        
        for title, score, desc in scores:
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(80, 6, title)
            pdf.set_font("helvetica", "B", 11)
            
            if score >= 80:
                pdf.set_text_color(22, 163, 74) # Green
            elif score >= 60:
                pdf.set_text_color(217, 119, 6) # Orange
            else:
                pdf.set_text_color(220, 38, 38) # Red
                
            pdf.cell(0, 6, f"{score}%", ln=True, align="R")
            
            # Simple progress bar
            y = pdf.get_y()
            pdf.set_fill_color(226, 232, 240) # light grey bar track
            pdf.rect(10, y + 1, 190, 3, "F")
            
            # fill progress
            if score >= 80:
                pdf.set_fill_color(22, 163, 74)
            elif score >= 60:
                pdf.set_fill_color(217, 119, 6)
            else:
                pdf.set_fill_color(220, 38, 38)
            pdf.rect(10, y + 1, int(190 * (score / 100.0)), 3, "F")
            
            pdf.ln(6)
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, desc, ln=True)
            pdf.ln(5)
            
        pdf.ln(5)
        
        # Section 3: Category breakdown
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, "3. Prompt Test Breakdown by Category", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(95, 8, "Prompt Category", border=1, fill=True)
        pdf.cell(95, 8, "Executed Tests Count", border=1, fill=True, ln=True)
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        for cat, count in data.get("category_counts", {}).items():
            pdf.cell(95, 8, cat, border=1)
            pdf.cell(95, 8, str(count), border=1, ln=True)
            
        # Write to byte buffer
        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str):
            # Fallback if old fpdf format is used
            pdf_bytes = pdf_bytes.encode('latin1')
        return pdf_bytes
