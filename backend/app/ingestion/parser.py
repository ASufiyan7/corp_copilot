from html.parser import HTMLParser
import re

class HTMLTextExtractor(HTMLParser):
    """
    Custom HTML parser to extract readable text from SEC filings.
    Ignores tags like script/style/head and inserts spaces at block elements
    to prevent word merging.
    """
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.ignore_depth = 0
        self.skip_tags = {"script", "style", "head", "title"}
        self.block_tags = {
            "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", 
            "li", "tr", "td", "th", "br", "option", "table", "pre"
        }

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.ignore_depth += 1
        elif tag in self.block_tags:
            if self.text_parts and not self.text_parts[-1].endswith(("\n", " ")):
                self.text_parts.append(" ")

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.ignore_depth = max(0, self.ignore_depth - 1)
        elif tag in self.block_tags:
            if self.text_parts and not self.text_parts[-1].endswith(("\n", " ")):
                self.text_parts.append(" ")

    def handle_data(self, data):
        if self.ignore_depth == 0:
            self.text_parts.append(data)

    def get_text(self) -> str:
        return "".join(self.text_parts)


def strip_html(html_content: str) -> str:
    """
    Strip HTML tags and return normalized text.
    Collapses multiple horizontal spaces and empty lines.
    """
    if not html_content:
        return ""
    parser = HTMLTextExtractor()
    parser.feed(html_content)
    text = parser.get_text()
    
    # Normalize newline characters
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple spaces and tabs to a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse multiple consecutive newlines to double newlines (paragraphs)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """
    Split text into chunks of target size (chunk_size to chunk_size + margin)
    with overlap. Aims to align with space/newline boundaries in the [chunk_size, chunk_size + margin] range.
    
    Default settings align with Document Copilot specifications:
      - chunk_size = 1000 (target length)
      - overlap = 150 (overlap length)
      - margin = 200 (allow chunks up to 1200 characters to align on boundaries)
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # If remaining text fits inside target chunk size, take it all and finish
        if start + chunk_size >= text_len:
            chunks.append(text[start:])
            break
            
        # Target end position
        target_end = start + chunk_size
        # Maximum allowed end position (to maintain 1000-1200 characters limit)
        max_end = min(start + chunk_size + 200, text_len)
        
        # Try to find a space or newline boundary in [target_end, max_end]
        end = target_end
        for i in range(target_end, max_end):
            if text[i] in (' ', '\n', '\t'):
                end = i
                break
                
        chunks.append(text[start:end])
        
        # Advance starting point based on overlap
        next_start = end - overlap
        # Prevent infinite loops if progress is stalled
        if next_start <= start:
            next_start = start + chunk_size - overlap
            
        start = next_start
        
    return chunks
