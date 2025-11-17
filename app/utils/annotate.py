
def get_glossaries_mapping(project_id: str) -> Dict[str, str]:
    """
    获取项目的术语名称映射（中文->英文）。

    Args:
        project_id: 项目ID

    Returns:
        Dict[str, str]: 角色映射字典
    """
    glossaries_map = {}
    try:
        glossaries = get_glossaries_by_project_id(project_id)
        for glossary in glossaries:
            if glossary.name and glossary.translation:
                glossaries_map[glossary.name] = glossary.translation
    except Exception as e:
        logger.error(f"获取术语映射失败: {e}")

    return glossaries_map   


def annotate_text(text: str, glossaries: Dict[str, str]) -> str:
    """
    将章节文本中的术语直接替换为对应的英文翻译。

    Args:
        text: 原始章节文本
        glossaries: 术语 glossary 映射，键为术语，值为英文翻译

    Returns:
        str: 部分翻译（角色和术语被替换为英文）后的文本
    """
    replaced_text = text
    # 将所有术语名按长度降序排序，构建一个大的正则表达式
    terms = sorted(glossaries.keys(), key=len, reverse=True)
    if terms:
        char_pattern = re.compile("|".join(re.escape(name) for name in terms))
        # 使用 re.sub 和一个替换函数，直接返回 map 中的英文 value
        replaced_text = char_pattern.sub(
            lambda match: glossaries_map[match.group(0)], replaced_text
        )
return replaced_text
