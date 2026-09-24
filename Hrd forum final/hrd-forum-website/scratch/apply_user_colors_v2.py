import re

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_root = """    :root {
        /* User Palette */
        --primary-blue: #0130BE;
        --secondary-teal: #2085AB;
        --light-blue: #D5ECFF;
        --white: #FFFFFF;
        --dark-text: #172033;

        /* Remapped Existing Project Variables */
        --bg-white: var(--white);
        --bg-light: var(--light-blue);
        --bg-slate: var(--light-blue);
        --card-bg: var(--white);
        --border-color: rgba(23, 32, 51, 0.08);
        
        --text-dark: var(--dark-text);
        --text-body: var(--dark-text);
        --text-muted: #64748B;
        --text-light: #FFFFFF;
  
        --primary-navy: var(--primary-blue);
        --royal-blue: var(--primary-blue);
        --royal-blue-hover: var(--secondary-teal);
        --cerulean-blue: var(--secondary-teal);
        --dark-slate-base: var(--dark-text);
        --emergency-red: #DC2626;
        --emergency-red-hover: #B91C1C;
  
        --cobalt-blue: var(--primary-blue);
        --cobalt-accent: var(--secondary-teal);
        --cobalt-light: var(--light-blue);
  
        --deep-teal: var(--secondary-teal);
        --deep-teal-hover: var(--primary-blue);
        --deep-teal-light: var(--light-blue);
  
        --action-crimson: #DC2626;
        --action-crimson-hover: #B91C1C;
        --amber-gold: #F59E0B;
        --amber-gold-hover: #d97706;
  
        --shadow-sm: 0 2px 10px rgba(1, 48, 190, 0.04);
        --shadow-md: 0 8px 30px rgba(1, 48, 190, 0.08);
        --shadow-lg: 0 20px 50px rgba(1, 48, 190, 0.12);
        --radius: 16px;
    }"""

pattern = r'[ ]*:root\s*\{.*?\--radius:\s*16px;\s*\}'
content = re.sub(pattern, new_root, content, flags=re.DOTALL)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
