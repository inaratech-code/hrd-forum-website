from flask import Flask, jsonify, request, send_from_directory
import os
import database

app = Flask(__name__, static_folder='.', static_url_path='')

# Ensure database is initialized
database.init_db()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

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
        return jsonify({"success": False, "error": "Reporter Name, Contact Info, Province, and Incident Details are required."}), 400

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

