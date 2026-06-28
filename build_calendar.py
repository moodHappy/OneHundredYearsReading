import os
import json

BASE_DIR = "docs"

def generate_index():
    os.makedirs(BASE_DIR, exist_ok=True)
    
    print("⚙️ 正在重新编译《百年孤独》专属解构枢纽...")
    archive_data = {}
    
    if os.path.exists(BASE_DIR):
        years = [d for d in os.listdir(BASE_DIR) if d.isdigit()]
        for year in years:
            y_int = int(year) 
            if y_int not in archive_data: archive_data[y_int] = {}
                
            months = [d for d in os.listdir(os.path.join(BASE_DIR, year)) if d.isdigit()]
            for month in months:
                m_int = int(month) 
                if m_int not in archive_data[y_int]: archive_data[y_int][m_int] = {}
                    
                files = sorted([f for f in os.listdir(os.path.join(BASE_DIR, year, month)) if f.endswith('.html')], reverse=True)
                for file in files:
                    try:
                        parts = file.replace(".html", "").split('_')
                        if len(parts) >= 4:
                            d_int = int(parts[2]) 
                            time_str = f"{parts[3][:2]}:{parts[3][2:4]}"
                            file_path = f"{year}/{month}/{file}"
                            
                            title = "📌 语法解构"
                            snippet = ""
                            
                            with open(os.path.join(BASE_DIR, year, month, file), 'r', encoding='utf-8') as f_html:
                                content = f_html.read()
                                # 提取 <title>
                                start_t = content.find('<title>')
                                end_t = content.find('</title>')
                                if start_t != -1 and end_t != -1:
                                    title = content[start_t+7:end_t]
                                
                                # 提取 id="view-original" 的正文内容
                                start_s = content.find('id="view-original"')
                                if start_s != -1:
                                    # 寻找 div 的开始标记 >
                                    start_div = content.find('>', start_s) + 1
                                    end_div = content.find('</div>', start_div)
                                    if end_div != -1:
                                        snippet = content[start_div:end_div].strip()[:60] + "..." # 截取前60字符

                            if d_int not in archive_data[y_int][m_int]:
                                archive_data[y_int][m_int][d_int] = []
                            archive_data[y_int][m_int][d_int].append({
                                "time": time_str, 
                                "path": file_path, 
                                "title": title,
                                "snippet": snippet # 存入提取的正文片段
                            })
                    except Exception as e:
                        print(f"解析文件出错 {file}: {e}")

    json_data = json.dumps(archive_data)

    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Macondo Matrix</title>
    <style>
        :root { --bg: #f5f5f7; --primary: #2980b9; --accent: #f39c12; --card: #ffffff; --border: #e0e0e0; --text: #333; --btn-blue: #6482f0; }
        body, html { font-family: -apple-system, sans-serif; background: var(--bg); margin: 0; padding: 0; color: var(--text); height: 100%; overflow-y: auto; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; box-sizing: border-box; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px dashed var(--border); margin-bottom: 20px; position: relative; }
        .header h1 { margin: 0 0 5px 0; font-size: 2.2rem; color: var(--primary); font-weight: 800; font-family: Georgia, serif; }
        .settings-btn { position: absolute; right: 0; top: 20px; background: none; border: none; font-size: 1.4rem; cursor: pointer; }
        
        .controls { display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 20px; }
        .select-box { padding: 0 12px; border: 1px solid var(--border); border-radius: 6px; height: 36px; font-weight: bold; color: var(--primary); }
        .btn-nav, .btn-today { background-color: var(--btn-blue); color: white; border: none; border-radius: 6px; height: 36px; cursor: pointer; font-weight: 600; }
        
        .calendar-wrapper { background: var(--card); padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; }
        .days-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
        .day-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-weight: bold; border-radius: 10px; position: relative; cursor: pointer; }
        .day-cell.selected { background: #eaf2f8; color: var(--primary); border: 1px solid #3498db; }
        .day-cell.today { background: #fff9e6; border: 1px solid #f1c40f; }
        .dot { width: 5px; height: 5px; background: var(--primary); border-radius: 50%; position: absolute; bottom: 5px; display: none; }
        .day-cell.has-news .dot { display: block; }
        
        .feed-list { display: flex; flex-direction: column; gap: 12px; }
        .feed-item { background: var(--card); padding: 16px 18px; border-radius: 12px; text-decoration: none; color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.03); display: flex; flex-direction: column; gap: 6px; }
        .feed-meta { display: flex; align-items: center; gap: 10px; }
        .feed-time { font-weight: 800; color: #111; }
        .feed-snippet { font-size: 0.85rem; color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Macondo Matrix</h1>
            <button class="settings-btn" onclick="document.getElementById('modal').style.display='flex'">⚙️</button>
        </div>
        <div class="controls">
            <button class="btn-nav" id="prevMonthBtn">&lt;</button>
            <select class="select-box" id="yearSelect"></select>
            <select class="select-box" id="monthSelect"></select>
            <button class="btn-nav" id="nextMonthBtn">&gt;</button>
            <button class="btn-today" id="todayBtn">回到今天</button>
        </div>
        <div class="calendar-wrapper"><div class="days-grid" id="daysGrid"></div></div>
        <div class="feed-list" id="feedList"></div>
    </div>
    <script>
        const archiveData = REPLACEME_JSON_DATA;
        // ... (省略部分逻辑代码，与上一版本一致) ...
        function renderList() {
            const list = document.getElementById('feedList');
            const data = (archiveData[sY] && archiveData[sY][sM] && archiveData[sY][sM][sD]) || [];
            list.innerHTML = data.map(item => `
                <a href="${item.path}" class="feed-item">
                    <div class="feed-meta">
                        <span class="feed-time">${item.time}</span>
                        <span style="color:var(--primary)">${item.title}</span>
                    </div>
                    <div class="feed-snippet">${item.snippet}</div>
                </a>`).join('') || '<div style="text-align:center; padding:20px; color:#ccc;">当日无解构档案</div>';
        }
        // ... (后续逻辑一致)
    </script>
</body>
</html>"""
    # 写入文件逻辑...
