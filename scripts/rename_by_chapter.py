#!/usr/bin/env python3
"""
重命名 md 目录中的文件，根据其内容中的章节号进行重命名。
从 「卷四十三之二」 提取并改为 043_02.md 格式。

用法：
    python scripts/rename_by_chapter.py [--dry-run]
"""

import os
import re
import sys
import argparse
from pathlib import Path


def parse_chapter_title(content):
    """
    从 markdown 文件内容中提取章节号。

    支持格式：
    - 卷三目録 -> (3, None)
    - 卷一之一 -> (1, 1)
    - 卷十之一 -> (10, 1)
    - 卷一百之十二 -> (100, 12)
    - 卷一百二之七 -> (102, 7)
    - 卷一百六之一 -> (106, 1)

    返回: (卷数, 之数) 或 (卷数, None) 或 None
    """
    # 优先查找 "# 卷...之..." 格式
    pattern_with_section = r'^#\s+卷([一二三四五六七八九十百]+)之([一二三四五六七八九十百]+)'
    # 备选查找 "# 卷...目録" 或 "# 卷..." 格式（无"之"）
    pattern_without_section = r'^#\s+卷([一二三四五六七八九十百]+)(?:目録)?$'

    for line in content.split('\n'):
        # 先尝试匹配带"之"的格式
        match = re.match(pattern_with_section, line)
        if match:
            volume_str = match.group(1)
            section_str = match.group(2)

            volume_num = chinese_to_number(volume_str)
            section_num = chinese_to_number(section_str)

            return (volume_num, section_num)

        # 再尝试匹配不带"之"的格式
        match = re.match(pattern_without_section, line)
        if match:
            volume_str = match.group(1)
            volume_num = chinese_to_number(volume_str)

            return (volume_num, None)

    return None


def chinese_to_number(chinese_str):
    """
    将中文数字转换为阿拉伯数字。

    例如：
    - 一 -> 1
    - 十 -> 10
    - 四十三 -> 43
    - 一百 -> 100
    - 一百二 -> 102
    - 一百六 -> 106
    """
    chinese_nums = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100
    }

    # 处理简单数字
    if len(chinese_str) == 1:
        return chinese_nums.get(chinese_str, 0)

    result = 0
    temp = 0

    for i, char in enumerate(chinese_str):
        if char == '百':
            if temp == 0:
                temp = 1
            result += temp * 100
            temp = 0
        elif char == '十':
            if temp == 0:
                temp = 1
            result += temp * 10
            temp = 0
        else:
            temp = chinese_nums.get(char, 0)

    result += temp

    return result


def format_chapter_number(volume, section):
    """
    格式化章节号为标准格式。

    例如：
    - (3, None) -> "003"
    - (43, 2) -> "043_02"
    - (1, 1) -> "001_01"
    - (106, 12) -> "106_12"
    """
    if section is None:
        return f"{volume:03d}"
    else:
        return f"{volume:03d}_{section:02d}"


def process_md_files(md_dir, dry_run=False):
    """
    处理 md 目录中的所有文件。
    """
    md_path = Path(md_dir)

    if not md_path.exists():
        print(f"错误: 目录 {md_dir} 不存在")
        return

    # 获取所有 .md 文件
    md_files = sorted(md_path.glob("KR3k0059_*.md"))

    print(f"找到 {len(md_files)} 个文件")
    print()

    renamed_count = 0
    failed_count = 0
    skipped_count = 0

    for file_path in md_files:
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取章节号
            chapter_info = parse_chapter_title(content)

            if chapter_info is None:
                print(f"❌ 跳过 {file_path.name}: 无法找到章节标题")
                skipped_count += 1
                continue

            volume, section = chapter_info
            new_name = format_chapter_number(volume, section)
            new_file_path = file_path.parent / f"{new_name}.md"

            # 如果文件名已经是目标格式，跳过
            if file_path.name == f"{new_name}.md":
                print(f"⏭️  跳过 {file_path.name}: 已经是正确的名称")
                skipped_count += 1
                continue

            # 检查目标文件是否已存在
            if new_file_path.exists() and new_file_path != file_path:
                print(f"⚠️  警告 {file_path.name} -> {new_name}.md: 目标文件已存在")
                failed_count += 1
                continue

            # 生成显示信息
            if section is None:
                chapter_display = f"卷{volume}"
            else:
                chapter_display = f"卷{volume}之{section}"

            if dry_run:
                print(f"[试运行] {file_path.name} -> {new_name}.md ({chapter_display})")
            else:
                file_path.rename(new_file_path)
                print(f"✓ {file_path.name} -> {new_name}.md ({chapter_display})")

            renamed_count += 1

        except Exception as e:
            print(f"❌ 处理 {file_path.name} 时出错: {e}")
            failed_count += 1

    print()
    print("=" * 60)
    print(f"处理完成!")
    print(f"  重命名: {renamed_count} 个文件")
    print(f"  跳过: {skipped_count} 个文件")
    print(f"  失败: {failed_count} 个文件")
    if dry_run:
        print()
        print("注意: 这是试运行，没有实际重命名文件。")
        print("要实际执行重命名，请运行: python scripts/rename_by_chapter.py")


def main():
    parser = argparse.ArgumentParser(
        description='根据章节号重命名 md 目录中的文件'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行，不实际重命名文件'
    )
    parser.add_argument(
        '--md-dir',
        default='md',
        help='md 文件所在目录（默认: md）'
    )

    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("试运行模式 - 不会实际重命名文件")
        print("=" * 60)
        print()

    process_md_files(args.md_dir, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
