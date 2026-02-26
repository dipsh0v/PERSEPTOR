import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
import json
import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, Preformatted, Frame, HRFlowable
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ReportSection:
    """Represents a section in the PDF report."""
    title: str
    content: List[Any]
    level: int = 1
    style: Optional[Dict] = None

class PDFReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        """Initialize the PDF report generator.
        
        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self._ensure_output_dir()
        
    def _setup_styles(self):
        """Setup custom styles for the report."""
        # Custom styles for different heading levels
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a237e')  # Deep blue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor('#283593')  # Indigo
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#303f9f')  # Indigo 700
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#424242')  # Grey 800
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=8,
            fontName='Courier',
            backColor=colors.HexColor('#f5f5f5'),  # Grey 100
            borderPadding=5,
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0')  # Grey 300
        ))

        # Add styles for tables
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=1  # Center
        ))

        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#424242'),  # Grey 800
            leading=12
        ))

        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#0d47a1')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Content',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leading=14
        ))

    def _ensure_output_dir(self):
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)

    def _create_header(self, title: str) -> List[Any]:
        """Create the report header."""
        elements = []
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Content']
        ))
        elements.append(Spacer(1, 20))
        return elements

    def _create_section(self, section: ReportSection) -> List[Any]:
        """Create a report section."""
        elements = []
        
        # Add section title with horizontal line
        style_name = f'CustomHeading{section.level}'
        elements.append(Paragraph(section.title, self.styles[style_name]))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        elements.append(Spacer(1, 12))
        
        # Add section content
        for item in section.content:
            if isinstance(item, str):
                if self._is_code_block(item):
                    elements.append(Preformatted(item, self.styles['CustomCode']))
                else:
                    elements.append(Paragraph(item, self.styles['CustomBody']))
            elif isinstance(item, dict):
                elements.extend(self._handle_dict_content(item))
            elif isinstance(item, list):
                elements.extend(self._handle_list_content(item))
            elif isinstance(item, (Image, Table)):
                elements.append(item)
        
        elements.append(Spacer(1, 12))
        return elements

    def _is_code_block(self, text: str) -> bool:
        """Check if text should be formatted as code."""
        code_indicators = ['rule ', 'meta:', 'strings:', 'condition:', 'yaml', 'json']
        return any(indicator in text.lower() for indicator in code_indicators)

    def _handle_dict_content(self, content: Dict) -> List[Any]:
        """Handle dictionary content in the report."""
        elements = []
        
        # Special handling for different types of content
        if any(key in content for key in ['iocs', 'ttps', 'process_chains', 'malicious_execution_chains']):
            elements.extend(self._handle_special_tables(content))
        else:
            # Regular dictionary content
            table_data = []
            for k, v in content.items():
                if isinstance(v, list):
                    v = '\n'.join(str(x) for x in v)
                table_data.append([
                    Paragraph(str(k), self.styles['TableCell']),
                    Paragraph(str(v), self.styles['TableCell'])
                ])
            
            table = Table(table_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),  # Grey 100
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#424242')),  # Grey 800
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),  # Grey 300
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            elements.append(table)
        
        return elements

    def _handle_special_tables(self, content: Dict) -> List[Any]:
        """Handle special table formats for IoCs, TTPs, and chains."""
        elements = []
        
        # Handle IoCs
        if 'iocs' in content:
            ioc_data = content['iocs']
            table_data = [['IoC Type', 'Values']]
            for ioc_type, values in ioc_data.items():
                if isinstance(values, list):
                    values = '\n'.join(str(x) for x in values)
                table_data.append([ioc_type, values])
            
            table = Table(table_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),  # Deep blue
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#424242')),  # Grey 800
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),  # Grey 300
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Handle TTPs
        if 'ttps' in content:
            ttp_data = content['ttps']
            table_data = [['MITRE ID', 'Technique Name', 'Description']]
            for ttp in ttp_data:
                table_data.append([
                    ttp.get('mitre_id', ''),
                    ttp.get('technique_name', ''),
                    ttp.get('description', '')
                ])
            
            table = Table(table_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),  # Deep blue
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#424242')),  # Grey 800
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),  # Grey 300
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # Handle Process Chains
        if 'process_chains' in content:
            elements.append(Paragraph("Process Chains:", self.styles['CustomHeading2']))
            for chain in content['process_chains']:
                table_data = [['Step', 'Process', 'Description']]
                for step in chain:
                    table_data.append([
                        step.get('step', ''),
                        step.get('process', ''),
                        step.get('description', '')
                    ])
                
                table = Table(table_data, colWidths=[1*inch, 2*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),  # Indigo
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#424242')),  # Grey 800
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),  # Grey 300
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))

        return elements

    def _handle_list_content(self, content: List) -> List[Any]:
        """Handle list content in the report."""
        elements = []
        for item in content:
            if isinstance(item, str):
                if self._is_code_block(item):
                    elements.append(Preformatted(item, self.styles['CustomCode']))
                else:
                    elements.append(Paragraph(f"• {item}", self.styles['CustomBody']))
            elif isinstance(item, dict):
                elements.extend(self._handle_dict_content(item))
            elif isinstance(item, list):
                elements.extend(self._handle_list_content(item))
        return elements

    def _create_chart(self, data: Dict[str, float], chart_type: str = 'bar') -> Image:
        """Create a chart and return it as a ReportLab Image."""
        plt.figure(figsize=(6, 4))
        plt.style.use('seaborn')
        
        if chart_type == 'bar':
            plt.bar(data.keys(), data.values(), color='#1a237e')  # Deep blue
            plt.xticks(rotation=45, ha='right')
        elif chart_type == 'pie':
            plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%',
                   colors=sns.color_palette('Blues_d'))
        
        plt.tight_layout()
        
        # Save plot to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create ReportLab Image from the BytesIO object
        buf.seek(0)
        img = Image(buf)
        img.drawHeight = 3*inch
        img.drawWidth = 6*inch
        
        return img

    def generate_report(self, title: str, sections: list[ReportSection]) -> bytes:
        buffer = io.BytesIO()
            doc = SimpleDocTemplate(
            buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
        story = []
        
        # Add title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Generated on: {timestamp}", self.styles['Content']))
        story.append(Spacer(1, 24))
            
            # Add sections
        for section in sections:
            story.append(Paragraph(section.title, self.styles['SectionTitle']))
            story.append(Paragraph(section.content, self.styles['Content']))
            story.append(Spacer(1, 12))
            
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def add_sigma_matches(
        self,
        matches: List[Dict],
        confidence_scores: Dict[str, float]
    ) -> ReportSection:
        """Create a section for Sigma rule matches."""
        content = []
        
        # Group matches by category
        categories = {}
        for match in matches:
            category = match.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(match)
        
        # Create a table for each category
        for category, category_matches in categories.items():
            content.append(Paragraph(f"{category} Matches:", self.styles['CustomHeading2']))
            
            table_data = [['Sigma Rule Title', 'Match Ratio', 'Matched Keywords']]
            for match in category_matches:
                table_data.append([
                    match.get('title', ''),
                    f"{match.get('ratio', 0):.1f}%",
                    match.get('keywords', '')
                ])
            
            table = Table(table_data, colWidths=[3*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),  # Deep blue
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#424242')),  # Grey 800
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),  # Grey 300
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            content.append(table)
            content.append(Spacer(1, 12))
        
        return ReportSection(
            title="Global Sigma Matches",
            content=content,
            level=1
        )

    def add_analysis_summary(
        self,
        summary: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> ReportSection:
        """Create a section for analysis summary."""
        content = []
        
        # Add summary text
        content.append("Analysis Summary")
        content.append(summary.get('description', 'No description available'))
        
        # Add metrics
        content.append("\nKey Metrics:")
        metrics_table = Table(
            [[k, f"{v:.2f}"] for k, v in metrics.items()],
            colWidths=[2*inch, 1*inch]
        )
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
        ]))
        content.append(metrics_table)
        
        return ReportSection(
            title="Analysis Summary",
            content=content,
            level=1
        )

    def _add_sigma_match_section(self, section):
        """Add a sigma match section with detailed formatting."""
        self.doc.add_heading(section.title, level=2)
        
        for match in section.content:
            # Create a table for the match details
            table = self.doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            
            # Add header row
            header_cells = table.rows[0].cells
            header_cells[0].text = "Property"
            header_cells[1].text = "Value"
            
            # Add match details
            for key, value in match.items():
                row_cells = table.add_row().cells
                row_cells[0].text = key.replace('_', ' ').title()
                row_cells[1].text = str(value)
            
            # Add spacing after the table
            self.doc.add_paragraph()

    def _add_section(self, section):
        """Add a section to the document with appropriate formatting."""
        if section.title.startswith("Global Sigma Match"):
            self._add_sigma_match_section(section)
        else:
            self.doc.add_heading(section.title, level=1)
            
            for content in section.content:
                if isinstance(content, dict):
                    # Handle dictionary content (like analysis data)
                    table = self.doc.add_table(rows=1, cols=2)
                    table.style = 'Table Grid'
                    
                    # Add header row
                    header_cells = table.rows[0].cells
                    header_cells[0].text = "Property"
                    header_cells[1].text = "Value"
                    
                    # Add content rows
                    for key, value in content.items():
                        row_cells = table.add_row().cells
                        row_cells[0].text = key.replace('_', ' ').title()
                        if isinstance(value, list):
                            row_cells[1].text = '\n'.join(str(item) for item in value)
                        else:
                            row_cells[1].text = str(value)
                    
                    self.doc.add_paragraph()
                else:
                    # Handle text content
                    self.doc.add_paragraph(content)
                    self.doc.add_paragraph()

def create_pdf_generator(output_dir: str = "reports") -> PDFReportGenerator:
    """Create a PDF report generator instance."""
    return PDFReportGenerator(output_dir) 