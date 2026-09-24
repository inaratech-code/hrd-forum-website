import re

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_root = """    :root {
        /* User Palette */
        --primary-blue: #0130BE;
        --secondary-teal: #2085AB;
        --bright-blue: #0288D1;
        --navy: #0B192C;
        --navy-light: #1E2B3D;
        --orange: #F59E0B;
        --red: #DC2626;
        --white: #FFFFFF;
        --light-bg: #F1F5F9;
        
        --text-dark: #172033;
        --text-light: #FFFFFF;
        --text-muted: #64748B;

        /* Remapped Existing Project Variables (preserving functionality) */
        --bg-white: var(--white);
        --bg-light: var(--light-bg);
        --bg-slate: var(--light-bg);
        --card-bg: var(--white);
        --border-color: rgba(11, 25, 44, 0.08);
        
        --text-body: var(--text-dark);
  
        --primary-navy: var(--navy);
        --royal-blue: var(--primary-blue);
        --royal-blue-hover: var(--bright-blue);
        --cerulean-blue: var(--bright-blue);
        --dark-slate-base: var(--navy);
        --emergency-red: var(--red);
        --emergency-red-hover: #B91C1C;
  
        --cobalt-blue: var(--primary-blue);
        --cobalt-accent: var(--bright-blue);
        --cobalt-light: #E1F5FE;
  
        --deep-teal: var(--secondary-teal);
        --deep-teal-hover: var(--secondary-teal);
        --deep-teal-light: #E1F5FE;
  
        --action-crimson: var(--red);
        --action-crimson-hover: #B91C1C;
        --amber-gold: var(--orange);
        --amber-gold-hover: #d97706;
  
        --shadow-sm: 0 2px 10px rgba(11, 25, 44, 0.03);
        --shadow-md: 0 8px 30px rgba(11, 25, 44, 0.06);
        --shadow-lg: 0 20px 50px rgba(11, 25, 44, 0.1);
        --radius: 16px;
    }"""

# regex to find and replace the :root block
pattern = r'[ ]*:root\s*\{.*?\--radius:\s*16px;\s*\}'
content = re.sub(pattern, new_root, content, flags=re.DOTALL)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
