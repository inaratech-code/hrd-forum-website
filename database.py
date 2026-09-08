import sqlite3
import os
import hashlib

def get_db_path():
    if os.environ.get('VERCEL') or not os.access(os.path.dirname(__file__), os.W_OK):
        return '/tmp/hrd_forum.db'
    return os.path.join(os.path.dirname(__file__), 'hrd_forum.db')

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Table: Stats
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY DEFAULT 1,
        provincial_networks INTEGER NOT NULL DEFAULT 7,
        monitored_defenders TEXT NOT NULL DEFAULT '1,200+',
        resolved_cases TEXT NOT NULL DEFAULT '150+',
        total_visitors INTEGER NOT NULL DEFAULT 14230
    )
    ''')

    # Table: Provinces (Enhanced)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS provinces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        base_city TEXT NOT NULL,
        coords_lat REAL NOT NULL,
        coords_lng REAL NOT NULL,
        coordinators_count INTEGER NOT NULL,
        helpline_phone TEXT NOT NULL,
        address TEXT NOT NULL,
        active_cases INTEGER NOT NULL DEFAULT 0,
        description TEXT NOT NULL,
        long_summary TEXT NOT NULL
    )
    ''')

    # Table: News
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date_str TEXT NOT NULL,
        image_url TEXT NOT NULL,
        category TEXT DEFAULT 'News & Updates',
        summary TEXT
    )
    ''')

    # Table: Resources
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'Document',
        format TEXT NOT NULL,
        file_size TEXT NOT NULL,
        file_url TEXT NOT NULL,
        is_gated INTEGER DEFAULT 1
    )
    ''')

    # Table: Memberships
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        province TEXT NOT NULL,
        organization TEXT,
        role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Incidents
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_name TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        province TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        details TEXT NOT NULL,
        priority TEXT DEFAULT 'High',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Admin Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Popup Announcement Config
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS popup_config (
        id INTEGER PRIMARY KEY DEFAULT 1,
        image_url TEXT NOT NULL,
        title TEXT NOT NULL,
        subtitle TEXT,
        link_url TEXT,
        link_text TEXT,
        active INTEGER DEFAULT 1
    )
    ''')

    # Table: Photo Gallery
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gallery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        image_url TEXT NOT NULL,
        category TEXT DEFAULT 'Advocacy',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Blogs & Articles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        date_str TEXT NOT NULL,
        content TEXT NOT NULL,
        image_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Videos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        embed_url TEXT NOT NULL,
        category TEXT DEFAULT 'Documentary',
        date_str TEXT NOT NULL
    )
    ''')

    # Table: Team Members
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        designation TEXT NOT NULL,
        category TEXT DEFAULT 'executive',
        bio TEXT,
        image_url TEXT,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Collaborations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS collaborations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT DEFAULT 'institutional',
        logo_url TEXT,
        blurb TEXT,
        website_url TEXT,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: News Flashes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_flashes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        link_url TEXT,
        active INTEGER DEFAULT 1,
        order_index INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table: Gated Download Leads
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gated_downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_email TEXT NOT NULL,
        resource_id INTEGER,
        resource_title TEXT NOT NULL,
        downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Seed Admin User if not exists
    cursor.execute('SELECT COUNT(*) FROM admin_users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)',
                       ('admin', hash_password('hrdadmin2026')))

    # Seed Team Members if empty
    cursor.execute('SELECT COUNT(*) FROM team_members')
    if cursor.fetchone()[0] == 0:
        team_data = [
            ('Adv. Ramesh Adhikari', 'Executive Director', 'executive', 'Lead human rights attorney with 18+ years experience advocating for civic space protections.', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80', 1),
            ('Sujan Shrestha', 'Chairperson', 'executive', 'Constitutional scholar leading strategic Supreme Court litigation.', 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&q=80', 2),
            ('Maya Tamang', 'Head of Rapid Response', 'executive', 'Coordinates emergency relocation desks across all 7 provinces.', 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&q=80', 3)
        ]
        cursor.executemany('INSERT INTO team_members (name, designation, category, bio, image_url, order_index) VALUES (?, ?, ?, ?, ?, ?)', team_data)

    # Seed Collaborations if empty
    cursor.execute('SELECT COUNT(*) FROM collaborations')
    if cursor.fetchone()[0] == 0:
        collab_data = [
            ('National Human Rights Commission (NHRC)', 'institutional', 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=400&q=80', 'Formal memorandum of understanding for joint fact-finding missions.', '#', 1),
            ('International Rights Protection Coalition', 'institutional', 'https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=400&q=80', 'Global alliance providing emergency grants for high-risk advocates.', '#', 2)
        ]
        cursor.executemany('INSERT INTO collaborations (name, category, logo_url, blurb, website_url, order_index) VALUES (?, ?, ?, ?, ?, ?)', collab_data)

    # Seed News Flashes if empty
    cursor.execute('SELECT COUNT(*) FROM news_flashes')
    if cursor.fetchone()[0] == 0:
        flash_data = [
            ('Urgent Hotline Active: Call +977-01-55511400 for emergency legal assistance across all 7 provinces.', '#', 1, 1),
            ('National Defender Convention 2026 registrations are now open for regional delegates.', '#', 1, 2)
        ]
        cursor.executemany('INSERT INTO news_flashes (text, link_url, active, order_index) VALUES (?, ?, ?, ?)', flash_data)

    # Seed Stats if empty
    cursor.execute('SELECT COUNT(*) FROM stats')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO stats (provincial_networks, monitored_defenders, resolved_cases, total_visitors) VALUES (7, "1,200+", "150+", 14230)')

    # Seed Popup Config if empty
    cursor.execute('SELECT COUNT(*) FROM popup_config')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO popup_config (id, image_url, title, subtitle, link_url, link_text, active)
            VALUES (1, 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=800&q=80',
                    'National Human Rights Defenders Convention 2026',
                    'Join regional coordinators and international legal observers in Kathmandu this September.',
                    '#', 'Register Online Now', 1)
        ''')

    # Seed Provinces if empty (with Lat/Lng and details)
    cursor.execute('SELECT COUNT(*) FROM provinces')
    if cursor.fetchone()[0] == 0:
        provinces_data = [
            ('Koshi Province Desk', 'p1', 'Biratnagar Base', 26.4525, 87.2718, 12, '+977-21-524100', 'Main Road, Ward No. 4, Biratnagar', 14,
             '12 localized monitoring human rights coordinators processing regional case interventions.',
             'The Koshi Helpdesk actively coordinates legal aid and emergency relocation across 14 Eastern districts, protecting environmental and indigenous community advocates.'),
            
            ('Madhesh Province Desk', 'p2', 'Janakpur Base', 26.7288, 85.9254, 15, '+977-41-520330', 'Station Road, Janakpurdham', 22,
             'High-density advocacy missions protecting localized civil advocates.',
             'Monitors gender-based violence, election observers, and grassroots paralegals in dense border corridor districts.'),

            ('Bagmati Province Desk (Central HQ)', 'p3', 'Kathmandu HQ', 27.6939, 85.3340, 20, '+977-01-55511400', 'Thapagaun, New Baneshwor, Kathmandu', 35,
             'Integrating central judicial lobbying with operational rapid response desks.',
             'Serves as the national command hub integrating Supreme Court litigation support, diplomatic liaison, and emergency security funds.'),

            ('Gandaki Province Desk', 'p4', 'Pokhara Base', 28.2096, 83.9856, 10, '+977-61-532190', 'New Road, Pokhara', 9,
             'Active focal points monitoring environmental and land rights defenders.',
             'Specializes in safeguarding eco-defenders, conservationists, and indigenous river basin advocates against illegal resource extraction harassment.'),

            ('Lumbini Province Desk', 'p5', 'Butwal Base', 27.7006, 83.4484, 14, '+977-71-540220', 'Traffic Chowk, Butwal', 18,
             'Cross-border coordination units assisting community paralegals.',
             'Monitors labor rights advocates, border migrant safety, and community legal aid networks across Lumbini province.'),

            ('Karnali Province Desk', 'p6', 'Surkhet Base', 28.6019, 81.6348, 8, '+977-83-521090', 'Birendranagar, Surkhet', 11,
             'Remote-access defender support networks covering highland jurisdictions.',
             'Deploys satellite-linked emergency communication units for remote mountain defenders facing geographic isolation.'),

            ('Sudurpashchim Province Desk', 'p7', 'Dhangadhi Base', 28.6852, 80.5940, 11, '+977-91-523410', 'Main Bazaar, Dhangadhi', 13,
             'Grassroots protective action programs for marginalized legal representatives.',
             'Focuses on protecting Dalit rights defenders, anti-caste discrimination campaigners, and rural legal assistants.')
        ]
        cursor.executemany('''
            INSERT INTO provinces (name, code, base_city, coords_lat, coords_lng, coordinators_count, helpline_phone, address, active_cases, description, long_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', provinces_data)

    # Seed News if empty
    cursor.execute('SELECT COUNT(*) FROM news')
    if cursor.fetchone()[0] == 0:
        news_data = [
            ('HRD Forum Launches Provincial Safety Monitoring Initiative', '12 OCT 2025', 'https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=500&q=80', 'Safety', 'Establishing 24/7 hotline desks across Koshi and Madhesh provinces for instant threat triage.'),
            ('New Policy Guidelines Released for Defender Protection', '28 SEP 2025', 'https://images.unsplash.com/photo-1450133064473-71024230f91b?w=500&q=80', 'Policy', 'A comprehensive legal framework blueprint presented to parliament for civic space protection.'),
            ('National Defender Assembly Concludes in Kathmandu', '15 AUG 2025', 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=500&q=80', 'Assembly', 'Over 300 regional delegates aligned on unified security protocols for frontline activists.')
        ]
        cursor.executemany('INSERT INTO news (title, date_str, image_url, category, summary) VALUES (?, ?, ?, ?, ?)', news_data)

    # Seed Gallery if empty
    cursor.execute('SELECT COUNT(*) FROM gallery')
    if cursor.fetchone()[0] == 0:
        gallery_data = [
            ('National Convention Keynote Speech', 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=600&q=80', 'Assemblies'),
            ('Provincial Legal Workshop in Janakpur', 'https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=600&q=80', 'Training'),
            ('Grassroots Fact-Finding Mission in Karnali', 'https://images.unsplash.com/photo-1450133064473-71024230f91b?w=600&q=80', 'Fact-Finding'),
            ('Community Human Rights Awareness Rally', 'https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=600&q=80', 'Advocacy'),
            ('Regional Legal Aid Counsel Training', 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=80', 'Training'),
            ('Environmental Rights Defenders Assembly', 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=600&q=80', 'Assemblies')
        ]
        cursor.executemany('INSERT INTO gallery (title, image_url, category) VALUES (?, ?, ?)', gallery_data)

    # Seed Resources if empty
    cursor.execute('SELECT COUNT(*) FROM resources')
    if cursor.fetchone()[0] == 0:
        resources_data = [
            ('Annual Protection Status Report 2025', 'Document', 'PDF', '4.2 MB', '#', 1),
            ('Strategic Plan 2026–2030 Blueprint', 'Document', 'PDF', '2.8 MB', '#', 1),
            ('Grassroots Security & Digital Safety Manual', 'Document', 'PDF', '3.5 MB', '#', 1),
            ('Legal Framework Guidelines for Civic Activists', 'Document', 'PDF', '1.5 MB', '#', 1)
        ]
        cursor.executemany('INSERT INTO resources (title, category, format, file_size, file_url, is_gated) VALUES (?, ?, ?, ?, ?, ?)', resources_data)

    # Seed Blogs if empty
    cursor.execute('SELECT COUNT(*) FROM blogs')
    if cursor.fetchone()[0] == 0:
        blogs_data = [
            ('Defending the Defenders: Why Provincial Safety Networks Matter', 'Adv. Ramesh Adhikari', '05 JAN 2026', 'Grassroots activists in remote districts face unique threats requiring localized legal emergency response...', 'https://images.unsplash.com/photo-1450133064473-71024230f91b?w=600&q=80'),
            ('Digital Rights & Encryption for Frontline Human Rights Workers', 'Sujan Shrestha', '18 DEC 2025', 'Protecting communications and data integrity is the first defense line against illegal digital surveillance...', 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80')
        ]
        cursor.executemany('INSERT INTO blogs (title, author, date_str, content, image_url) VALUES (?, ?, ?, ?, ?)', blogs_data)

    # Seed Videos if empty
    cursor.execute('SELECT COUNT(*) FROM videos')
    if cursor.fetchone()[0] == 0:
        videos_data = [
            ('Voices of Frontline Defenders in Nepal', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'Documentary', '2025'),
            ('Provincial Helpdesk Operations Walkthrough', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'Training', '2025')
        ]
        cursor.executemany('INSERT INTO videos (title, embed_url, category, date_str) VALUES (?, ?, ?, ?)', videos_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized with expanded schema and seed data.")
