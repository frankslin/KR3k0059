#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并目录文件和内容文件
奇数号文件为目录，偶数号文件为内容
将两者合并，只保留一份 frontmatter
"""

import os
import re
from pathlib import Path


def extract_frontmatter_and_content(file_path):
    """提取 frontmatter 和正文内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 frontmatter
    frontmatter_pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        frontmatter = match.group(1)
        body = match.group(2)
        return frontmatter, body
    else:
        return None, content


def merge_files(md_dir, output_dir):
    """合并奇数号（目录）和偶数号（内容）文件"""
    md_path = Path(md_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 获取所有文件并按编号排序
    files = sorted(md_path.glob('KR3k0059_*.md'))

    # 提取文件编号
    file_dict = {}
    for file in files:
        match = re.search(r'KR3k0059_(\d+)\.md', file.name)
        if match:
            num = int(match.group(1))
            file_dict[num] = file

    # 合并文件
    merged_count = 0
    for num in sorted(file_dict.keys()):
        # 只处理奇数号文件（目录）
        if num % 2 == 1:
            catalog_file = file_dict.get(num)
            content_file = file_dict.get(num + 1)

            if catalog_file and content_file:
                print(f"合并 {catalog_file.name} 和 {content_file.name}")

                # 读取目录文件
                catalog_fm, catalog_body = extract_frontmatter_and_content(catalog_file)

                # 读取内容文件
                content_fm, content_body = extract_frontmatter_and_content(content_file)

                # 使用目录文件的 frontmatter（保留第一个）
                frontmatter = catalog_fm if catalog_fm else content_fm

                # 合并内容：目录 + 内容
                merged_content = f"---\n{frontmatter}\n---\n{catalog_body}\n{content_body}"

                # 输出文件名使用奇数号
                output_file = output_path / f"KR3k0059_{num:03d}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(merged_content)

                merged_count += 1
            elif catalog_file:
                print(f"警告: {catalog_file.name} 没有对应的内容文件")

    print(f"\n完成！共合并了 {merged_count} 对文件")
    print(f"输出目录: {output_path.absolute()}")


if __name__ == '__main__':
    # 源目录和输出目录
    source_dir = 'md'
    output_dir = 'merged'

    print(f"开始合并文件...")
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)

    merge_files(source_dir, output_dir)
