import re

with open('templates/portal/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix Page Header layout for mobile
header_pattern = r'<div class="flex items-center justify-between">'
header_replacement = r'<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">'
content = content.replace(header_pattern, header_replacement, 1)

# 2. Fix KPI strip grid for mobile (from 2 columns to 1 column on smallest screens)
kpi_grid_pattern = r'<div class="grid gap-3 grid-cols-2 sm:grid-cols-4">'
kpi_grid_replacement = r'<div class="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">'
content = content.replace(kpi_grid_pattern, kpi_grid_replacement, 1)

with open('templates/portal/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
