import re

with open('templates/portal/base_portal.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove Admin Roles
admin_roles_pattern = r'<a href="{% url \'portal_group_list\' %}".*?Admin Roles.*?</a>\s*'
content = re.sub(admin_roles_pattern, '', content, flags=re.DOTALL)

# 2. Add Hamburger to header
header_pattern = r'(<header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm h-16 flex items-center justify-between px-4 sm:px-6 \{% if user\.is_authenticated %\}md:hidden\{% endif %\}"(.*?)>\s*<div class="flex items-center gap-3">)'
header_replacement = r'\1\n        <button onclick="toggleSidebar()" class="md:hidden text-slate-500 hover:text-slate-900 focus:outline-none p-1 -ml-1 mr-1">\n            <i class="fas fa-bars text-[20px]"></i>\n        </button>'
content = re.sub(header_pattern, header_replacement, content)

# 3. Update sidebar classes and add backdrop
sidebar_pattern = r'(<aside class=")hidden (md:flex fixed left-0 top-0 bottom-0 h-full w-\[260px\] bg-white border-r border-slate-200 z-40 flex-col justify-between overflow-y-auto)(")'
sidebar_replacement = r'<!-- Mobile Backdrop -->\n    <div id="sidebarBackdrop" onclick="toggleSidebar()" class="fixed inset-0 bg-slate-900/50 z-40 hidden md:hidden transition-opacity opacity-0 pointer-events-none"></div>\n    \1\2 -translate-x-full md:translate-x-0 transition-transform duration-300 ease-in-out\3 id="mobileSidebar"'
content = re.sub(sidebar_pattern, sidebar_replacement, content)

# 4. Add JS toggle script before closing body
script_addition = """
    <script>
    function toggleSidebar() {
        const sidebar = document.getElementById('mobileSidebar');
        const backdrop = document.getElementById('sidebarBackdrop');
        if (!sidebar) return;
        
        const isClosed = sidebar.classList.contains('-translate-x-full');
        if (isClosed) {
            sidebar.classList.remove('-translate-x-full');
            backdrop.classList.remove('hidden', 'opacity-0', 'pointer-events-none');
            backdrop.classList.add('opacity-100');
            document.body.style.overflow = 'hidden'; // lock scroll
        } else {
            sidebar.classList.add('-translate-x-full');
            backdrop.classList.remove('opacity-100');
            backdrop.classList.add('opacity-0', 'pointer-events-none');
            setTimeout(() => backdrop.classList.add('hidden'), 300);
            document.body.style.overflow = ''; // unlock scroll
        }
    }
    </script>
"""
if 'function toggleSidebar()' not in content:
    content = content.replace('</body>', script_addition + '\n</body>')

with open('templates/portal/base_portal.html', 'w', encoding='utf-8') as f:
    f.write(content)
