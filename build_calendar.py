import os
import json

BASE_DIR = "docs"

def generate_index():
    os.makedirs(BASE_DIR, exist_ok=True)

    print("⚙️ 正在重新编译全栈语法枢纽 (集成了全库文本检索与云端删除功能)...")
    archive_data = {}

    # 扫描年份文件夹
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
                        time_str = f"{parts[3][:2]}:{parts[3][2:]}"
                        file_path = f"{year}/{month}/{file}"

                        title = "📌 语法解构"
                        original_text = "" # 用于存放提取出的原始英文文本

                        # 通读文件，精准解构 Title 与原始文本内容
                        with open(os.path.join(BASE_DIR, year, month, file), 'r', encoding='utf-8') as f_html:
                            content = f_html.read()

                            # 提取标题
                            start = content.find('<title>')
                            end = content.find('</title>')
                            if start != -1 and end != -1:
                                title = content[start+7:end]

                            # 提取指定的 raw-original 内容
                            orig_start_tag = '<textarea id="raw-original" style="display:none;">'
                            start_orig = content.find(orig_start_tag)
                            if start_orig != -1:
                                end_orig = content.find('</textarea>', start_orig)
                                if end_orig != -1:
                                    original_text = content[start_orig + len(orig_start_tag):end_orig]

                        if d_int not in archive_data[y_int][m_int]:
                            archive_data[y_int][m_int][d_int] = []

                        # 将原文沉淀进 JSON 数据库中
                        archive_data[y_int][m_int][d_int].append({
                            "time": time_str, 
                            "path": file_path, 
                            "title": title,
                            "original": original_text.strip()
                        })
                except Exception as e:
                    print(f"解析文件出错 {file}: {e}")

    json_data = json.dumps(archive_data)

    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Macondo Matrix 枢纽</title>
    <style>
        :root { --bg: #f5f5f7; --primary: #2980b9; --accent: #f1c40f; --card: #ffffff; --border: #e0e0e0; --text: #333; }
        body, html { font-family: -apple-system, "Segoe UI", sans-serif; background: var(--bg); margin: 0; padding: 0; color: var(--text); height: 100%; overflow: hidden; }
        
        .viewport { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; height: 100vh; -webkit-overflow-scrolling: touch; }
        .viewport::-webkit-scrollbar { display: none; }
        .page { flex: 0 0 100vw; width: 100vw; height: 100vh; scroll-snap-align: start; overflow-y: auto; padding-bottom: 30px; box-sizing: border-box; }
        
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        
        /* 完美还原截图的顶部顶格搜索栏 */
        .search-bar-wrapper { display: flex; align-items: center; gap: 12px; margin-top: 5px; margin-bottom: 20px; }
        .search-input { flex-grow: 1; padding: 12px 18px; border: 1px solid var(--border); border-radius: 25px; outline: none; font-size: 0.95rem; background: var(--card); box-shadow: inset 0 1px 3px rgba(0,0,0,0.02); transition: border-color 0.2s; }
        .search-input:focus { border-color: var(--primary); }
        .settings-btn-top { background: none; border: none; font-size: 1.4rem; cursor: pointer; opacity: 0.8; padding: 0; display: flex; align-items: center; }
        
        .controls { display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 20px; }
        .select-box { padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; outline: none; font-weight: bold; background: var(--card); color: var(--primary); -webkit-appearance: none; appearance: none; text-align: center; }
        .nav-btn, .today-btn { background: #e74c3c; color: white; border: none; border-radius: 8px; padding: 8px 14px; font-weight: bold; font-size: 0.95rem; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s, background 0.2s;}
        .nav-btn:active, .today-btn:active { transform: scale(0.95); background: #c0392b; }
        .today-btn { padding: 8px 18px; }

        .calendar-wrapper { background: var(--card); padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.01); margin-bottom: 20px; }
        .weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 13px; color: #888; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
        .days-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
        .day-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-weight: bold; border-radius: 10px; position: relative; cursor: pointer; transition: all 0.2s; }
        .day-cell.empty { visibility: hidden; }
        .day-cell.has-news { color: var(--text); background: #fdfdfd; border: 1px solid #f5f5f5; }
        .day-cell.no-news { color: #dcdde1; }
        .day-cell.selected { border: 1px solid #e74c3c; background: #fdedec; color: #e74c3c; }
        .day-cell.today { background: #fff9e6; border: 1px solid #f1c40f; }
        .dot { width: 4px; height: 4px; background: #e74c3c; border-radius: 50%; position: absolute; bottom: 6px; display: none; }
        .day-cell.has-news .dot { display: block; }
        
        /* 极致紧凑一行流行表 */
        .feed-list { display: flex; flex-direction: column; gap: 12px; }
        .feed-item { background: var(--card); padding: 16px 18px; border-radius: 12px; text-decoration: none; color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.02); display: flex; flex-direction: row; align-items: center; gap: 15px; transition: transform 0.2s; border: 1px solid transparent; cursor: pointer; }
        .feed-item:active { transform: scale(0.98); background: #fafafa; }
        .feed-time { font-family: -apple-system, sans-serif; font-weight: 800; color: #111; font-size: 0.95rem; flex-shrink: 0; min-width: 45px; text-align: center; }
        .feed-title { color: #7f8c8d; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-grow: 1; }
        
        /* 新增删除按钮样式 */
        .delete-btn { background: #e74c3c; color: white; border: none; border-radius: 6px; padding: 6px 14px; font-size: 0.85rem; font-weight: bold; cursor: pointer; margin-left: auto; box-shadow: 0 2px 5px rgba(231,76,60,0.3); transition: transform 0.2s; }
        .delete-btn:active { transform: scale(0.9); }

        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; font-weight: bold; margin-bottom: 8px; color: var(--primary); font-size: 0.95rem; }
        .form-control { width: 100%; box-sizing: border-box; padding: 15px; border: 1px solid var(--border); border-radius: 10px; font-size: 1rem; font-family: inherit; resize: vertical; background: var(--card); }
        .form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(41,128,185,0.1); }
        textarea.form-control { min-height: 120px; line-height: 1.5; }
        .btn-push { width: 100%; background: var(--primary); color: white; border: none; padding: 16px; border-radius: 10px; font-size: 1.15rem; font-weight: bold; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 15px rgba(41,128,185,0.3); transition: background 0.2s; }
        .btn-push:active { transform: scale(0.98); background: #2471a3; }
        .btn-push:disabled { background: #95a5a6; cursor: not-allowed; box-shadow: none; }
        
        .modal { display: none; position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; padding: 20px; backdrop-filter: blur(4px); }
        .modal-content { background: #fff; padding: 25px; border-radius: 16px; width: 100%; max-width: 350px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .modal-content input { width: 100%; padding: 12px; margin-bottom: 15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 8px; font-size: 1rem; }
        .modal-content button { width: 100%; padding: 12px; background: var(--primary); color: #fff; border: none; border-radius: 8px; font-size: 1rem; font-weight: bold; }
        
        .page-indicator { text-align: center; color: #95a5a6; font-size: 0.85rem; padding: 15px; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="viewport" id="viewport">
        <div class="page" id="page-1">
            <div class="container">
                <div class="search-bar-wrapper">
                    <input type="text" id="searchInput" class="search-input" placeholder="搜索全库 HTML 英文原文或标题...">
                    <button class="settings-btn-top" onclick="document.getElementById('modal').style.display='flex'">⚙️</button>
                </div>
                
                <div class="controls" id="calendarControls">
                    <button class="nav-btn" id="prevMonthBtn">&lt;</button>
                    <select class="select-box" id="yearSelect"></select>
                    <select class="select-box" id="monthSelect">
                        <option value="1">01月</option><option value="2">02月</option><option value="3">03月</option>
                        <option value="4">04月</option><option value="5">05月</option><option value="6">06月</option>
                        <option value="7">07月</option><option value="8">08月</option><option value="9">09月</option>
                        <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
                    </select>
                    <button class="nav-btn" id="nextMonthBtn">&gt;</button>
                    <button class="today-btn" id="todayBtn">今天</button>
                </div>
                
                <div class="calendar-wrapper" id="calendarWrapper">
                    <div class="weekdays"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>
                    <div class="days-grid" id="daysGrid"></div>
                </div>
                
                <div class="feed-list" id="feedList"></div>
                <div class="page-indicator" id="slideIndicator">← 向左滑动进入录入矩阵</div>
            </div>
        </div>
        
        <div class="page" id="page-2">
            <div class="container">
                <div class="header" style="text-align: center; padding: 10px 0 20px 0;">
                    <h1 style="margin: 0; font-size: 1.8rem; color: var(--primary);">Deconstruct</h1>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #7f8c8d;">目标仓库: OneHundredYearsReading</p>
                </div>
                <div class="form-group">
                    <label>原文 (Original Text)</label>
                    <textarea id="in-original" class="form-control" placeholder="输入英语原句..."></textarea>
                </div>
                <div class="form-group">
                    <label>教师级剖析 (Markdown Analysis)</label>
                    <textarea id="in-analysis" class="form-control" style="min-height: 280px;" placeholder="支持 Markdown 语法..."></textarea>
                </div>
                <button class="btn-push" id="pushBtn" onclick="pushToGitHub()">🚀 推送至云端矩阵</button>
                <div class="page-indicator" style="margin-top: 20px;">向右滑动返回日历枢纽 →</div>
            </div>
        </div>
    </div>

    <div class="modal" id="modal">
        <div class="modal-content">
            <h3 style="margin-top:0; color:#2c3e50;">配置核心 Token</h3>
            <p style="font-size:0.8rem; color:#888; margin-top:-10px;">仅需 Token，目标仓库已自动焊死！</p>
            <input type="password" id="gh-token" placeholder="输入你的 GitHub Token">
            <button onclick="saveSettings()">💾 永久保存至本地</button>
        </div>
    </div>

    <script>
        const GH_OWNER = "moodHappy";
        const GH_REPO = "OneHundredYearsReading";

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
        const searchInput = document.getElementById('searchInput');
        
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
                // 使用 div 代替 a 标签，方便捕捉双击和防止误触跳转
                const itemsHtml = data.map(item => `
                    <div class="feed-item" onclick="handleItemClick(event, '${item.path}')">
                        <span class="feed-time">${item.time}</span>
                        <span class="feed-title">${item.title}</span>
                        <button class="delete-btn" style="display:none;" onclick="event.stopPropagation(); confirmDelete('${item.path}', this)">删除</button>
                    </div>
                `).join('');
                list.innerHTML = itemsHtml;
            } else {
                list.innerHTML = '<div style="text-align:center; padding: 25px 20px; color:#bdc3c7; font-size: 0.9rem;">当日无其他解构档案</div>';
            }
        }

        // 捕捉列表项目的单双击状态
        let clickTimer = null;
        function handleItemClick(e, path) {
            // 如果点到的是删除按钮本身，忽略不处理
            if(e.target.closest('.delete-btn')) return;
            
            const currentItem = e.currentTarget;
            
            if (clickTimer === null) {
                // 启动定时器等待可能的第二次点击（300ms为常规防抖区间）
                clickTimer = setTimeout(() => {
                    clickTimer = null;
                    // 单击：直接跳转页面
                    window.location.href = path;
                }, 300);
            } else {
                // 已经有点击触发且在300ms内，判定为双击
                clearTimeout(clickTimer);
                clickTimer = null;
                
                const delBtn = currentItem.querySelector('.delete-btn');
                if(delBtn) {
                    // 先隐藏其它的所有删除按钮，保持页面整洁
                    document.querySelectorAll('.delete-btn').forEach(btn => btn.style.display = 'none');
                    // 切换当前条目删除按钮的显示状态
                    delBtn.style.display = 'block';
                }
            }
        }

        // ==========================================
        // 核心亮点：全静态库无缝搜索功能逻辑
        // ==========================================
        searchInput.oninput = function(e) {
            const query = e.target.value.trim().toLowerCase();
            const calWrapper = document.getElementById('calendarWrapper');
            const calControls = document.getElementById('calendarControls');
            const slideIndicator = document.getElementById('slideIndicator');
            const list = document.getElementById('feedList');
            
            if (query) {
                calWrapper.style.display = 'none';
                calControls.style.display = 'none';
                if(slideIndicator) slideIndicator.style.display = 'none';
                
                let resultsHtml = '';
                let matchCount = 0;
                
                for (const y in archiveData) {
                    for (const m in archiveData[y]) {
                        for (const d in archiveData[y][m]) {
                            const items = archiveData[y][m][d];
                            items.forEach(item => {
                                const inOriginal = item.original && item.original.toLowerCase().includes(query);
                                const inTitle = item.title && item.title.toLowerCase().includes(query);
                                
                                if (inOriginal || inTitle) {
                                    matchCount++;
                                    const datePrefix = `${m.toString().padStart(2, '0')}-${d.toString().padStart(2, '0')}`;
                                    resultsHtml += `
                                        <div class="feed-item" onclick="handleItemClick(event, '${item.path}')">
                                            <span class="feed-time" style="min-width: 55px; font-size: 0.85rem; color: #e74c3c; background: #fdedec; border-radius: 6px; padding: 2px 4px;">${datePrefix}</span>
                                            <span class="feed-title">${item.title}</span>
                                            <button class="delete-btn" style="display:none;" onclick="event.stopPropagation(); confirmDelete('${item.path}', this)">删除</button>
                                        </div>`;
                                }
                            });
                        }
                    }
                }
                
                if (matchCount > 0) {
                    list.innerHTML = resultsHtml;
                } else {
                    list.innerHTML = '<div style="text-align:center; padding: 35px 20px; color:#bdc3c7; font-size: 0.9rem;">🔍 未检索到匹配的解构档案</div>';
                }
            } else {
                calWrapper.style.display = 'block';
                calControls.style.display = 'flex';
                if(slideIndicator) slideIndicator.style.display = 'block';
                renderCalendar();
                renderList();
            }
        };

        // 云端同步删除条目记录
        async function confirmDelete(path, btnElement) {
            if(!confirm("确定要删除这条解构档案吗？此操作不可恢复。")) return;
            
            const token = localStorage.getItem('GH_TOKEN');
            if(!token) {
                alert("请先配置 GitHub Token！");
                document.getElementById('modal').style.display='flex';
                return;
            }
            
            // 构建相对于仓库根目录的文件路径
            const apiPath = 'docs/' + path;
            
            btnElement.innerText = "正在删除...";
            btnElement.disabled = true;
            
            try {
                // 1. 先通过 GET 获取待删除文件的 sha 码
                const getRes = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${apiPath}`, {
                    headers: { 'Authorization': `token ${token}` }
                });
                
                if(!getRes.ok) {
                    alert("获取云端文件信息失败，文件可能已被删除。");
                    btnElement.innerText = "删除";
                    btnElement.disabled = false;
                    return;
                }
                const fileData = await getRes.json();
                
                // 2. 携带 sha 码发起 DELETE 物理清除请求
                const delRes = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${apiPath}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `token ${token}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: `Macondo Matrix Delete: 删除档案 ${path}`,
                        sha: fileData.sha
                    })
                });
                
                if(delRes.ok) {
                    // 3. 从本地内存变量中剥离已被销毁的条目
                    removeRecordFromData(path);
                    
                    // DOM 直接物理消灭该节点
                    const itemEl = btnElement.closest('.feed-item');
                    if(itemEl) itemEl.remove();
                    
                    // 如果不是在搜索模式下，立刻刷新日历和红点状态
                    if (document.getElementById('calendarWrapper').style.display !== 'none') {
                        renderCalendar();
                        renderList();
                    }
                } else {
                    const err = await delRes.json();
                    alert("删除失败: " + err.message);
                    btnElement.innerText = "删除";
                    btnElement.disabled = false;
                }
            } catch(e) {
                alert("网络或 API 请求发生异常: " + e.message);
                btnElement.innerText = "删除";
                btnElement.disabled = false;
            }
        }

        // 从全局的 JSON 缓存树中剔除已被删除的条目
        function removeRecordFromData(path) {
            for (const y in archiveData) {
                for (const m in archiveData[y]) {
                    for (const d in archiveData[y][m]) {
                        archiveData[y][m][d] = archiveData[y][m][d].filter(item => item.path !== path);
                    }
                }
            }
        }
        
        yearSelect.onchange = e => { sY = parseInt(e.target.value); renderCalendar(); renderList(); };
        monthSelect.onchange = e => { sM = parseInt(e.target.value); renderCalendar(); renderList(); };
        
        initSelects(); 
        renderCalendar(); 
        renderList();

        function ensureYearOption(y) {
            let found = false;
            for(let i=0; i<yearSelect.options.length; i++){
                if(parseInt(yearSelect.options[i].value) === y) { found = true; break; }
            }
            if(!found) {
                const opt = document.createElement('option'); opt.value = y; opt.textContent = y + '年';
                yearSelect.appendChild(opt);
                let opts = Array.from(yearSelect.options);
                opts.sort((a,b) => parseInt(b.value) - parseInt(a.value));
                yearSelect.innerHTML = '';
                opts.forEach(o => yearSelect.appendChild(o));
            }
        }

        function updateUI() {
            ensureYearOption(sY);
            yearSelect.value = sY;
            monthSelect.value = sM;
            renderCalendar();
            renderList();
        }

        document.getElementById('prevMonthBtn').onclick = () => { 
            sM--; 
            if (sM < 1) { sM = 12; sY--; } 
            updateUI(); 
        };
        
        document.getElementById('nextMonthBtn').onclick = () => { 
            sM++; 
            if (sM > 12) { sM = 1; sY++; } 
            updateUI(); 
        };
        
        document.getElementById('todayBtn').onclick = () => { 
            sY = today.getFullYear(); 
            sM = today.getMonth() + 1; 
            sD = today.getDate(); 
            updateUI(); 
        };

        function saveSettings() {
            localStorage.setItem('GH_TOKEN', document.getElementById('gh-token').value.trim());
            document.getElementById('modal').style.display = 'none';
        }

        function escapeHTML(str) {
            return str.replace(/&/g, '&amp;')
                      .replace(/</g, '&lt;')
                      .replace(/>/g, '&gt;')
                      .replace(/"/g, '&quot;')
                      .replace(/'/g, '&#039;');
        }

        async function pushToGitHub() {
            const token = localStorage.getItem('GH_TOKEN');
            if(!token) {
                document.getElementById('modal').style.display='flex';
                return;
            }
            
            const original = document.getElementById('in-original').value.trim();
            const analysis = document.getElementById('in-analysis').value.trim();
            
            if(!original || !analysis) return alert("原文和分析均不能为空！");
            
            let autoTitle = original.substring(0, 25).replace(/\\n/g, ' ');
            if (original.length > 25) autoTitle += '...';
            
            const btn = document.getElementById('pushBtn');
            btn.innerText = "⏳ 跨海直推中..."; btn.disabled = true;
            
            const targetHtml = generateTemplate(autoTitle, original, analysis);
            
            const now = new Date();
            const y = now.getFullYear();
            const m = String(now.getMonth()+1).padStart(2, '0');
            const d = String(now.getDate()).padStart(2, '0');
            const h = String(now.getHours()).padStart(2, '0');
            const mn = String(now.getMinutes()).padStart(2, '0');
            
            const filePath = `docs/${y}/${m}/${y}_${m}_${d}_${h}${mn}.html`;
            
            try {
                const utf8Encode = new TextEncoder().encode(targetHtml);
                const binaryString = String.fromCodePoint(...utf8Encode);
                const base64Html = btoa(binaryString);

                const res = await fetch(`https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/contents/${filePath}`, {
                    method: 'PUT',
                    headers: { 'Authorization': `token ${token}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: `Macondo Matrix Record: ${autoTitle}`,
                        content: base64Html
                    })
                });
                
                if(res.ok) {
                    alert("🎉 记录成功！日历将在几秒后自动刷新。");
                    document.getElementById('in-original').value = '';
                    document.getElementById('in-analysis').value = '';
                    document.getElementById('viewport').scrollTo({ left: 0, behavior: 'smooth' });
                } else {
                    const err = await res.json();
                    alert("❌ 失败: " + err.message);
                }
            } catch(e) { alert("网络错误: " + e.message); }
            
            btn.innerText = "🚀 推送至云端矩阵"; btn.disabled = false;
        }

        function generateTemplate(title, orig, anal) {
            const safeOrig = escapeHTML(orig);
            const safeAnal = escapeHTML(anal);
            
            return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>${title}</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></scr` + `ipt>
    <style>
        :root { --bg: #fcfcfc; --surface: #ffffff; --text: #2c3e50; --border: #ecf0f1; --accent: #6c5ce7; --highlight: #fef9e7; }
        body { font-family: -apple-system, "Segoe UI", sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: 0 auto; padding-bottom: 50px;}
        .nav-back { margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;}
        .nav-back a { text-decoration: none; color: white; background: var(--text); padding: 8px 18px; border-radius: 20px; font-size: 0.9rem; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .sync-status { font-size: 0.85rem; color: #27ae60; font-weight: bold; display: none; }
        
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
        .card-header { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #95a5a6; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 12px; font-weight: bold;}
        
        .markdown-body { font-size: 1.05rem; line-height: 1.6; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 { color: var(--accent); margin-top: 16px; margin-bottom: 8px; font-weight: 700; border-bottom: 1px dashed #eee; padding-bottom: 4px; }
        #view-original p { margin-bottom: 16px; color: #34495e; font-family: Georgia, serif; font-size: 1.15rem; line-height: 1.8; }
        #view-original p:last-child { margin-bottom: 0; }
        
        .markdown-body p { margin-top: 0; margin-bottom: 12px; }
        .markdown-body ul, .markdown-body ol { margin-top: 0; margin-bottom: 8px; padding-left: 20px; }
        .markdown-body li { margin-bottom: 4px; }
        .markdown-body blockquote { margin: 0 0 10px 0; padding: 10px 15px; background: var(--highlight); border-left: 5px solid #f1c40f; color: #5c4d22; font-family: Georgia, serif; font-size: 1.1rem; border-radius: 0 8px 8px 0; }
        .markdown-body hr { border: 0; border-top: 1px dashed #bdc3c7; margin: 15px 0; }
        .markdown-body table { width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 0.95rem; }
        .markdown-body th, .markdown-body td { border: 1px solid var(--border); padding: 8px; text-align: left; }
        .markdown-body th { background: #f8f9fa; color: var(--accent); }
        .edit-textarea { width: 100%; min-height: 150px; padding: 15px; font-family: monospace; font-size: 1.05rem; border: 2px solid var(--accent); border-radius: 10px; box-sizing: border-box; resize: vertical; display: none; background: #fff; color: #2c3e50; line-height: 1.5; outline: none; box-shadow: 0 4px 15px rgba(41,128,185,0.1);}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-back">
            <a href="../../index.html">🔙 返回矩阵枢纽</a>
            <span class="sync-status" id="sync-status">📡 同步中...</span>
        </div>
        
        <textarea id="raw-original" style="display:none;">${safeOrig}</textarea>
        <textarea id="raw-analysis" style="display:none;">${safeAnal}</textarea>

        <div class="card">
            <div class="card-header">📖 原始文本 (Original)</div>
            <div id="view-original" class="markdown-body" style="white-space: pre-wrap; font-family: Georgia, serif; font-size: 1.15rem; line-height: 1.8; color: #34495e;"></div>
        </div>

        <div class="card" id="block-analysis">
            <div class="card-header">🔬 深度解构 (Analysis)</div>
            <div id="view-analysis" class="markdown-body"></div>
            <textarea id="edit-analysis" class="edit-textarea"></textarea>
        </div>
    </div>

    <script>
        const GH_OWNER = "moodHappy";
        const GH_REPO = "OneHundredYearsReading";

        function renderAll() {
            document.getElementById('view-original').textContent = document.getElementById('raw-original').value;
            const analContent = document.getElementById('raw-analysis').value;
            
            try {
                if (typeof marked !== 'undefined') {
                    document.getElementById('view-analysis').innerHTML = marked.parse(analContent);
                }
            } catch(e) { console.error("Markdown failed", e); }
        }
        window.onload = renderAll;

        const viewBlock = document.getElementById('view-analysis');
        const editBlock = document.getElementById('edit-analysis');
        const statusMsg = document.getElementById('sync-status');

        viewBlock.addEventListener('dblclick', triggerEdit);
        viewBlock.addEventListener('touchstart', e => {
            if (e.touches.length === 2) triggerEdit(); 
        });

        function triggerEdit() {
            viewBlock.style.display = 'none';
            editBlock.style.display = 'block';
            editBlock.value = document.getElementById('raw-analysis').value;
            editBlock.focus();
        }

        function escapeHTML(str) {
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
        }

        function reconstructSelfHTML(newAnal) {
            const orig = document.getElementById('raw-original').value;
            const safeOrig = escapeHTML(orig);
            const safeAnal = escapeHTML(newAnal);
            
            const template = \`<!DOCTYPE html>\\n<html lang="zh-CN">\\n<head>\\n\` + document.head.innerHTML + \`\\n</head>\\n<body>\\n\` +
            \`    <div class="container">\\n\` +
            \`        <div class="nav-back">\\n\` +
            \`            <a href="../../index.html">🔙 返回矩阵枢纽</a>\\n\` +
            \`            <span class="sync-status" id="sync-status">📡 同步中...</span>\\n\` +
            \`        </div>\\n\\n\` +
            \`        <textarea id="raw-original" style="display:none;">\${safeOrig}</textarea>\\n\` +
            \`        <textarea id="raw-analysis" style="display:none;">\${safeAnal}</textarea>\\n\\n\` +
            \`        <div class="card">\\n\` +
            \`            <div class="card-header">📖 原始文本 (Original)</div>\\n\` +
            \`            <div id="view-original" class="markdown-body" style="white-space: pre-wrap; font-family: Georgia, serif; font-size: 1.15rem; line-height: 1.8; color: #34495e;"></div>\\n\` +
            \`        </div>\\n\\n\` +
            \`        <div class="card" id="block-analysis">\\n\` +
            \`            <div class="card-header">🔬 深度解构 (Analysis)</div>\\n\` +
            \`            <div id="view-analysis" class="markdown-body"></div>\\n\` +
            \`            <textarea id="edit-analysis" class="edit-textarea"></textarea>\\n\` +
            \`        </div>\\n\` +
            \`    </div>\\n\\n\` +
            \`    <script>\\n\` + renderAll.toString() + \`\\n\` +
            \`    window.onload = renderAll;\\n\` +
            \`    const viewBlock = document.getElementById('view-analysis');\\n\` +
            \`    const editBlock = document.getElementById('edit-analysis');\\n\` +
            \`    const statusMsg = document.getElementById('sync-status');\\n\` +
            \`    viewBlock.addEventListener('dblclick', triggerEdit);\\n\` +
            \`    viewBlock.addEventListener('touchstart', e => { if (e.touches.length === 2) triggerEdit(); });\\n\` +
            \`    \` + triggerEdit.toString() + \`\\n\` +
            \`    \` + escapeHTML.toString() + \`\\n\` +
            \`    \` + reconstructSelfHTML.toString() + \`\\n\` +
            \`    const GH_OWNER = "\${GH_OWNER}"; const GH_REPO = "\${GH_REPO}";\\n\` +
            \`    editBlock.addEventListener('blur', \` + editBlock.onblur.toString() + \`);\\n\` +
            \`    </scr\` + \`ipt>\\n</body>\\n</html>\`;
            return template;
        }

        editBlock.onblur = async function() {
            const newText = editBlock.value.trim();
            const oldText = document.getElementById('raw-analysis').value.trim();
            
            editBlock.style.display = 'none';
            viewBlock.style.display = 'block';
            
            if (newText && newText !== oldText) {
                document.getElementById('raw-analysis').value = newText;
                renderAll();
                
                const token = localStorage.getItem('GH_TOKEN');
                if(!token) return;

                statusMsg.style.display = 'block';
                statusMsg.style.color = '#2980b9';
                statusMsg.innerText = '📡 静默同步中...';
                
                const pureHtml = reconstructSelfHTML(newText);
                const path = window.location.pathname;
                const fileRelPath = path.substring(path.indexOf('docs/'));
                
                try {
                    const utf8Encode = new TextEncoder().encode(pureHtml);
                    const binaryString = String.fromCodePoint(...utf8Encode);
                    const base64Html = btoa(binaryString);

                    const getRes = await fetch(\`https://api.github.com/repos/\${GH_OWNER}/\${GH_REPO}/contents/\${fileRelPath}\`, {
                        headers: { 'Authorization': \`token \${token}\` }
                    });
                    const fileData = await getRes.json();
                    
                    const putRes = await fetch(\`https://api.github.com/repos/\${GH_OWNER}/\${GH_REPO}/contents/\${fileRelPath}\`, {
                        method: 'PUT',
                        headers: { 'Authorization': \`token \${token}\`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: \`Auto-save analysis update\`,
                            content: base64Html,
                            sha: fileData.sha
                        })
                    });
                    
                    if(putRes.ok) {
                        statusMsg.style.color = '#27ae60';
                        statusMsg.innerText = '✅ 云端已同步';
                        setTimeout(() => statusMsg.style.display = 'none', 3000);
                    } else {
                        statusMsg.style.color = '#e74c3c';
                        statusMsg.innerText = '❌ 同步失败';
                    }
                } catch(e) {
                    statusMsg.style.color = '#e74c3c';
                    statusMsg.innerText = '❌ 网络断开';
                }
            }
        };
        editBlock.addEventListener('blur', editBlock.onblur);

    </scr` + `ipt>
</body>
</html>`;
        }
    </script>
</body>
</html>"""

    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content.replace("REPLACEME_JSON_DATA", json_data))
    print("🚀 枢纽引擎编译完毕！")

if __name__ == "__main__":
    generate_index()
