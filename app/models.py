from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


class TranslationStage(Enum):
    """翻译阶段枚举类，定义翻译的不同阶段状态"""
    TRANSLATED = "translated"   # 初始翻译完成
    OPTIMIZED = "optimized"     # 优化润色完成
    HUMAN_REVIEWED = "human_reviewed" # 人工审核修订完成


class GlossaryType(Enum):
    """术语表类型枚举类，定义术语表的不同类型"""
    CHAR = 'char'     # 角色名称类术语
    TERM = 'term'     # 普通术语类


@dataclass(slots=True)
class Project:
    """小说翻译项目数据模型
    
    用于存储和管理小说翻译项目的基本信息，包括项目ID、名称、作者、
    类型、描述、源语言和目标语言等核心信息。
    """
    id: str  # 项目唯一标识符
    name: str  # 小说名称
    author: str = ""  # 小说作者
    genre: str = ""  # 小说类型/流派
    description: str = ""  # 小说简介/描述
    source_language: str = "zh"  # 源语言，默认为中文
    target_language: str = "en"  # 目标语言，默认为英文
    metadata: Dict[str, Any] = field(default_factory=dict)  # 项目元数据，存储额外信息


@dataclass(slots=True)
class Chapter:
    """小说章节数据模型
    
    用于存储小说章节的详细信息，包括章节ID、所属项目ID、标题、内容、
    摘要、角色列表和术语列表等。
    """
    id: int  # 章节唯一标识符
    project_id: str  # 所属项目的唯一标识符
    title: str  # 章节标题
    content: str  # 章节原始内容
    summary: str = ""  # 章节内容摘要
    characters: List[str] = field(default_factory=list)  # 章节中出现的角色列表
    terminologies: List[str] = field(default_factory=list)  # 章节中出现的术语列表
    metadata: Dict[str, Any] = field(default_factory=dict)  # 章节元数据，存储额外信息


@dataclass(slots=True)
class Glossary:
    """术语表数据模型
    
    用于存储和管理翻译项目中的术语信息，包括术语ID、所属项目ID、
    源语言术语、术语类型、翻译、备注等。
    """
    id: int  # 术语唯一标识符
    project_id: str  # 所属项目的唯一标识符
    source: str  # 源语言术语原文
    type: GlossaryType  # 术语类型（角色或普通术语）
    translation: str  # 目标语言翻译
    notes: str = ""  # 术语翻译备注或说明
    metadata: Dict[str, Any] = field(default_factory=dict)  # 术语元数据，存储额外信息


@dataclass(slots=True)
class Translation:
    """翻译结果数据模型
    
    用于存储章节的翻译结果，包括项目ID、章节ID、翻译阶段、翻译内容、
    验证信息、元数据以及创建和更新时间等。
    """
    project_id: str  # 所属项目的唯一标识符
    chapter_id: int  # 所属章节的唯一标识符
    stage: TranslationStage  # 当前翻译所处的阶段
    content: str  # 翻译后的内容
    validation: Dict[str, Any] = field(default_factory=dict)  # 翻译质量验证信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 翻译元数据，存储额外信息
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))  # 翻译创建时间（UTC）
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))  # 翻译最后更新时间（UTC）


def utc_now() -> datetime:
    """获取当前UTC时间的辅助函数
    
    返回:
        datetime: 当前UTC时间对象
    """
    return datetime.now(timezone.utc)
