import re

# 1. Update settings.html to use 'form' instead of 'password_form'
with open('templates/portal/settings.html', 'r', encoding='utf-8') as f:
    settings_content = f.read()

settings_content = settings_content.replace('password_form', 'form')
settings_content = settings_content.replace('Change Password', 'Change / Reset Password')

with open('templates/portal/settings.html', 'w', encoding='utf-8') as f:
    f.write(settings_content)


# 2. Update base_portal.html to rename "My Password" to "Change / Reset Password"
with open('templates/portal/base_portal.html', 'r', encoding='utf-8') as f:
    base_content = f.read()

base_content = base_content.replace('<span class="flex-1">My Password</span>', '<span class="flex-1">Change / Reset Password</span>')

with open('templates/portal/base_portal.html', 'w', encoding='utf-8') as f:
    f.write(base_content)
