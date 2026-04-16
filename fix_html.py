import re

with open('refactor.py', 'r', encoding='utf-8') as f:
    refactor_code = f.read()

# get the NEW_HTML part
new_html_match = re.search(r'NEW_HTML\s*=\s*\"\"\"(.*?)(\"\"\"\s*\n)', refactor_code, re.DOTALL)
new_html = new_html_match.group(1)

with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Grab only the last script block starting with <script> and // --- LOGIC ---
js_match = re.search(r'(<script>\s*// --- LOGIC ---.*?</script>)', text, re.DOTALL)
if js_match:
    js_content = js_match.group(1)
    final_html = new_html + f"\n    {js_content}\n</body>\n</html>"
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("Fixed index.html!")
else:
    print("Could not find logic script.")
