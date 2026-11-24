"""Static-site CSP: hash the exact emitted scripts, without eval/inline handlers."""
import base64
import hashlib
import re

def secure_html(html):
    html = re.sub(r'<meta\s+data-eclipse-security="1"[^>]*>\s*', '', html)
    hashes = []
    for attributes, script in re.findall(r'<script\b([^>]*)>([\s\S]*?)</script\s*>', html, re.I):
        if not re.search(r'\bsrc\s*=', attributes, re.I):
            digest = base64.b64encode(hashlib.sha256(script.encode('utf-8')).digest()).decode()
            hashes.append("'sha256-" + digest + "'")
    policy = "; ".join([
        "default-src 'self'", "script-src 'self' " + " ".join(dict.fromkeys(hashes)),
        "script-src-attr 'none'", "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob:", "media-src 'self' blob:", "font-src 'self'",
        # GLTFLoader decodes embedded maps using ImageBitmapLoader.fetch(blob:).
        # This grants local object URLs without allowing an external API origin.
        "connect-src 'self' blob:", "frame-src 'self'", "worker-src 'self' blob:",
        "object-src 'none'", "base-uri 'none'", "form-action 'none'",
    ])
    metadata = ('<meta data-eclipse-security="1" http-equiv="Content-Security-Policy" content="'
                + policy + '">\n<meta data-eclipse-security="1" name="referrer" content="no-referrer">\n')
    tag = r'(<head\b[^>]*>)' if re.search(r'<head\b', html, re.I) else r'(<html\b[^>]*>)'
    return re.sub(tag, lambda m: m.group(1) + metadata, html, count=1, flags=re.I)
