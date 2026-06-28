import requests
import base64
import datetime
import json
import re

# ==========================================
# ⚙️ 配置区：请在此处填入你的信息
# ==========================================
GITHUB_TOKEN = ""  # 留空：请在本地手动填写你的 GitHub Personal Access Token
REPO_NAME = "你的用户名/你的仓库名"  # 例如: "moodHappy/syntax-calendar"
BRANCH = "main"    # 你的默认分支名称
# ==========================================

def upload_to_github(path, content, message):
    """通过 GitHub API 上传文件到指定路径"""
    if not GITHUB_TOKEN or not REPO_NAME or "你的用户名" in REPO_NAME:
        print("❌ 拦截：请先在脚本顶部配置 GITHUB_TOKEN 和 REPO_NAME")
        return False

    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. 查询文件是否已存在（为了获取 SHA 以覆盖旧文件）
    r_get = requests.get(url, headers=headers)
    sha = r_get.json().get("sha") if r_get.status_code == 200 else None

    # 2. 构建推送数据 (内容必须是 Base64 编码)
    data = {
        "message": message,
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha

    # 3. 执行推送
    r_put = requests.put(url, headers=headers, json=data)
    if r_put.status_code in (200, 201):
        print(f"✅ 成功推送到仓库: {path}")
        return True
    else:
        print(f"❌ 推送失败 {path}: {r_put.json()}")
        return False

def build_calendar_index():
    """从远程仓库抓取结构，生成并推送日历索引 index.html"""
    print("🔍 正在拉取仓库最新的文件树...")
    tree_url = f"https://api.github.com/repos/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    r = requests.get(tree_url, headers=headers)
    if r.status_code != 200:
        print(f"❌ 获取文件树失败: {r.text}")
        return

    tree = r.json().get("tree", [])
    html_files = []
    
    # 严格匹配 docs/年份/月份/xxx.html 的结构
    pattern = re.compile(r"^docs/(\d{4})/(\d{2})/(.*?\.html)$")

    for item in tree:
        match = pattern.match(item["path"])
        if match and "index.html" not in item["path"]:
            year, month, filename = match.groups()
            html_files.append(f"{year}/{month}/{filename}")

    # 按时间倒序排列（最新的在最上面）
    html_files.sort(reverse=True)

    # 动态生成包含日历 UI 的 HTML（数据以 JSON 格式注入 JS）
    files_json = json.dumps(html_files)
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Syntax Calendar</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; background: #f6f8fa; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ border-bottom: 2px solid #eaecef; padding-bottom: 10px; color: #24292e; }}
        .year-group {{ margin-top: 24px; color: #0366d6; border-left: 4px solid #0366d6; padding-left: 10px; }}
        .month-group {{ margin-top: 16px; margin-left: 16px; color: #586069; font-size: 1.1em; }}
        ul {{ list-style-type: none; padding-left: 20px; }}
        li {{ margin: 8px 0; padding: 6px; background: #f1f8ff; border-radius: 4px; }}
        a {{ color: #0366d6; text-decoration: none; display: block; }}
        a:hover {{ text-decoration: underline; color: #005cc5; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>📚 Syntax Analysis Calendar</h1>
        <div id="calendar-container"></div>
    </div>

    <script>
        const files = {files_json};
        const container = document.getElementById('calendar-container');

        if(files.length === 0) {{
            container.innerHTML = '<p>暂无语法分析记录。</p>';
        }} else {{
            let currentYear = '';
            let currentMonth = '';
            let html = '';

            files.forEach(path => {{
                const parts = path.split('/');
                const year = parts[0];
                const month = parts[1];
                const filename = decodeURIComponent(parts[2]);

                if (year !== currentYear) {{
                    html += `<h2 class="year-group">🗓️ ${{year}}年</h2>`;
                    currentYear = year;
                    currentMonth = ''; 
                }}
                if (month !== currentMonth) {{
                    if (currentMonth !== '') html += '</ul>';
                    html += `<h3 class="month-group">${{month}}月</h3><ul>`;
                    currentMonth = month;
                }}

                html += `<li><a href="${{path}}">${{filename}}</a></li>`;
            }});
            html += '</ul>';
            container.innerHTML = html;
        }}
    </script>
</body>
</html>
"""
    print("⚙️ 正在生成并推送最新的日历索引 (index.html)...")
    upload_to_github("docs/index.html", index_content, "Calendar: Rebuild index")


def main():
    # ---------------------------------------------------------
    # 这里是你实际要推送的 HTML 语法分析内容。
    # 实际使用中，可以写代码读取你本地的分析结果文件赋值给 html_content
    # ---------------------------------------------------------
    html_content = """
    <html>
    <head><title>Syntax Analysis</title></head>
    <body>
        <h2>这是一个新的句子分析测试</h2>
        <p>自动生成的结构测试。</p>
    </body>
    </html>
    """

    # 获取当前时间，自动按 年、月 生成文件夹结构
    now = datetime.datetime.now()
    year_str = now.strftime("%Y")
    month_str = now.strftime("%m")
    date_str = now.strftime("%Y%m%d_%H%M%S") # 用作文件名防止重复

    # 构建路径：docs/年/月/文件名.html
    file_path = f"docs/{year_str}/{month_str}/analysis_{date_str}.html"

    print(f"🚀 开始执行推送任务...\n目标保存路径: {file_path}")

    # 第一步：把新内容推送到 年/月 文件夹下
    is_success = upload_to_github(file_path, html_content, f"Add syntax analysis for {year_str}-{month_str}")
    
    # 第二步：推送成功后，自动触发重新抓取结构并更新 index.html
    if is_success:
        build_calendar_index()
        print("🎉 所有操作已完成！现在打开你仓库的 GitHub Pages 就能看到最新的日历分类了。")

if __name__ == "__main__":
    main()
