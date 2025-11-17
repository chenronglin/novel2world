import re
import os
from typing import List, Tuple, Dict
from app.storage import Storage
from app.directus_cms import DirectusCms

# 初始化存储实例
cms = DirectusCms(base_url="http://118.195.150.71:8055",
                  token="23d3JXNyv4w09ZHtzKStqfDPoaA-aQ6z")
storage = Storage(cms)


def chinese_to_number(chinese_str: str) -> int:
    """
    将中文数字转换为阿拉伯数字
    
    参数:
        chinese_str: 中文数字字符串
        
    返回:
        对应的阿拉伯数字
    """
    chinese_digits = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '百': 100, '千': 1000, '万': 10000, '亿': 100000000,
        '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5,
        '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10,
        '佰': 100, '仟': 1000
    }

    # 处理特殊情况，如"十"、"二十"等
    if chinese_str == '十':
        return 10
    elif chinese_str.startswith('十') and len(chinese_str) > 1:
        # 如"十一"、"十二"等
        return 10 + chinese_digits.get(chinese_str[1], 0)

    # 预处理：移除所有"零"字符，但在特定位置保留其占位作用
    processed = []
    for i, char in enumerate(chinese_str):
        if char == '零':
            # 如果"零"后面是单位（百、千、万等），保留"零"
            if i + 1 < len(chinese_str) and chinese_str[i + 1] in ['百', '千', '万', '亿']:
                processed.append(char)
            # 否则跳过"零"
        else:
            processed.append(char)

    processed_str = ''.join(processed)

    result = 0
    temp = 0

    for char in processed_str:
        if char in chinese_digits:
            digit = chinese_digits[char]
            if digit < 10:  # 数字
                temp = temp * 10 + digit
            else:  # 单位
                if temp == 0:
                    temp = 1
                result += temp * digit
                temp = 0
        else:
            # 如果不是中文数字字符，尝试直接转换为阿拉伯数字
            try:
                return int(chinese_str)
            except ValueError:
                pass

    return result + temp


def parse_chapter_title(title: str) -> Tuple[int, str]:
    """
    解析章节标题，分离章节号和标题
    
    参数:
        title: 原始章节标题，如"第四百零六章 星残、巫影离开"
        
    返回:
        元组(章节号, 标题)，如(406, "星残、巫影离开")
    """
    # 匹配"第X章"格式的标题
    match = re.match(r'^第(.+?)章\s*(.*)$', title)
    if match:
        number_str, title_part = match.groups()
        try:
            # 尝试直接转换为阿拉伯数字
            chapter_number = int(number_str)
        except ValueError:
            # 转换中文数字
            chapter_number = chinese_to_number(number_str)

        return chapter_number, title_part.strip()

    # 如果不匹配标准格式，尝试其他格式
    # 如"1. 标题"格式
    match = re.match(r'^(\d+)\.\s*(.*)$', title)
    if match:
        chapter_number = int(match.group(1))
        return chapter_number, match.group(2).strip()

    # 默认情况，将整个标题作为章节标题，章节号为0
    return 0, title.strip()


# noinspection PyArgumentList
def load_novel_document(document_path: str) -> str:
    """
    加载小说文档内容
    
    参数:
        document_path: 文档路径
        
    返回:
        文档内容字符串
        
    异常:
        FileNotFoundError: 当文件不存在时
        UnicodeDecodeError: 当文件编码不是UTF-8时
    """
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"文档文件不存在: {document_path}")

    try:
        with open(document_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"文档读取成功: {len(content)} 字符")
        return content
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(document_path, "r", encoding="gbk") as f:
                content = f.read()
            print(f"文档读取成功(GBK编码): {len(content)} 字符")
            return content
        except UnicodeDecodeError:
            raise UnicodeDecodeError("无法解码文档，请确保文档为UTF-8或GBK编码")


def identify_chapters(content: str) -> List[Tuple[int, str, int, str]]:
    """
    识别文档中的章节标记
    
    参数:
        content: 文档内容
        
    返回:
        章节信息列表，格式为[(行号, 原始标题, 章节号, 章节标题), ...]
    """
    lines = content.split('\n')
    chapter_info = []

    # 定义章节标题的正则表达式模式
    patterns = [
        r'^第[零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟0-9]+章\s*',  # 中文数字章节
        r'^第[0-9]+章\s*',  # 阿拉伯数字章节
        r'^(?:Chapter|CHAPTER)\s+[0-9IVXLC]+\s*',  # 英文章节
        r'^\s*[0-9]+\.\s*',  # 数字加点格式，如 "1. "
        r'^\s*第[0-9]+节\s*',  # 节格式
    ]

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:  # 跳过空行
            continue

        for pattern in patterns:
            if re.match(pattern, line_stripped):
                # 解析章节号和标题
                chapter_number, chapter_title = parse_chapter_title(line_stripped)
                chapter_info.append((i, line_stripped, chapter_number, chapter_title))
                break

    return chapter_info


