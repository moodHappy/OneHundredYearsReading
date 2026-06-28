import os
import json
import re

BASE_DIR = "docs"

def generate_index():
    os.makedirs(BASE_DIR, exist_ok=True)
    
    print("⚙️ 正在重新编译《百年孤独》专属解构枢纽...")
    archive_data = {}
    
    if os.path.exists(BASE_DIR):
        years = [d for d in os.listdir(BASE_DIR) if d.isdigit()]
        for year in years:
            y_int = int(year) 
            if y_int not in archive_data:
                archive_data[y_int] = {}
                
            months = [d for d in os.listdir(os.path.join(BASE_DIR, year)) if d.isdigit()]
            for month in months:
                m_int = int(month) 
                if m_int not in archive_data[y_int]:
                    archive_data[y_int][m_int] = {}
                    
                files = sorted([f for f in os.listdir(os.path.join(BASE_DIR, year, month)) if f.endswith('.html')], reverse=True)
                for file in files:
                    try:
                        parts = file.replace(".html", "").split('_')
                        if len(parts) >= 4:
                            d_int = int(parts[2]) 
                            # 严格截取时和分
                            time_str = f"{parts[3][:2]}:{parts[3][2:4]}"
                            file_path = f"{year}/{month}/{file}"
                            
                            snippet = ""
                            with open(os.path.join(BASE_DIR, year, month, file), 'r', encoding='utf-8') as f_html:
                                # 读取足够多的内容以寻找正文，最高读取10000字符防止内存占用
                                content = f_html.read(10000) 
                                
                                # 定位正文部分
                                body_start = content.find('<body')
                                search_area = content[body_start:] if body_start != -1 else content
                                
                                # 将常见的块级元素替换为换行符，以便分行提取
                                text_block = re.sub(r'</?(div|p|br|h[1-6]|li|article|section)[^>]*>', '\n', search_area, flags=re.IGNORECASE)
                                # 去除其余所有 HTML 标签
                                pure_text = re.sub(r'<[^>]+>', '', text_block)
                                
                                # 按行分割并去除空白
                                lines = [line.strip() for line in pure_text.split('\n') if line.strip()]
                                
                                # 1. 尝试寻找“原始摘录”或“Original Text”
                                for i, line in enumerate(lines):
                                    if "原始摘录" in line or "Original Text" in line:
                                        if i + 1 < len(lines):
                                            snippet = lines[i+1] # 抓取特征词后的下一行正文
                                        else:
                                            snippet = line
                                        break
                                
                                # 2. 如果没找到特定标题，随便抓取第一段具有一定长度的文字
                                if not snippet:
                                    for line in lines:
                                        # 过滤掉可能的 CSS/JS 残留或极短的标题
                                        if len(line) > 15 and not re.match(r'^[\.\#\{\}\;]', line):
                                            snippet = line
                                            break
                                            
                                # 3. 终极回退：抓取网页 title 标签
                                if not snippet:
                                    start = content.find('<title>')
                                    end = content.find('</title>')
                                    if start != -1 and end != -1:
                                        snippet = content[start+7:end].strip()
                                    else:
                                        snippet = "📌 语法解构"
                            
                            # 截取最多100个字符避免 JSON 过大，多出的部分 CSS 会自动加省略号
                            if len(snippet) > 100:
                                snippet = snippet[:100]
                                
                            if d_int not in archive_data[y_int][m_int]:
                                archive_data[y_int][m_int][d_int] = []
                            archive_data[y_int][m_int][d_int].append({"time": time_str, "path": file_path, "title": snippet})
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
        body, html { font-family: -apple-system, "Segoe UI", sans-serif; background: var(--bg); margin: 0; padding: 0; color: var(--text); height: 100%; overflow-y: auto; -webkit-font-smoothing: antialiased; }
        
        .container { max-width: 600px; margin: 0 auto; padding: 20px; box-sizing: border-box; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px dashed var(--border); margin-bottom: 20px; position: relative; }
        .header h1 { margin: 0 0 5px 0; font-size: 2.2rem; color: var(--primary); font-weight: 800; font-family: Georgia, serif; }
        .header p { margin: 0; font-size: 0.9rem; color: #7f8c8d; letter-spacing: 1px; }
        .settings-btn { position: absolute; right: 0; top: 20px; background: none; border: none; font-size: 1.4rem; cursor: pointer; opacity: 0.8; }
        
        /* 更新控件布局 */
        .controls { display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 20px; }
        .select-box { padding: 0 12px; border: 1px solid var(--border); border-radius: 6px; outline: none; font-weight: bold; background: var(--card); color: var(--primary); height: 36px; box-sizing: border-box; font-size: 0.95rem; }
        
        /* 按钮样式 */
        .btn-nav, .btn-today {
            background-color: var(--btn-blue);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 0.95rem;
            cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 36px;
            box-sizing: border-box;
            font-weight: 600;
        }
        .btn-nav { width: 36px; padding: 0; }
        .btn-today { padding: 0 12px; }
        .btn-nav:active, .btn-today:active { transform: scale(0.95); }
        .btn-nav:hover, .btn-today:hover { opacity: 0.9; }

        .calendar-wrapper { background: var(--card); padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; }
        .weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 13px; color: #888; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
        .days-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
        .day-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-weight: bold; border-radius: 10px; position: relative; cursor: pointer; transition: all 0.2s; }
        .day-cell.empty { visibility: hidden; }
        .day-cell.has-news { color: var(--text); background: #fdfdfd; border: 1px solid #f5f5f5; }
        .day-cell.no-news { color: #dcdde1; }
        .day-cell.selected { background: #eaf2f8; color: var(--primary); border: 1px solid #3498db; }
        .day-cell.today { background: #fff9e6; border: 1px solid #f1c40f; }
        .dot { width: 5px; height: 5px; background: var(--primary); border-radius: 50%; position: absolute; bottom: 5px; display: none; }
        .day-cell.has-news .dot { display: block; }
        
        .feed-list { display: flex; flex-direction: column; gap: 12px; }
        .feed-item { background: var(--card); padding: 16px 18px; border-radius: 12px; text-decoration: none; color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.03); display: flex; flex-direction: row; align-items: center; gap: 15px; transition: transform 0.2s; border: 1px solid transparent; }
        .feed-item:active { transform: scale(0.98); background: #fafafa; }
        .feed-time { font-family: -apple-system, sans-serif; font-weight: 800; color: #111; font-size: 0.95rem; flex-shrink: 0; min-width: 45px; text-align: center; }
        .feed-title { color: #7f8c8d; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-grow: 1; }
        
        .modal { display: none; position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; padding: 20px; backdrop-filter: blur(4px); }
        .modal-content { background: #fff; padding: 25px; border-radius: 16px; width: 100%; max-width: 350px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .modal-content input { width: 100%; padding: 12px; margin-bottom: 15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 8px; font-size: 1rem; }
        .modal-content button { width: 100%; padding: 12px; background: var(--primary); color: #fff; border: none; border-radius: 8px; font-size: 1rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Macondo Matrix</h1>
            <p>《百年孤独》精读解构实验室</p>
            <button class="settings-btn" onclick="document.getElementById('modal').style.display='flex'">⚙️</button>
        </div>
        <div class="controls">
            <button class="btn-nav" id="prevMonthBtn">&lt;</button>
            <select class="select-box" id="yearSelect"></select>
            <select class="select-box" id="monthSelect">
                <option value="1">01月</option><option value="2">02月</option><option value="3">03月</option>
                <option value="4">04月</option><option value="5">05月</option><option value="6">06月</option>
                <option value="7">07月</option><option value="8">08月</option><option value="9">09月</option>
                <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
            </select>
            <button class="btn-nav" id="nextMonthBtn">&gt;</button>
            <button class="btn-today" id="todayBtn">回到今天</button>
        </div>
        <div class="calendar-wrapper">
            <div class="weekdays"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>
            <div class="days-grid" id="daysGrid"></div>
        </div>
        <div class="feed-list" id="feedList"></div>
    </div>

    <div class="modal" id="modal">
        <div class="modal-content">
            <h3 style="margin-top:0; color:#2c3e50;">配置核心 Token</h3>
            <p style="font-size:0.8rem; color:#888; margin-top:-10px;">用于同步子页面的后续无痕编辑修改</p>
            <input type="password" id="gh-token" placeholder="输入你的 GitHub Token">
            <button onclick="saveSettings()">💾 永久保存至本地</button>
        </div>
    </div>

    <script>
        window.onload = function() {
            if (!localStorage.getItem('GH_TOKEN')) {
                document.getElementById('modal').style.display = 'flex';
            }
        };

        const archiveData = REPLACEME_JSON_DATA;
        const today = new Date();
        let sY = today.getFullYear(), sM = today.getMonth() + 1, sD = today.getDate();
        
        const yearSelect = document.getElementById('yearSelect');
        const monthSelect = document.getElementById('monthSelect');
        const daysGrid = document.getElementById('daysGrid');
        
        function initSelects() {
            const years = Object.keys(archiveData).map(Number).sort((a,b)=>b-a);
            if(!years.includes(sY)) years.unshift(sY);
            yearSelect.innerHTML = ''; // 清空重新生成
            years.forEach(y => {
                const opt = document.createElement('option'); opt.value = y; opt.textContent = y + '年';
                yearSelect.appendChild(opt);
            });
            yearSelect.value = sY; monthSelect.value = sM;
        }

        // 同步 UI 状态
        function syncUI() {
            let yearFound = false;
            for(let i=0; i<yearSelect.options.length; i++) {
                if(parseInt(yearSelect.options[i].value) === sY) { yearFound = true; break; }
            }
            if(!yearFound) {
                const opt = document.createElement('option'); opt.value = sY; opt.textContent = sY + '年';
                yearSelect.appendChild(opt);
            }
            yearSelect.value = sY;
            monthSelect.value = sM;
        }

        // 限制日期合法性
        function clampDate() {
            const daysInMonth = new Date(sY, sM, 0).getDate();
            if (sD > daysInMonth) sD = daysInMonth;
        }
        
        function renderCalendar() {
            daysGrid.innerHTML = '';
            let firstDay = new Date(sY, sM - 1, 1).getDay();
            if (firstDay === 0) firstDay = 7;
            const daysInMonth = new Date(sY, sM, 0).getDate();
            
            for(let i=1; i<firstDay; i++) {
                daysGrid.innerHTML += '<div class="day-cell empty"></div>';
            }
            
            const monthData = (archiveData[sY] && archiveData[sY][sM]) || {};
            for(let d=1; d<=daysInMonth; d++) {
                const hasNews = monthData[d] && monthData[d].length > 0;
                const isToday = sY === today.getFullYear() && sM === today.getMonth()+1 && d === today.getDate();
                const isSelected = d === sD;
                
                let classes = 'day-cell';
                if(hasNews) classes += ' has-news'; else classes += ' no-news';
                if(isToday) classes += ' today';
                if(isSelected) classes += ' selected';
                
                const cell = document.createElement('div');
                cell.className = classes;
                cell.innerHTML = d + `<div class="dot" style="display:${hasNews?'block':'none'}"></div>`;
                cell.onclick = () => { sD = d; renderCalendar(); renderList(); };
                daysGrid.appendChild(cell);
            }
        }
        
        function renderList() {
            const list = document.getElementById('feedList');
            const data = (archiveData[sY] && archiveData[sY][sM] && archiveData[sY][sM][sD]) || [];
            
            if(data.length) {
                const itemsHtml = data.map(item => `<a href="${item.path}" class="feed-item"><span class="feed-time">${item.time}</span><span class="feed-title">${item.title}</span></a>`).join('');
                list.innerHTML = itemsHtml;
            } else {
                list.innerHTML = '<div style="text-align:center; padding: 25px 20px; color:#bdc3c7; font-size: 0.9rem;">当日无解构档案</div>';
            }
        }
        
        yearSelect.onchange = e => { sY = parseInt(e.target.value); clampDate(); renderCalendar(); renderList(); };
        monthSelect.onchange = e => { sM = parseInt(e.target.value); clampDate(); renderCalendar(); renderList(); };

        // 按钮事件绑定
        document.getElementById('prevMonthBtn').onclick = () => {
            sM--;
            if(sM < 1) { sM = 12; sY--; }
            clampDate(); syncUI(); renderCalendar(); renderList();
        };

        document.getElementById('nextMonthBtn').onclick = () => {
            sM++;
            if(sM > 12) { sM = 1; sY++; }
            clampDate(); syncUI(); renderCalendar(); renderList();
        };

        document.getElementById('todayBtn').onclick = () => {
            sY = today.getFullYear();
            sM = today.getMonth() + 1;
            sD = today.getDate();
            syncUI(); renderCalendar(); renderList();
        };
        
        function saveSettings() {
            localStorage.setItem('GH_TOKEN', document.getElementById('gh-token').value.trim());
            document.getElementById('modal').style.display = 'none';
        }
        document.getElementById('gh-token').value = localStorage.getItem('GH_TOKEN') || '';

        initSelects(); 
        renderCalendar(); 
        renderList();
    </script>
</body>
</html>"""

    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content.replace("REPLACEME_JSON_DATA", json_data))
    print("🚀 《百年孤独》枢纽索引构建完毕！")

if __name__ == "__main__":
    generate_index()
