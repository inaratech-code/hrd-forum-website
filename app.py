from flask import Flask, jsonify, request, send_from_directory
import os
import database

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Ensure DB is initialized
database.init_db()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory('static', 'admin.html')

# --- PUBLIC APIs ---

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = database.get_db()
    stats = conn.execute('SELECT * FROM stats WHERE id = 1').fetchone()
    conn.close()
    if stats:
        return jsonify(dict(stats))
    return jsonify({
        "provincial_networks": 7,
        "monitored_defenders": "1,200+",
        "resolved_cases": "150+",
        "total_visitors": 14230
    })

@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM provinces ORDER BY id ASC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/province/<int:prov_id>', methods=['GET'])
def get_province_detail(prov_id):
    conn = database.get_db()
    row = conn.execute('SELECT * FROM provinces WHERE id = ?', (prov_id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Province not found"}), 404

@app.route('/api/news', methods=['GET'])
def get_news():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM news ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/resources', methods=['GET'])
def get_resources():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM resources ORDER BY id ASC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/popup', methods=['GET'])
def get_popup():
    conn = database.get_db()
    row = conn.execute('SELECT * FROM popup_config WHERE id = 1').fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"active": 0})

@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM gallery ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/blogs', methods=['GET'])
def get_blogs():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM blogs ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/videos', methods=['GET'])
def get_videos():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM videos ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# --- GATED DOWNLOAD LOGIC ---

@app.route('/api/resource/download-access', methods=['POST'])
def record_gated_download():
    data = request.get_json() or {}
    user_name = data.get('user_name', '').strip()
    user_email = data.get('user_email', '').strip()
    resource_id = data.get('resource_id')

    if not user_name or not user_email or not resource_id:
        return jsonify({"success": False, "error": "Name, Email, and Resource selection are required."}), 400

    conn = database.get_db()
    cursor = conn.cursor()
    resource = cursor.execute('SELECT * FROM resources WHERE id = ?', (resource_id,)).fetchone()
    if not resource:
        conn.close()
        return jsonify({"success": False, "error": "Resource document not found."}), 404

    res_dict = dict(resource)
    cursor.execute('''
        INSERT INTO gated_downloads (user_name, user_email, resource_id, resource_title)
        VALUES (?, ?, ?, ?)
    ''', (user_name, user_email, resource_id, res_dict['title']))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "download_url": res_dict['file_url'],
        "message": f"Thank you, {user_name}. Your download has been authorized!"
    })

# --- FORM SUBMISSIONS ---

@app.route('/api/membership', methods=['POST'])
def submit_membership():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    province = data.get('province', '').strip()
    organization = data.get('organization', '').strip()
    role = data.get('role', '').strip()

    if not full_name or not email or not province:
        return jsonify({"success": False, "error": "Full Name, Email, and Province are required fields."}), 400

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO memberships (full_name, email, phone, province, organization, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (full_name, email, phone, province, organization, role))
    membership_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "id": membership_id,
        "message": "Membership application submitted successfully! Our team will contact you shortly."
    }), 201

@app.route('/api/incident', methods=['POST'])
def report_incident():
    data = request.get_json() or {}
    reporter_name = data.get('reporter_name', '').strip()
    contact_info = data.get('contact_info', '').strip()
    province = data.get('province', '').strip()
    incident_type = data.get('incident_type', 'Urgent Support').strip()
    details = data.get('details', '').strip()
    priority = data.get('priority', 'High').strip()

    if not reporter_name or not contact_info or not province or not details:
        return jsonify({"success": False, "error": "Reporter Name, Contact Info, Province, and Details are required."}), 400

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incidents (reporter_name, contact_info, province, incident_type, details, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (reporter_name, contact_info, province, incident_type, details, priority))
    incident_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "id": incident_id,
        "message": "Incident report logged securely. The regional helpdesk team has been alerted."
    }), 201

# --- ADMIN APIs ---

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400

    pwd_hash = database.hash_password(password)
    conn = database.get_db()
    user = conn.execute('SELECT * FROM admin_users WHERE username = ? AND password_hash = ?',
                         (username, pwd_hash)).fetchone()
    conn.close()

    if user:
        return jsonify({
            "success": True,
            "token": "hrd_session_admin_secure_token_2026",
            "username": username
        })
    return jsonify({"success": False, "error": "Invalid admin credentials"}), 401

@app.route('/api/admin/popup', methods=['POST'])
def update_popup():
    data = request.get_json() or {}
    image_url = data.get('image_url', '').strip()
    title = data.get('title', '').strip()
    subtitle = data.get('subtitle', '').strip()
    link_url = data.get('link_url', '').strip()
    link_text = data.get('link_text', 'Learn More').strip()
    active = 1 if data.get('active') else 0

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO popup_config (id, image_url, title, subtitle, link_url, link_text, active)
        VALUES (1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            image_url=excluded.image_url,
            title=excluded.title,
            subtitle=excluded.subtitle,
            link_url=excluded.link_url,
            link_text=excluded.link_text,
            active=excluded.active
    ''', (image_url, title, subtitle, link_url, link_text, active))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Popup banner updated successfully!"})

@app.route('/api/admin/news', methods=['POST'])
def add_news():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    date_str = data.get('date_str', '').strip()
    image_url = data.get('image_url', '').strip()
    category = data.get('category', 'News & Updates').strip()
    summary = data.get('summary', '').strip()

    if not title or not date_str or not image_url:
        return jsonify({"success": False, "error": "Title, Date, and Image URL are required"}), 400

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news (title, date_str, image_url, category, summary)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, date_str, image_url, category, summary))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "News item published successfully!"})

@app.route('/api/admin/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM news WHERE id = ?', (news_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "News item deleted."})

@app.route('/api/admin/gallery', methods=['POST'])
def add_gallery():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    image_url = data.get('image_url', '').strip()
    category = data.get('category', 'Advocacy').strip()

    if not title or not image_url:
        return jsonify({"success": False, "error": "Title and Image URL required"}), 400

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO gallery (title, image_url, category) VALUES (?, ?, ?)',
                   (title, image_url, category))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Photo added to gallery."})

@app.route('/api/admin/gallery/<int:item_id>', methods=['DELETE'])
def delete_gallery(item_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gallery WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Photo deleted from gallery."})

@app.route('/api/admin/resources', methods=['POST'])
def add_resource():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    category = data.get('category', 'Document').strip()
    fmt = data.get('format', 'PDF').strip()
    file_size = data.get('file_size', '1.0 MB').strip()
    file_url = data.get('file_url', '#').strip()
    is_gated = 1 if data.get('is_gated', True) else 0

    if not title or not file_url:
        return jsonify({"success": False, "error": "Title and File URL required"}), 400

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resources (title, category, format, file_size, file_url, is_gated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, category, fmt, file_size, file_url, is_gated))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Resource published."})

@app.route('/api/admin/resources/<int:res_id>', methods=['DELETE'])
def delete_resource(res_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM resources WHERE id = ?', (res_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Resource deleted."})

@app.route('/api/admin/gated-logs', methods=['GET'])
def get_gated_logs():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM gated_downloads ORDER BY downloaded_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/memberships', methods=['GET'])
def list_memberships():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM memberships ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/incidents', methods=['GET'])
def list_incidents():
    conn = database.get_db()
    rows = conn.execute('SELECT * FROM incidents ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    print("Starting HRD Forum Nepal Flask Backend on http://127.0.0.1:5050 ...")
    app.run(host='0.0.0.0', port=5050, debug=True)
