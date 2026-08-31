import html
import re

def render_citations(text: str) -> str:
    if not text:
        return ""

    escaped = html.escape(text)

    pattern = re.compile(r'\(Citation:\s*&quot;(.*?)&quot;\)')

    def replace(match: re.Match) -> str:
        quote = match.group(1)
        return (
            f'<span title="{quote}" '
            'style="cursor: help; border-bottom: 1px dotted #888; '
            'padding: 0 2px;">📝</span>'
        )

    return pattern.sub(replace, escaped)


def render_list_with_citations(items: list[str]) -> str:
    html_bullets = ""

    for item in items:
        rendered_item = render_citations(item)
        
        html_bullets += f"<li>{rendered_item}</li>"

    return f"<ul>{html_bullets}</ul>"