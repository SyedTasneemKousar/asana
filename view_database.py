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
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        .table-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin: 20px 0; }
        .table-card { padding: 15px; background: #e8f4f8; border-radius: 5px; cursor: pointer; border: 2px solid transparent; }
        .table-card:hover { border-color: #0066cc; }
        .table-card h3 { margin: 0 0 5px 0; color: #0066cc; }
        .table-card .count { color: #666; font-size: 14px; }
        #data-view { margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #0066cc; color: white; padding: 10px; text-align: left; }
        td { padding: 8px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f0f0f0; }
        .loading { text-align: center; padding: 20px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Asana Simulation Database Viewer</h1>
        <p>Click on a table to view its data</p>
        <div id="tables" class="table-list">
            <div class="loading">Loading tables...</div>
        </div>
        <div id="data-view"></div>
    </div>
    <script>
        async function loadTables() {
            const response = await fetch('/api/tables');
            const tables = await response.json();
            const container = document.getElementById('tables');
            container.innerHTML = tables.map(t => `
                <div class="table-card" onclick="loadTable('${t.name}')">
                    <h3>${t.name}</h3>
                    <div class="count">${t.count.toLocaleString()} rows</div>
                </div>
            `).join('');
        }
        
        async function loadTable(tableName) {
            document.getElementById('data-view').innerHTML = '<div class="loading">Loading data...</div>';
            const response = await fetch(`/api/table?name=${tableName}&limit=100`);
            const data = await response.json();
            
            if (data.rows.length === 0) {
                document.getElementById('data-view').innerHTML = '<p>No data found</p>';
                return;
            }
            
            let html = `<h2>${tableName} (showing ${data.rows.length} rows)</h2>`;
            html += '<table><thead><tr>';
            data.columns.forEach(col => {
                html += `<th>${col}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            data.rows.forEach(row => {
                html += '<tr>';
                data.columns.forEach(col => {
                    const value = row[col];
                    const display = value === null ? '<em>null</em>' : 
                                   typeof value === 'string' && value.length > 50 ? 
                                   value.substring(0, 50) + '...' : value;
                    html += `<td>${display}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            document.getElementById('data-view').innerHTML = html;
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

