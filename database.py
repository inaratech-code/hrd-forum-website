import sqlite3
import os

def get_db_path():
    if os.environ.get('VERCEL') or not os.access(os.path.dirname(__file__), os.W_OK):
        return '/tmp/hrd_forum.db'
    return os.path.join(os.path.dirname(__file__), 'hrd_forum.db')

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY DEFAULT 1,
        provincial_networks INTEGER NOT NULL DEFAULT 7,
        monitored_defenders TEXT NOT NULL DEFAULT '1,200+',
        resolved_cases TEXT NOT NULL DEFAULT '150+',
        total_visitors INTEGER NOT NULL DEFAULT 14230
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS provinces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        base_city TEXT NOT NULL,
        coordinators_count INTEGER NOT NULL,
        description TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date_str TEXT NOT NULL,
        image_url TEXT NOT NULL,
        category TEXT DEFAULT 'News & Updates'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        format TEXT NOT NULL,
        file_size TEXT NOT NULL,
        file_url TEXT NOT NULL
    )
    ''')

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

    # Seed initial data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM stats')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO stats (provincial_networks, monitored_defenders, resolved_cases, total_visitors) VALUES (7, "1,200+", "150+", 14230)')

    cursor.execute('SELECT COUNT(*) FROM provinces')
    if cursor.fetchone()[0] == 0:
        provinces_data = [
            ('Koshi Province Desk', 'Biratnagar Base', 12, '12 localized monitoring human rights coordinators processing regional case interventions.'),
            ('Madhesh Province Desk', 'Janakpur Base', 15, 'High-density advocacy missions protecting localized civil advocates.'),
            ('Bagmati Province Desk', 'Kathmandu HQ', 20, 'Integrating central judicial lobbying with operational rapid response desks.'),
            ('Gandaki Province Desk', 'Pokhara Base', 10, 'Active focal points monitoring environmental and land rights defenders.'),
            ('Lumbini Province Desk', 'Butwal Base', 14, 'Cross-border coordination units assisting community paralegals.'),
            ('Karnali Province Desk', 'Surkhet Base', 8, 'Remote-access defender support networks covering highland jurisdictions.'),
            ('Sudurpashchim Province Desk', 'Dhangadhi Base', 11, 'Grassroots protective action programs for marginalized legal representatives.')
        ]
        cursor.executemany('INSERT INTO provinces (name, base_city, coordinators_count, description) VALUES (?, ?, ?, ?)', provinces_data)

    cursor.execute('SELECT COUNT(*) FROM news')
    if cursor.fetchone()[0] == 0:
        news_data = [
            ('HRD Forum Launches Provincial Safety Monitoring Initiative', '12 OCT 2025', 'https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=160&q=80', 'Safety'),
            ('New Policy Guidelines Released for Defender Protection', '28 SEP 2025', 'https://images.unsplash.com/photo-1450133064473-71024230f91b?w=160&q=80', 'Policy'),
            ('National Defender Assembly Concludes in Kathmandu', '15 AUG 2025', 'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=160&q=80', 'Assembly')
        ]
        cursor.executemany('INSERT INTO news (title, date_str, image_url, category) VALUES (?, ?, ?, ?)', news_data)

    cursor.execute('SELECT COUNT(*) FROM resources')
    if cursor.fetchone()[0] == 0:
        resources_data = [
            ('Annual Report 2025', 'PDF', '4.2 MB', '#'),
            ('Strategic Plan 2026–2030', 'PDF', '2.8 MB', '#'),
            ('Policy & Guidelines', 'PDF', '1.5 MB', '#'),
            ('Grassroots Safety Manual', 'PDF', '3.1 MB', '#')
        ]
        cursor.executemany('INSERT INTO resources (title, format, file_size, file_url) VALUES (?, ?, ?, ?)', resources_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
