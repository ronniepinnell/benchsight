#!/usr/bin/env python3
"""Convert markdown files to styled HTML for BenchSight documentation."""

import os
import re
from pathlib import Path

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - BenchSight Docs</title>
<style>
:root {{
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --accent: #58a6ff;
  --accent2: #3fb950;
  --code-bg: #0d1117;
  --warn: #d29922;
  --danger: #f85149;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  font-size: 14px;
}}
.container {{ max-width: 900px; margin: 0 auto; padding: 20px 40px; }}
header {{
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 15px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}}
header .container {{ display: flex; justify-content: space-between; align-items: center; }}
header h1 {{ font-size: 18px; color: var(--accent); }}
header nav a {{
  color: var(--text-muted);
  text-decoration: none;
  margin-left: 20px;
  font-size: 13px;
}}
header nav a:hover {{ color: var(--accent); }}
main {{ padding: 30px 0; }}
h1, h2, h3, h4, h5, h6 {{ color: var(--text); margin: 20px 0 10px; }}
h1 {{ font-size: 28px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }}
h2 {{ font-size: 22px; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-top: 30px; }}
h3 {{ font-size: 18px; }}
h4 {{ font-size: 15px; color: var(--accent); }}
p {{ margin: 10px 0; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
code {{
  font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  border: 1px solid var(--border);
}}
pre {{
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 15px;
  overflow-x: auto;
  margin: 15px 0;
}}
pre code {{ border: none; padding: 0; }}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}}
th, td {{
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}}
th {{ background: var(--surface); color: var(--accent); font-weight: 600; }}
tr:nth-child(even) {{ background: rgba(255,255,255,0.02); }}
ul, ol {{ margin: 10px 0 10px 25px; }}
li {{ margin: 5px 0; }}
blockquote {{
  border-left: 3px solid var(--accent);
  padding-left: 15px;
  margin: 15px 0;
  color: var(--text-muted);
}}
hr {{ border: none; border-top: 1px solid var(--border); margin: 30px 0; }}
.toc {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 15px 20px;
  margin: 20px 0;
}}
.toc h4 {{ margin-top: 0; color: var(--accent2); }}
.toc ul {{ list-style: none; margin-left: 0; }}
.toc li {{ margin: 5px 0; }}
.toc a {{ color: var(--text-muted); }}
.note {{ background: rgba(88,166,255,0.1); border-left: 3px solid var(--accent); padding: 10px 15px; margin: 15px 0; border-radius: 0 6px 6px 0; }}
.warning {{ background: rgba(210,153,34,0.1); border-left: 3px solid var(--warn); padding: 10px 15px; margin: 15px 0; border-radius: 0 6px 6px 0; }}
.danger {{ background: rgba(248,81,73,0.1); border-left: 3px solid var(--danger); padding: 10px 15px; margin: 15px 0; border-radius: 0 6px 6px 0; }}
footer {{ border-top: 1px solid var(--border); padding: 20px 0; margin-top: 40px; text-align: center; color: var(--text-muted); font-size: 12px; }}
</style>
</head>
<body>
<header>
<div class="container">
<h1>📊 BenchSight Docs</h1>
<nav>
<a href="TRACKER_INDEX.html">Index</a>
<a href="TRACKER_REQUIREMENTS.html">Requirements</a>
<a href="SUPABASE_SETUP_GUIDE.html">Supabase</a>
<a href="TRACKER_DEVELOPER_HANDOFF.html">Dev Handoff</a>
</nav>
</div>
</header>
<main>
<div class="container">
{content}
</div>
</main>
<footer>
<div class="container">
BenchSight Tracker Documentation • Generated {date}
</div>
</footer>
</body>
</html>
'''

def md_to_html(md_content: str) -> str:
    """Convert markdown to HTML with basic formatting."""
    html = md_content
    
    # Escape HTML entities first (but not in code blocks)
    # Skip this for now as it would break intended HTML
    
    # Code blocks (``` ... ```)
    def code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        # Escape < and > in code
        code = code.replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    html = re.sub(r'```(\w*)\n(.*?)```', code_block, html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Headers
    html = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
    
    # Tables
    def convert_table(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        
        # Header row
        headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        html_table = '<table>\n<thead>\n<tr>'
        for h in headers:
            html_table += f'<th>{h}</th>'
        html_table += '</tr>\n</thead>\n<tbody>\n'
        
        # Data rows (skip separator line)
        for line in lines[2:]:
            if line.strip() and '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                html_table += '<tr>'
                for cell in cells:
                    html_table += f'<td>{cell}</td>'
                html_table += '</tr>\n'
        
        html_table += '</tbody>\n</table>'
        return html_table
    
    # Match table blocks
    html = re.sub(r'(\|[^\n]+\|\n)+', convert_table, html)
    
    # Lists (basic support)
    lines = html.split('\n')
    in_ul = False
    in_ol = False
    result_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Unordered list
        if re.match(r'^[-*+]\s+', stripped):
            if not in_ul:
                result_lines.append('<ul>')
                in_ul = True
            content = re.sub(r'^[-*+]\s+', '', stripped)
            result_lines.append(f'<li>{content}</li>')
        # Ordered list
        elif re.match(r'^\d+\.\s+', stripped):
            if not in_ol:
                result_lines.append('<ol>')
                in_ol = True
            content = re.sub(r'^\d+\.\s+', '', stripped)
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            
            # Paragraphs
            if stripped and not stripped.startswith('<'):
                result_lines.append(f'<p>{line}</p>')
            else:
                result_lines.append(line)
    
    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')
    
    html = '\n'.join(result_lines)
    
    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>\s*(<h[1-6]>)', r'\1', html)
    html = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*(<table>)', r'\1', html)
    html = re.sub(r'(</table>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*(<pre>)', r'\1', html)
    html = re.sub(r'(</pre>)\s*</p>', r'\1', html)
    html = re.sub(r'<p>\s*(<ul>)', r'\1', html)
    html = re.sub(r'<p>\s*(<ol>)', r'\1', html)
    html = re.sub(r'<p>\s*(<hr>)', r'\1', html)
    
    return html

def convert_file(md_path: Path, output_dir: Path):
    """Convert a single markdown file to HTML."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first H1 or filename
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else md_path.stem
    
    # Convert content
    html_content = md_to_html(md_content)
    
    # Fill template
    from datetime import datetime
    full_html = HTML_TEMPLATE.format(
        title=title,
        content=html_content,
        date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    
    # Write output
    output_path = output_dir / (md_path.stem + '.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f'Converted: {md_path.name} -> {output_path.name}')
    return output_path

def main():
    docs_dir = Path('/home/claude/benchsight/project/docs')
    html_dir = docs_dir / 'html'
    html_dir.mkdir(exist_ok=True)
    
    # Convert tracker-related docs
    tracker_docs = [
        'TRACKER_REQUIREMENTS.md',
        'TRACKER_DEVELOPER_HANDOFF.md',
        'SUPABASE_SETUP_GUIDE.md',
        'TRACKING_TEMPLATE_ANALYSIS.md'
    ]
    
    for doc in tracker_docs:
        md_path = docs_dir / doc
        if md_path.exists():
            convert_file(md_path, html_dir)
        else:
            print(f'Not found: {doc}')
    
    print(f'\nHTML files generated in: {html_dir}')

if __name__ == '__main__':
    main()
