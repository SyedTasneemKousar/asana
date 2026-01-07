"""
Simple web-based database viewer for Asana simulation database.
Run this after generation completes to explore the data.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import json
from urllib.parse import urlparse, parse_qs
import html

class DatabaseViewer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_index_page().encode())
        elif path == '/api/tables':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.get_tables()).encode())
        elif path == '/api/table':
            table_name = query.get('name', [''])[0]
            limit = int(query.get('limit', ['100'])[0])
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.get_table_data(table_name, limit)).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_tables(self):
        conn = sqlite3.connect('output/asana_simulation.sqlite')
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            tables.append({'name': table_name, 'count': count})
        conn.close()
        return tables
    
    def get_table_data(self, table_name, limit=100):
        conn = sqlite3.connect('output/asana_simulation.sqlite')
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = []
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            rows.append(dict(row))
        conn.close()
        return {'columns': columns, 'rows': rows, 'count': len(rows)}
    
    def get_index_page(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Asana Database Viewer</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 12px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 { 
            color: #333; 
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        .stats {
            display: flex;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            flex: 1;
            min-width: 150px;
        }
        .stat-card h3 {
            margin: 0;
            font-size: 0.9em;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            margin-top: 5px;
        }
        .table-list { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); 
            gap: 15px; 
            margin: 30px 0; 
        }
        .table-card { 
            padding: 20px; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px; 
            cursor: pointer; 
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .table-card:hover { 
            transform: translateY(-5px);
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        .table-card.empty {
            opacity: 0.5;
            background: #f0f0f0;
        }
        .table-card h3 { 
            margin: 0 0 8px 0; 
            color: #333;
            font-size: 1.1em;
        }
        .table-card .count { 
            color: #667eea; 
            font-size: 1.3em;
            font-weight: bold;
        }
        .table-card.empty .count {
            color: #999;
        }
        #data-view { 
            margin-top: 40px; 
        }
        .data-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .data-header h2 {
            margin: 0;
            color: #333;
        }
        .back-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .back-btn:hover {
            background: #5568d3;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        th { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 12px; 
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        td { 
            padding: 12px; 
            border-bottom: 1px solid #e0e0e0; 
        }
        tr:hover { 
            background: #f8f9ff; 
        }
        tr:nth-child(even) {
            background: #fafafa;
        }
        tr:nth-child(even):hover {
            background: #f8f9ff;
        }
        .loading { 
            text-align: center; 
            padding: 40px; 
            color: #666;
            font-size: 1.2em;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        .search-box {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 20px;
        }
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Asana Simulation Database Viewer</h1>
            <p class="subtitle">Explore the generated seed data for the Asana RL environment</p>
            <div class="stats" id="stats">
                <div class="stat-card">
                    <h3>Total Tables</h3>
                    <div class="value" id="total-tables">-</div>
                </div>
                <div class="stat-card">
                    <h3>Total Rows</h3>
                    <div class="value" id="total-rows">-</div>
                </div>
            </div>
        </div>
        <input type="text" class="search-box" id="search" placeholder="Search tables..." onkeyup="filterTables()">
        <div id="tables" class="table-list">
            <div class="loading">Loading tables...</div>
        </div>
        <div id="data-view"></div>
    </div>
    <script>
        let allTables = [];
        
        async function loadTables() {
            const response = await fetch('/api/tables');
            allTables = await response.json();
            updateStats();
            renderTables();
        }
        
        function updateStats() {
            const totalTables = allTables.length;
            const totalRows = allTables.reduce((sum, t) => sum + t.count, 0);
            document.getElementById('total-tables').textContent = totalTables;
            document.getElementById('total-rows').textContent = totalRows.toLocaleString();
        }
        
        function renderTables(tables = allTables) {
            const container = document.getElementById('tables');
            if (tables.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">(empty)</div><p>No tables found matching your search</p></div>';
                return;
            }
            container.innerHTML = tables.map(t => `
                <div class="table-card ${t.count === 0 ? 'empty' : ''}" onclick="loadTable('${t.name}')">
                    <h3>${t.name}</h3>
                    <div class="count">${t.count.toLocaleString()} ${t.count === 1 ? 'row' : 'rows'}</div>
                </div>
            `).join('');
        }
        
        function filterTables() {
            const search = document.getElementById('search').value.toLowerCase();
            const filtered = allTables.filter(t => t.name.toLowerCase().includes(search));
            renderTables(filtered);
        }
        
        async function loadTable(tableName) {
            document.getElementById('data-view').innerHTML = '<div class="loading">Loading data...</div>';
            const response = await fetch(`/api/table?name=${tableName}&limit=200`);
            const data = await response.json();
            
            if (data.rows.length === 0) {
                document.getElementById('data-view').innerHTML = `
                    <div class="data-header">
                        <h2>${tableName}</h2>
                        <button class="back-btn" onclick="document.getElementById('data-view').innerHTML=''">← Back</button>
                    </div>
                    <div class="empty-state">
                        <div class="empty-state-icon">(empty)</div>
                        <p>No data found in this table</p>
                    </div>
                `;
                return;
            }
            
            let html = `
                <div class="data-header">
                    <h2>${tableName} <span style="color: #666; font-size: 0.8em;">(${data.rows.length} rows)</span></h2>
                    <button class="back-btn" onclick="document.getElementById('data-view').innerHTML=''">← Back to Tables</button>
                </div>
            `;
            html += '<div style="overflow-x: auto;"><table><thead><tr>';
            data.columns.forEach(col => {
                html += `<th>${escapeHtml(col)}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            data.rows.forEach(row => {
                html += '<tr>';
                data.columns.forEach(col => {
                    const value = row[col];
                    let display = '';
                    if (value === null || value === '') {
                        display = '<em style="color: #999;">null</em>';
                    } else if (typeof value === 'string' && value.length > 100) {
                        display = escapeHtml(value.substring(0, 100)) + '...';
                    } else {
                        display = escapeHtml(String(value));
                    }
                    html += `<td>${display}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            document.getElementById('data-view').innerHTML = html;
            
            // Scroll to data view
            document.getElementById('data-view').scrollIntoView({ behavior: 'smooth' });
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        loadTables();
    </script>
</body>
</html>
        """

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), DatabaseViewer)
    print(f"🌐 Database Viewer started!")
    print(f"📊 Open your browser and go to: http://localhost:{port}")
    print(f"⏹️  Press Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

