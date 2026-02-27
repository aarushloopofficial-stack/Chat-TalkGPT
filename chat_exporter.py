"""
Chat&Talk GPT - Chat History Export Module
Export chat conversations to various formats (PDF, Markdown, JSON, HTML)
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("ChatExporter")

# Try to import PDF library
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    REPORTLAB_AVAILABLE = True
    logger.info("ReportLab is available")
except ImportError:
    logger.warning("ReportLab not available")


class ChatExporter:
    """
    Chat History Exporter
    
    Features:
    - Export to PDF
    - Export to Markdown
    - Export to JSON
    - Export to HTML
    - Export with timestamps
    - Include metadata
    """
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize Chat Exporter
        
        Args:
            output_dir: Directory to save exports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Chat Exporter initialized with output dir: {output_dir}")
    
    def export_to_json(
        self,
        chats: List[Dict[str, Any]],
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export chats to JSON
        
        Args:
            chats: List of chat messages
            filename: Output filename
            include_metadata: Include export metadata
            
        Returns:
            Export result with file path
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_export_{timestamp}.json"
            
            filepath = os.path.join(self.output_dir, filename)
            
            export_data = {
                "export_version": "1.0",
                "export_date": datetime.now().isoformat(),
                "total_messages": len(chats),
                "chats": chats
            }
            
            if include_metadata:
                export_data["metadata"] = {
                    "total": len(chats),
                    "first_message": chats[0] if chats else None,
                    "last_message": chats[-1] if chats else None
                }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported to JSON: {filepath}")
            
            return {
                "success": True,
                "filepath": filepath,
                "format": "json",
                "message_count": len(chats)
            }
            
        except Exception as e:
            logger.error(f"Export to JSON error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_to_markdown(
        self,
        chats: List[Dict[str, Any]],
        filename: Optional[str] = None,
        title: str = "Chat History"
    ) -> Dict[str, Any]:
        """
        Export chats to Markdown
        
        Args:
            chats: List of chat messages
            filename: Output filename
            title: Document title
            
        Returns:
            Export result with file path
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_export_{timestamp}.md"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Build markdown content
            md_lines = []
            
            # Header
            md_lines.append(f"# {title}\n")
            md_lines.append(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            md_lines.append(f"**Total Messages:** {len(chats)}\n")
            md_lines.append("---\n\n")
            
            # Messages
            for chat in chats:
                role = chat.get("role", "unknown")
                content = chat.get("content", "")
                timestamp_msg = chat.get("timestamp", "")
                
                if role == "user":
                    md_lines.append("## You\n")
                elif role == "assistant":
                    md_lines.append("## Assistant\n")
                else:
                    md_lines.append(f"## {role}\n")
                
                if timestamp_msg:
                    md_lines.append(f"*{timestamp_msg}*\n\n")
                
                md_lines.append(f"{content}\n\n")
                md_lines.append("---\n\n")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(md_lines)
            
            logger.info(f"Exported to Markdown: {filepath}")
            
            return {
                "success": True,
                "filepath": filepath,
                "format": "markdown",
                "message_count": len(chats)
            }
            
        except Exception as e:
            logger.error(f"Export to Markdown error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_to_html(
        self,
        chats: List[Dict[str, Any]],
        filename: Optional[str] = None,
        title: str = "Chat History"
    ) -> Dict[str, Any]:
        """
        Export chats to HTML
        
        Args:
            chats: List of chat messages
            filename: Output filename
            title: Document title
            
        Returns:
            Export result with file path
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_export_{timestamp}.html"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Build HTML content
            html_parts = []
            html_parts.append("<!DOCTYPE html><html lang='en'><head>")
            html_parts.append(f"<title>{title}</title>")
            html_parts.append("<meta charset='UTF-8'>")
            html_parts.append("<style>")
            html_parts.append("body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }")
            html_parts.append(".message { padding: 15px; margin: 10px 0; border-radius: 5px; }")
            html_parts.append(".user { background: #e3f2fd; border-left: 4px solid #2196f3; }")
            html_parts.append(".assistant { background: #f1f8e9; border-left: 4px solid #4caf50; }")
            html_parts.append("</style></head><body>")
            html_parts.append(f"<h1>{title}</h1>")
            html_parts.append(f"<p>Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
            
            # Messages
            for chat in chats:
                role = chat.get("role", "unknown")
                content = chat.get("content", "")
                timestamp_msg = chat.get("timestamp", "")
                
                role_class = "user" if role == "user" else "assistant"
                role_label = "You" if role == "user" else "Assistant"
                
                html_parts.append(f"<div class='message {role_class}'>")
                html_parts.append(f"<strong>{role_label}</strong>")
                if timestamp_msg:
                    html_parts.append(f"<br><small>{timestamp_msg}</small>")
                html_parts.append(f"<p>{self._escape_html(content)}</p>")
                html_parts.append("</div>")
            
            html_parts.append("</body></html>")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("".join(html_parts))
            
            logger.info(f"Exported to HTML: {filepath}")
            
            return {
                "success": True,
                "filepath": filepath,
                "format": "html",
                "message_count": len(chats)
            }
            
        except Exception as e:
            logger.error(f"Export to HTML error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_to_pdf(
        self,
        chats: List[Dict[str, Any]],
        filename: Optional[str] = None,
        title: str = "Chat History"
    ) -> Dict[str, Any]:
        """Export chats to PDF"""
        if not REPORTLAB_AVAILABLE:
            return {
                "success": False,
                "error": "ReportLab not available"
            }
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_export_{timestamp}.pdf"
            
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            
            story.append(Paragraph(title, "Heading1"))
            story.append(Paragraph(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "Normal"))
            story.append(Paragraph(f"Total Messages: {len(chats)}", "Normal"))
            story.append(Spacer(1, 20))
            
            for chat in chats:
                role = chat.get("role", "unknown")
                content = chat.get("content", "")
                timestamp_msg = chat.get("timestamp", "")
                
                role_label = "You" if role == "user" else "Assistant"
                story.append(Paragraph(f"<b>{role_label}</b>", "Heading2"))
                if timestamp_msg:
                    story.append(Paragraph(f"<i>{timestamp_msg}</i>", "Normal"))
                story.append(Paragraph(content, "Normal"))
                story.append(Spacer(1, 10))
            
            doc.build(story)
            
            return {
                "success": True,
                "filepath": filepath,
                "format": "pdf",
                "message_count": len(chats)
            }
            
        except Exception as e:
            logger.error(f"Export to PDF error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return text.replace('&', '&').replace('<', '<').replace('>', '>')
    
    def export_conversation(
        self,
        chats: List[Dict[str, Any]],
        format: str = "json",
        filename: Optional[str] = None,
        title: str = "Chat History"
    ) -> Dict[str, Any]:
        """Export conversation in specified format"""
        if format.lower() == "json":
            return self.export_to_json(chats, filename)
        elif format.lower() in ["markdown", "md"]:
            return self.export_to_markdown(chats, filename, title)
        elif format.lower() == "html":
            return self.export_to_html(chats, filename, title)
        elif format.lower() == "pdf":
            return self.export_to_pdf(chats, filename, title)
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {format}"
            }


# Singleton instance
chat_exporter = ChatExporter()


def export_conversation(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to export conversation"""
    return chat_exporter.export_conversation(*args, **kwargs)
