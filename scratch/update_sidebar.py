import re

with open('templates/portal/base_portal.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_sidebar = """
<!-- Top Navigation Bar (Mobile only or simplified for desktop since sidebar is fixed) -->
<header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm h-16 flex items-center justify-between px-4 sm:px-6 {% if user.is_authenticated %}md:hidden{% endif %}">
    <div class="flex items-center gap-3">
        <a href="{% url 'portal_dashboard' %}" class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
                <i class="fas fa-shield-alt text-[14px]"></i>
            </div>
            <span class="font-semibold text-[15px] text-slate-900 leading-tight">HRD Forum</span>
        </a>
    </div>
    <div class="flex items-center gap-3">
        <a href="/" target="_blank" class="flex items-center gap-2 text-[12px] font-semibold text-slate-600 hover:text-blue-700 bg-slate-50 hover:bg-blue-50 px-3 py-1.5 rounded-lg border border-slate-200 transition">
            <i class="fas fa-globe text-blue-500"></i>
            <span>Public Site</span>
        </a>
    </div>
</header>

<div class="flex flex-1 relative w-full max-w-full">
    {% if user.is_authenticated %}
    <!-- Fixed Sidebar for MD3 Theme -->
    <aside class="hidden md:flex fixed left-0 top-0 bottom-0 h-full w-[260px] bg-white border-r border-slate-200 z-40 flex-col justify-between overflow-y-auto">
        <div class="flex flex-col">
            <!-- Logo Header -->
            <div class="h-16 px-4 flex items-center justify-between border-b border-slate-200">
                <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
                        <i class="fas fa-shield-alt text-[14px]"></i>
                    </div>
                    <div class="flex flex-col">
                        <span class="font-semibold text-[15px] text-slate-900 leading-tight">HRD Forum</span>
                        <span class="text-[10px] font-mono font-semibold text-blue-600 uppercase tracking-wider">Portal OS</span>
                    </div>
                </div>
                <div class="flex items-center gap-1">
                    <a href="/" target="_blank" title="View Public Site" class="text-slate-400 hover:text-blue-600 rounded-lg p-1 transition">
                        <i class="fas fa-external-link-alt text-[14px]"></i>
                    </a>
                </div>
            </div>

            <!-- Navigation -->
            <nav class="flex flex-col px-3 py-4 gap-5">
                
                <!-- Overview -->
                <div class="flex flex-col gap-0.5">
                    <span class="px-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">Overview</span>
                    <a href="{% url 'portal_dashboard' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if request.resolver_match.url_name == 'portal_dashboard' %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-chart-pie text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Dashboard</span>
                    </a>
                </div>

                <!-- Home Page -->
                <div class="flex flex-col gap-0.5">
                    <span class="px-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">Home Page</span>
                    <a href="{% url 'portal_news_flash_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'news-flashes' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-bolt text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">News Flashes (Marquee)</span>
                    </a>
                    <a href="{% url 'portal_popup_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'popups' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-window-restore text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Announcement Popups</span>
                    </a>
                    <a href="{% url 'portal_news_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'news' in request.path and 'flashes' not in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-newspaper text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">News</span>
                    </a>
                    <a href="{% url 'portal_updates_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'updates' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-bullhorn text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Updates</span>
                    </a>
                    <a href="{% url 'portal_province_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'provinces' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-map-marked-alt text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Provincial Desks</span>
                    </a>
                </div>

                <!-- About Page -->
                <div class="flex flex-col gap-0.5">
                    <span class="px-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">About Page</span>
                    <a href="{% url 'portal_site_settings' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'site-settings' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-globe text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Site Settings</span>
                    </a>
                    <a href="{% url 'portal_team_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'team' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-users-cog text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Team Members</span>
                    </a>
                    <a href="{% url 'portal_collaboration_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'collaborations' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-handshake text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Collaborations</span>
                    </a>
                </div>

                <!-- Library -->
                <div class="flex flex-col gap-0.5">
                    <span class="px-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">Library</span>
                    <a href="{% url 'portal_gallery_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'gallery' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-images text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Photo Gallery</span>
                    </a>
                    <a href="{% url 'portal_resource_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'resources' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-file-alt text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Resource Archive</span>
                    </a>
                </div>

                <!-- Operations -->
                <div class="flex flex-col gap-0.5">
                    <span class="px-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">Operations</span>
                    <a href="{% url 'portal_incidents_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'incidents' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-exclamation-triangle text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Critical Incidents</span>
                    </a>
                    <a href="{% url 'portal_memberships_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'memberships' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-id-card text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Membership Apps</span>
                    </a>
                    <a href="{% url 'portal_contributions_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'support-contributions' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-hand-holding-heart text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Support Contributions</span>
                    </a>
                </div>

                <!-- System -->
                <div class="flex flex-col gap-0.5">
                    <span class="px-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1">System</span>
                    <a href="{% url 'portal_user_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'users' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-user-shield text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Admin Accounts</span>
                    </a>
                    <a href="{% url 'portal_group_list' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'groups' in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-user-tag text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">Admin Roles</span>
                    </a>
                    <a href="{% url 'portal_settings' %}" class="flex items-center gap-2.5 px-3 py-2 rounded-lg transition-colors text-[13px] font-medium {% if 'settings' in request.path and 'site-settings' not in request.path %}bg-blue-50 text-blue-700 font-semibold{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                        <i class="fas fa-cog text-[16px] w-[18px] text-center"></i>
                        <span class="flex-1">My Password</span>
                    </a>
                </div>
            </nav>
        </div>

        <!-- Footer / User info & Logout -->
        <div class="p-3 border-t border-slate-200 space-y-1 bg-slate-50/50">
            <div class="flex items-center gap-2.5 px-2 py-1.5">
                <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-[12px] font-bold">
                    {{ request.user.username.0|upper|default:"A" }}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-[13px] font-semibold text-slate-800 truncate leading-tight">{{ request.user.username }}</p>
                    <p class="text-[11px] text-blue-600 font-medium truncate">Administrator</p>
                </div>
            </div>
            <form method="post" action="{% url 'portal_logout' %}" class="w-full">
                {% csrf_token %}
                <button type="submit" class="flex items-center gap-2 w-full px-2.5 py-2 rounded-lg text-[13px] font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors">
                    <i class="fas fa-sign-out-alt text-[18px] w-[18px] text-center"></i>
                    Sign out
                </button>
            </form>
        </div>
    </aside>
    {% endif %}

    <!-- Main Content Area -->
    <main class="flex-1 w-full flex flex-col {% if user.is_authenticated %}md:ml-[260px]{% endif %} min-h-[100dvh]">
        <div class="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1280px] w-full mx-auto space-y-6">
"""

start_pattern = r'<!-- Top Navigation Bar -->'
end_pattern = r'<!-- Toast / Flash Notifications -->'

content_split = re.split(start_pattern, content)
pre_header = content_split[0]
post_header = re.split(end_pattern, content_split[1], maxsplit=1)[1]

# Reconstruct ensuring we close the new `.flex-1.flex.flex-col` and `.flex.flex-1` wrappers we opened around the footer.
final_content = pre_header + new_sidebar + '            <!-- Toast / Flash Notifications -->' + post_header

# Modify footer to close our newly added divs
footer_pattern = r'</footer>'
final_content = re.sub(footer_pattern, '</footer>\n    </div>\n</div>', final_content)

with open('templates/portal/base_portal.html', 'w', encoding='utf-8') as f:
    f.write(final_content)
