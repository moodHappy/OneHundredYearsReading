import os
import json

BASE_DIR = "docs"

# 统一维护的独立笔记页面模板
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{TITLE}}</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { --bg: #fcfcfc; --surface: #ffffff; --text: #2c3e50; --border: #ecf0f1; --accent: #f39c12; --highlight: #fef9e7; }
        body { font-family: -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: 0 auto; padding-bottom: 50px;}
        .nav-back { margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;}
        .nav-back a { text-decoration: none; color: white; background: var(--text); padding: 8px 18px; border-radius: 20px; font-size: 0.9rem; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .sync-status { font-size: 0.85rem; color: #27ae60; font-weight: bold; display: none; }
        .source-link { font-size: 0.85rem; color: var(--accent); text-decoration: none; display: inline-block; margin-top: 12px; background: #fffcf0; padding: 6px 14px; border-radius: 20px; font-weight: bold; border: 1px solid #fce8b2;}
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
        .card-header { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #95a5a6; border-bottom: 1px dashed var(--border); padding-bottom: 8px; margin-bottom: 12px; font-weight: bold;}
        .markdown-body { font-size: 1.05rem; line-height: 1.6; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 { color: var(--accent); margin-top: 16px; margin-bottom: 8px; font-weight: 700; border-bottom: 1px dashed #eee; padding-bottom: 4px; }
        .markdown-body h3 { font-size: 1.15rem; }
        .markdown-body p { margin-top: 0; margin-bottom: 8px; }
        .markdown-body ul, .markdown-body ol { margin-top: 0; margin-bottom: 8px; padding-left: 20px; }
        .markdown-body li { margin-bottom: 4px; }
        .markdown-body li p { margin: 0; } 
        .markdown-body p:empty { display: none; } 
        .markdown-body br + br { display: none; } 
        .markdown-body blockquote { margin: 0 0 10px 0; padding: 10px 15px; background: var(--highlight); border-left: 5px solid #f1c40f; color: #5c4d22; font-family: Georgia, serif; font-size: 1.1rem; border-radius: 0 8px 8px 0; }
        .markdown-body blockquote p { margin-bottom: 0; }
        .edit-control-block { display: none; background: #fff; border-radius: 10px; margin-top: 10px; }
        .edit-textarea { width: 100%; min-height: 250px; padding: 15px; font-family: monospace; font-size: 1.05rem; border: 2px solid var(--accent); border-radius: 10px; box-sizing: border-box; resize: vertical; background: #fff; color: #2c3e50; line-height: 1.5; outline: none; box-shadow: 0 4px 15px rgba(243,156,18,0.1);}
        .control-btn-row { display: flex; gap: 10px; margin-top: 10px; }
        .action-btn { border: none; padding: 10px 22px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 0.95rem; }
        .btn-save { background: var(--accent); color: white; flex: 1; }
        .btn-cancel { background: #ecf0f1; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-back">
            <a href="../../index.html">🔙 返回矩阵枢纽</a>
            <span class="sync-status" id="sync-status">📡 同步中...</span>
        </div>
        
        <div class="card">
            <div class="card-header">🌐 来源档案 (Source)</div>
            <div style="font-weight:bold; color:#2c3e50; line-height: 1.4;">{{SOURCE_TITLE}}</div>
            <a href="{{SOURCE_URL}}" target="_blank" class="source-link">🔗 原文链接</a>
        </div>

        <div class="card">
            <div class="card-header">📖 原始摘录 (Original Text)</div>
            <div id="view-original" class="markdown-body" style="white-space: pre-wrap; font-family: Georgia, serif; font-size: 1.15rem; line-height: 1.8; color: #34495e;">{{ORIGINAL_TEXT}}</div>
        </div>

        <div class="card" id="block-analysis">
            <div class="card-header">🔬 深度解构 (Analysis)</div>
            <div id="view-analysis" class="markdown-body"></div>
            
            <div id="edit-control-block" class="edit-control-block">
                <textarea id="edit-analysis" class="edit-textarea"></textarea>
                <div class="control-btn-row">
                    <button class="action-btn btn-save" onclick="saveEdit()">💾 写入云端数据 (触发重构)</button>
                    <button class="action-btn btn-cancel" onclick="cancelEdit()">取消</button>
                </div>
            </div>
        </div>
    </div>

    <textarea id="raw-original" style="display:none;">{{ORIGINAL_TEXT}}</textarea>
    <textarea id="raw-analysis" style="display:none;">{{ANALYSIS_TEXT}}</textarea>

    <script>
        const GH_OWNER = "moodHappy"; 
        const GH_REPO = "OneHundredYearsReading";
        const jsonRelPath = "{{JSON_REL_PATH}}";

        function renderAll() {
            const analContent = document.getElementById('raw-analysis').value;
            try { 
                if (typeof marked !== 'undefined') {
                    document.getElementById('view-analysis').innerHTML = marked.parse ? marked.parse(analContent) : marked(analContent); 
                } else {
                    document.getElementById('view-analysis').innerHTML = "<pre style='white-space:pre-wrap'>" + analContent + "</pre>";
                }
            } catch(e) {
                document.getElementById('view-analysis').innerHTML = "<pre style='white-space:pre-wrap'>" + analContent + "</pre>";
            }
        }
        window.onload = renderAll;

        const viewBlock = document.getElementById('view-analysis');
        const editCtrlBlock = document.getElementById('edit-control-block');
        const textarea = document.getElementById('edit-analysis');
        const statusMsg = document.getElementById('sync-status');

        viewBlock.addEventListener('dblclick', triggerEdit);
        viewBlock.addEventListener('touchstart', e => { if (e.touches.length === 2) triggerEdit(); });

        function triggerEdit() {
            viewBlock.style.display = 'none'; 
            editCtrlBlock.style.display = 'block';
            textarea.value = document.getElementById('raw-analysis').value; 
            textarea.focus();
        }

        function cancelEdit() {
            editCtrlBlock.style.display = 'none'; 
            viewBlock.style.display = 'block';
        }

        // 直接向后台 Python 推送更新的 JSON！
        async function saveEdit() {
            const btn = document.querySelector('.btn-save');
            const oldText = btn.innerText;
            btn.innerText = '📡 正在更新数据...';
            btn.disabled = true;
            
            const newText = textarea.value.trim();
            const token = localStorage.getItem('GH_TOKEN'); 
            if(!token) {
                btn.innerText = oldText; btn.disabled = false;
                return;
            }
            
            // 封装发给 Python 的数据
            const payload = {
                original: document.getElementById('raw-original').value,
                analysis: newText,
                sourceTitle: "{{SOURCE_TITLE}}",
                sourceUrl: "{{SOURCE_URL}}"
            };
            
            statusMsg.style.display = 'block'; 
            statusMsg.style.color = '#f39c12'; 
            statusMsg.innerText = '📡 静默同步中...';
            
            try {
                const getRes = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${jsonRelPath}`, { headers: { 'Authorization': `token ${token}` } });
                if(!getRes.ok) throw new Error('找不到云端数据源文件');
                const fileData = await getRes.json();
                
                const utf8Encode = new TextEncoder().encode(JSON.stringify(payload, null, 2));
                const base64Content = btoa(String.fromCodePoint(...utf8Encode));
                
                const putRes = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${jsonRelPath}`, {
                    method: 'PUT', 
                    headers: { 'Authorization': `token ${token}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: `Update analysis data via UI`, content: base64Content, sha: fileData.sha })
                });
                
                if(putRes.ok) { 
                    document.getElementById('raw-analysis').value = newText;
                    cancelEdit(); 
                    renderAll();
                    statusMsg.style.color = '#27ae60'; statusMsg.innerText = '✅ 云端数据已更新 (将在30秒后重构网页)'; 
                    setTimeout(() => statusMsg.style.display = 'none', 5000); 
                } else { 
                    statusMsg.style.display = 'none'; 
                }
            } catch(e) {
                statusMsg.style.display = 'none';
            }
            btn.innerText = oldText; btn.disabled = false;
        }
    </script>
</body>
</html>"""

def generate_index():
    os.makedirs(BASE_DIR, exist_ok=True)
    
    print("⚙️ 正在通过 Python 引擎重构《百年孤独》枢纽...")
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
                
                files = os.listdir(os.path.join(BASE_DIR, year, month))
                
                # 仅扫描油猴抓取的原生 JSON 纯净数据文件
                json_files = sorted([f for f in files if f.endswith('.json')], reverse=True)
                for json_file in json_files:
                    file_base = json_file.replace('.json', '')
                    path_json = os.path.join(BASE_DIR, year, month, json_file)
                    path_html = os.path.join(BASE_DIR, year, month, f"{file_base}.html")
                    
                    parts = file_base.split('_')
                    if len(parts) >= 4:
                        d_int = int(parts[2]) 
                        time_str = f"{parts[3][:2]}:{parts[3][2:4]}"
                        
                        try:
                            # 提取原生数据
                            with open(path_json, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            orig = data.get('original', '')
                            anal = data.get('analysis', '')
                            src_title = data.get('sourceTitle', 'Chapter 1')
                            src_url = data.get('sourceUrl', '#')

                            # 精准提取前25字符做日历标题，彻底告别默认文字！
                            title = orig[:25].replace('\n', ' ').strip()
                            if len(orig) > 25: title += '...'
                            if not title: title = "📌 语法解构"

                            # 由 Python 生成极简 HTML 覆盖并更新
                            safe_orig = orig.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            safe_anal = anal.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            
                            html_output = ARTICLE_TEMPLATE.replace('{{TITLE}}', title) \
                                                          .replace('{{SOURCE_TITLE}}', src_title) \
                                                          .replace('{{SOURCE_URL}}', src_url) \
                                                          .replace('{{ORIGINAL_TEXT}}', safe_orig) \
                                                          .replace('{{ANALYSIS_TEXT}}', safe_anal) \
                                                          .replace('{{JSON_REL_PATH}}', f"docs/{year}/{month}/{json_file}")
                            
                            with open(path_html, 'w', encoding='utf-8') as f_html:
                                f_html.write(html_output)

                            if d_int not in archive_data[y_int][m_int]:
                                archive_data[y_int][m_int][d_int] = []
                            archive_data[y_int][m_int][d_int].append({"time": time_str, "path": f"{year}/{month}/{file_base}.html", "title": title})
                        except Exception as e:
                            print(f"解析 JSON 错误 {json_file}: {e}")

    json_data = json.dumps(archive_data)

    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Macondo Matrix</title>
    <style>
        :root { --bg: #f5f5f7; --primary: #2980b9; --accent: #f39c12; --card: #ffffff; --border: #e0e0e0; --text: #333; }
        body, html { font-family: -apple-system, sans-serif; background: var(--bg); margin: 0; padding: 0; color: var(--text); height: 100%; overflow-y: auto; -webkit-font-smoothing: antialiased; }
        
        .container { max-width: 600px; margin: 0 auto; padding: 20px; box-sizing: border-box; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px dashed var(--border); margin-bottom: 20px; position: relative; }
        .header h1 { margin: 0 0 5px 0; font-size: 2.2rem; color: var(--primary); font-weight: 800; font-family: Georgia, serif; }
        .header p { margin: 0; font-size: 0.9rem; color: #7f8c8d; letter-spacing: 1px; }
        .settings-btn { position: absolute; right: 0; top: 20px; background: none; border: none; font-size: 1.4rem; cursor: pointer; opacity: 0.8; }
        
        .controls { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .select-box { padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; outline: none; font-weight: bold; background: var(--card); color: var(--primary); }
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
            <select class="select-box" id="yearSelect"></select>
            <select class="select-box" id="monthSelect">
                <option value="1">01月</option><option value="2">02月</option><option value="3">03月</option>
                <option value="4">04月</option><option value="5">05月</option><option value="6">06月</option>
                <option value="7">07月</option><option value="8">08月</option><option value="9">09月</option>
                <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
            </select>
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
            <p style="font-size:0.8rem; color:#888; margin-top:-10px;">用于同步编辑的纯净数据</p>
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
            years.forEach(y => {
                const opt = document.createElement('option'); opt.value = y; opt.textContent = y + '年';
                yearSelect.appendChild(opt);
            });
            yearSelect.value = sY; monthSelect.value = sM;
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
        
        yearSelect.onchange = e => { sY = parseInt(e.target.value); renderCalendar(); renderList(); };
        monthSelect.onchange = e => { sM = parseInt(e.target.value); renderCalendar(); renderList(); };
        
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
        f.write(index_html.replace("REPLACEME_JSON_DATA", json_data))
    print("🚀 《百年孤独》数据底座与前端面板构建完毕！")

if __name__ == "__main__":
    generate_index()
