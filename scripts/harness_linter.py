import argparse
import re
import sys
import os
import datetime

# Web3 Philosopher V26 强校验词库
FORBIDDEN_WORDS = [
    "颠覆性", "改变游戏规则", "史诗级", "巨大潜力", "无缝", "赋能", "创新", "的未来",
    "跨时代", "领先", "在这个", "不得不说", "让我们一起来", "揭秘", "不仅仅是",
    "全方位", "极致", "深度剖析", "一文带你", "把握机会", "革命性", "毋庸置疑",
    "大航海时代", "黑暗森林", "达摩克利斯之剑", "缸中之脑", "降维打击", "痛点"
]

JARGON_PATTERN = re.compile(r'[a-zA-Z0-9$]+')

def analyze_article(filepath):
    if not os.path.exists(filepath):
        print(f"Error: 文件不存在: {filepath}")
        sys.exit(1)

    filename = os.path.basename(filepath)
    is_short_post = "Short" in filename or "短帖" in filename
    is_long_post = "Long" in filename or "长文" in filename

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    full_text = "".join(lines)
    clean_text = re.sub(r'\s+', '', full_text)
    total_chars = len(clean_text)
    
    if total_chars == 0:
        print("Error: 文件为空。")
        sys.exit(1)

    has_error = False
    report_lines = [
        f"# Harness 审计报告: {filename}",
        f"**审计时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**文档类型**: {'短帖 (Short Post)' if is_short_post else '长文 (Long Article)'}",
        "---"
    ]

    # 1. 语义装甲审计
    report_lines.append("## 🛡️ 阶段 1: 语义装甲审计 (Lexicon Armor)")
    forbidden_hits = []
    for idx, line in enumerate(lines):
        line_num = idx + 1
        for word in FORBIDDEN_WORDS:
            if word in line:
                forbidden_hits.append((line_num, word, line.strip()))
    
    if forbidden_hits:
        report_lines.append(f"**状态**: ❌ 失败 (检测到 AI 指纹违禁词，共 {len(forbidden_hits)} 处)")
        for hit in forbidden_hits:
            report_lines.append(f"- [Line {hit[0]}] 匹配词: `{hit[1]}` | 原文: *{hit[2][:40]}...*")
        has_error = True
    else:
        report_lines.append("**状态**: ✅ 通过 (未检测到违禁词)。")

    # 2. 短帖排版审计
    if is_short_post:
        report_lines.append("\n## 📝 阶段 2: 排版审计 (Zero Markdown)")
        markdown_tags = ["**", "*", ">", "###", "##"]
        markdown_hits = []
        for idx, line in enumerate(lines):
            line_num = idx + 1
            if line.strip().startswith("#"): 
                if len(line.split()[0].replace("#", "")) == 0 and len(line.strip()) > 1:
                    markdown_hits.append((line_num, "Header", line.strip()))
                continue
            
            for tag in markdown_tags:
                if tag in line:
                    markdown_hits.append((line_num, tag, line.strip()))
        
        if markdown_hits:
            report_lines.append(f"**状态**: ❌ 失败 (短帖中检测到 Markdown 符号，共 {len(markdown_hits)} 处，违背 §3 铁律)")
            for hit in markdown_hits:
                report_lines.append(f"- [Line {hit[0]}] 命中: `{hit[1]}` | 原文: *{hit[2][:40]}...*")
            has_error = True
        else:
            report_lines.append("**状态**: ✅ 通过 (纯净文本，无 Markdown 污染)。")

    # 3. 灵魂注入指标审计 (Jargon Density)
    if is_long_post or not is_short_post:
        report_lines.append("\n## 🧮 阶段 3: 灵魂注入指标审计 (前 20% 防术语壁垒)")
        first_20_percent_char_count = int(total_chars * 0.2)
        current_chars = 0
        first_20_lines = []
        for line in lines:
            first_20_lines.append(line)
            current_chars += len(re.sub(r'\s+', '', line))
            if current_chars >= first_20_percent_char_count:
                break
        
        first_20_text = "".join(first_20_lines)
        first_20_clean = re.sub(r'\s+', '', first_20_text)
        
        jargons = JARGON_PATTERN.findall(first_20_text)
        jargon_char_count = sum(len(j) for j in jargons)
        density = (jargon_char_count / len(first_20_clean)) * 100 if len(first_20_clean) > 0 else 0
        
        report_lines.append(f"- **前 20% 字符数**: {len(first_20_clean)}")
        report_lines.append(f"- **技术术语/英文占比**: {density:.2f}%")
        
        if density > 5.0:
            report_lines.append(f"**状态**: ❌ 失败 (技术术语密度 {density:.2f}% > 5.0% 阈值！未完成世俗摩擦垫场)")
            report_lines.append(f"- 识别到的部分术语: `{', '.join(jargons[:15])}...`")
            has_error = True
        else:
            report_lines.append("**状态**: ✅ 通过 (术语密度健康，世俗场景构建成功)。")

    report_lines.append("\n---")
    
    if has_error:
        report_lines.append("## 🚨 最终结论: 审计不通过 (FAIL)")
        report_lines.append("存在认知崩塌点或机械化指纹，请参考报告退回重写。")
        print(f"FAIL: {filename} 包含错误。查看同目录下的审计报告。")
    else:
        report_lines.append("## 🛡️ 最终结论: 审计通过 (PASS)")
        report_lines.append("工业级品控符合标准，允许发布。")
        print(f"PASS: {filename} 审核通过。查看同目录下的审计报告。")
        
    report_path = filepath.replace('.md', '_AuditReport.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    if has_error:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web3 Philosopher Harness Linter")
    parser.add_argument("file", help="输入要审计的 markdown 文件路径")
    args = parser.parse_args()
    analyze_article(args.file)
