import os
import re
import zipfile
from pathlib import Path


# 预定义正则表达式和转换规则
PATTERNS = [
    (re.compile(r"\.apply\(\"(.*?)\"\s*>=\s*TO_TIMESTAMP\(\\?,\s*'YYYY-MM-DD HH24:MI:SS'\)\s*,\s*(\w+)\)"),
     "将 MyBatis .apply 方法中含有参数问号的代码改为直接拼接参数值",
     lambda match: f'.apply("{match.group(1)} >= TO_TIMESTAMP(" + {match.group(2)} + ", \"YYYY-MM-DD HH24:MI:SS\"))'),
    (re.compile(r"LIMIT\\s+\\d+(,?\\s*\\d+)?", re.IGNORECASE), "MySQL LIMIT 语法，Oracle 用 ROW_NUMBER() 或 FETCH FIRST", lambda match: "-- 替换为 ROW_NUMBER() 或 FETCH FIRST"),
    (re.compile(r"NOW\\(\\)", re.IGNORECASE), "MySQL NOW() 函数，Oracle 用 SYSDATE", lambda match: "SYSDATE"),
    (re.compile(r"IFNULL\\((.*?),\\s*(.*?)\\)", re.IGNORECASE), "MySQL IFNULL() 函数，Oracle 用 NVL()", lambda match: f"NVL({match.group(1)}, {match.group(2)})"),
    (re.compile(r"AUTO_INCREMENT", re.IGNORECASE), "MySQL AUTO_INCREMENT 语法，Oracle 用 SEQUENCE 和 TRIGGER", lambda match: "-- 替换为 SEQUENCE 和 TRIGGER"),
    (re.compile(r"CONCAT\\((.*?)\\)", re.IGNORECASE), "MySQL CONCAT() 函数，Oracle 用 ||", lambda match: " || ".join(match.group(1).split(','))),
    (re.compile(r"GROUP_CONCAT\\((.*?)\\)", re.IGNORECASE), "MySQL GROUP_CONCAT() 函数，Oracle 用 LISTAGG()", lambda match: f"LISTAGG({match.group(1)})"),
    (re.compile(r"DATE_FORMAT\\((.*?),\\s*(.*?)\\)", re.IGNORECASE), "MySQL DATE_FORMAT() 函数，Oracle 用 TO_CHAR()", lambda match: f"TO_CHAR({match.group(1)}, {match.group(2)})"),
    (re.compile(r"STR_TO_DATE\\((.*?),\\s*(.*?)\\)", re.IGNORECASE), "MySQL STR_TO_DATE() 函数，Oracle 用 TO_DATE()", lambda match: f"TO_DATE({match.group(1)}, {match.group(2)})"),

]

def scan_files_by_extension(target_dir, extensions):
    """扫描目录，按扩展名过滤文件"""
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(tuple(extensions)):
                yield os.path.join(root, file)

def process_line(line, patterns):
    """处理单行代码并返回转换后的结果和问题描述"""
    issues = []
    original_line = line
    for pattern, description, transformer in patterns:
        match = pattern.search(line)
        if match:
            # 针对 MyBatis 的特殊逻辑
            if description.startswith("MyBatis"):
                field_name = match.group(1).strip() if len(match.groups()) > 0 else ""
                if not ('date' in field_name.lower() or 'time' in field_name.lower()):
                    continue
            transformed_code = transformer(match)
            issues.append((description, original_line.strip(), transformed_code.strip()))
            line = pattern.sub(transformed_code, line)
    return line, issues

def analyze_file(file_path, patterns):
    """分析单个文件并记录问题"""
    issues_found = []
    modified_lines = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line_no, line in enumerate(file, start=1):
            modified_line, issues = process_line(line, patterns)
            if issues:
                for description, original, transformed in issues:
                    issues_found.append((description, original, transformed, line_no))
            modified_lines.append(modified_line)

    if issues_found:
        with open(file_path, 'w', encoding='utf-8') as mod_file:
            mod_file.writelines(modified_lines)

    return issues_found

def generate_report(file_issues, output_path):
    """生成问题报告"""
    report_lines = []
    for file_path, issues in file_issues.items():
        report_lines.append(f"文件: {file_path}")
        for description, original, transformed, line_no in issues:
            report_lines.append(f"  - 问题: {description}")
            report_lines.append(f"    原代码: {original}")
            report_lines.append(f"    修改后: {transformed}")
            report_lines.append(f"    行号: {line_no}")
        report_lines.append("")

    with open(output_path, 'w', encoding='utf-8') as report_file:
        report_file.write("\n".join(report_lines))

    print(f"分析完成，报告已生成: {output_path}")

def create_zip_file(file_paths, output_zip):
    """压缩文件"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            arcname = os.path.relpath(file_path, os.path.dirname(output_zip))
            zipf.write(file_path, arcname)
    print(f"需要转换的文件已打包: {output_zip}")

def scan_and_analyze(target_dir, output_zip):
    """扫描并分析目标目录中的文件，生成报告并打包修改后的文件"""
    file_issues = {}
    extensions = ['.java', '.xml']
    modified_files = []

    for file_path in scan_files_by_extension(target_dir, extensions):
        issues = analyze_file(file_path, PATTERNS)
        if issues:
            file_issues[file_path] = issues
            modified_files.append(file_path)

    if file_issues:
        report_path = os.path.join(target_dir, 'scan_report.txt')
        generate_report(file_issues, report_path)
        create_zip_file(modified_files, output_zip)
    else:
        print("未发现需要转换的问题。")

def main():
    target_dir = input("请输入要扫描的目录路径: ").strip()
    output_zip = os.path.join(target_dir, 'files_to_convert.zip')

    if not os.path.exists(target_dir):
        print("指定的目录不存在，请重新输入。")
        return

    scan_and_analyze(target_dir, output_zip)

if __name__ == "__main__":
    main()