def process_chapter_content(content: str) -> str:
    """
    处理章节内容，去掉每行开头的空格，并将连续的多个换行符替换为单个换行符
    
    参数:
        content: 原始章节内容
        
    返回:
        处理后的章节内容
    """
    # 去掉每行开头的空格
    lines = content.split('\n')
    stripped_lines = [line.lstrip() for line in lines]

    # 将连续的多个换行符替换为单个换行符
    processed_content = '\n'.join(stripped_lines)
    # 使用正则表达式将连续两个以上的换行符替换为单个换行符
    processed_content = re.sub(r'\n{2,}', '\n\n', processed_content)

    return processed_content


def split_chapters(content: str, chapter_info: List[Tuple[int, str, int, str]]) -> List[Dict[str, str]]:
    """
    根据章节标记分割文档内容
    
    参数:
        content: 文档内容
        chapter_info: 章节信息列表，格式为[(行号, 原始标题, 章节号, 章节标题), ...]
        
    返回:
        章节字典列表，每个字典包含章节号、标题和内容
    """
    lines = content.split('\n')
    chapters = []

    if not chapter_info:
        # 如果没有找到章节标记，将整个文档作为一章
        processed_content = process_chapter_content(content.strip())
        chapters.append({
            "number": 1,
            "title": "全文",
            "content": processed_content
        })
        return chapters

    for i, (line_num, original_title, chapter_number, chapter_title) in enumerate(chapter_info):
        # 确定章节内容的起始和结束位置
        start_line = line_num
        if i + 1 < len(chapter_info):
            end_line = chapter_info[i + 1][0]
        else:
            end_line = len(lines)

        # 提取章节内容
        chapter_lines = lines[start_line:end_line]
        chapter_text = "\n".join(chapter_lines).strip()

        # 处理章节内容：去掉每行开头的空格，并将连续的多个换行符替换为单个换行符
        processed_text = process_chapter_content(chapter_text)

        chapters.append({
            "number": chapter_number,
            "title": chapter_title,
            "original_title": original_title,
            "content": processed_text
        })

    return chapters


def save_chapters_to_storage(chapters: List[Dict[str, str]], project_id: str) -> None:
    """
    将章节保存到存储系统
    
    参数:
        chapters: 章节字典列表
        project_id: 项目ID
    """
    print(f"\n共识别到 {len(chapters)} 章")
    print("-" * 50)
    for chapter in chapters:
        result = storage.create_chapter(
            project_id, 
            chapter["title"], 
            chapter["content"], 
            int(chapter["number"])
        )
        if result:
            print(f"成功创建章节: {chapter['title']} (ID: {result.get('id')})")
        else:
            print(f"创建章节失败: {chapter['title']}")


def main():
    """
    主函数，执行文档加载和章节分割
    """
    # 获取用户输入的项目ID
    project_id = input("请输入项目ID: ").strip()
    if not project_id:
        print("错误: 项目ID不能为空")
        return None
    
    # 验证项目是否存在
    project = storage.get_project(project_id)
    if not project:
        print(f"错误: 项目ID '{project_id}' 不存在")
        return None
    
    print(f"已找到项目: {project.get('name', '未知项目')}")
    
    # 获取用户输入的文档路径
    default_document_path = "novels/《末世异神》.txt"
    document_path = input(f"请输入文档路径 (默认: {default_document_path}): ").strip()
    if not document_path:
        document_path = default_document_path

    try:
        # 加载文档
        content = load_novel_document(document_path)

        # 识别章节
        chapter_info = identify_chapters(content)
        print(f"识别到 {len(chapter_info)} 个章节标记")

        # 分割章节
        chapters = split_chapters(content, chapter_info)

        # 将章节保存到存储系统
        save_chapters_to_storage(chapters, project_id)

        return chapters

    except Exception as e:
        print(f"处理文档时出错: {str(e)}")
        return []


if __name__ == "__main__":
    main()
