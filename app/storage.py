"""
小说翻译项目的数据存储模块

该模块提供对Directus CMS的CRUD操作封装，用于管理小说翻译项目的数据，
包括项目、章节、术语表和翻译结果的数据操作。
"""

from typing import Dict, Any, List, Optional, Union
import logging

from .directus_cms import DirectusCms
from .models import TranslationStage, GlossaryType

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Storage:
    """小说翻译项目数据存储类
    
    提供对小说翻译项目数据的CRUD操作，包括项目、章节、术语表和翻译结果的管理。
    """
    
    def __init__(self, cms_client: DirectusCms):
        """
        初始化存储类
        
        Args:
            cms_client: Directus CMS客户端实例
        """
        self.cms = cms_client
    
    # ==================== 项目相关操作 ====================
    
    def create_project(self, project_id: str, name: str, author: str = "", genre: str = "",
                      description: str = "", source_language: str = "zh", 
                      target_language: str = "en", metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        创建新的翻译项目
        
        Args:
            project_id: 项目唯一标识符
            name: 小说名称
            author: 小说作者
            genre: 小说类型/流派
            description: 小说简介/描述
            source_language: 源语言，默认为中文
            target_language: 目标语言，默认为英文
            metadata: 项目元数据，存储额外信息
            
        Returns:
            创建成功返回项目数据字典，失败返回None
        """
        project_data = {
            "id": project_id,
            "name": name,
            "author": author,
            "genre": genre,
            "description": description,
            "source_language": source_language,
            "target_language": target_language,
            "metadata": metadata or {}
        }
        
        return self.cms.create_item("projects", project_data)
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个项目信息
        
        Args:
            project_id: 项目唯一标识符
            
        Returns:
            成功返回项目数据字典，失败返回None
        """
        return self.cms.get_item("projects", project_id)
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        更新项目信息
        
        Args:
            project_id: 项目唯一标识符
            **kwargs: 要更新的项目字段
            
        Returns:
            更新成功返回项目数据字典，失败返回None
        """
        return self.cms.update_item("projects", project_id, kwargs)
    
    def list_projects(self, limit: int = 25, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        获取项目列表
        
        Args:
            limit: 返回记录数限制
            offset: 偏移量
            
        Returns:
            成功返回项目数据列表，失败返回None
        """
        query = f"limit={limit}&offset={offset}"
        result = self.cms.get_items("projects", query)
        return result if isinstance(result, list) else None
    
    def delete_project(self, project_id: str) -> bool:
        """
        删除项目
        
        Args:
            project_id: 项目唯一标识符
            
        Returns:
            删除成功返回True，失败返回False
        """
        return self.cms.delete_item("projects", project_id)
    
    # ==================== 章节相关操作 ====================
    
    def create_chapter(self, project_id: str, title: str, content: str = None, 
                      chapter_number: int = None, summary: str = "", 
                      characters: List[str] = None, terminologies: List[str] = None,
                      metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        创建新的章节
        
        Args:
            project_id: 所属项目的唯一标识符
            title: 章节标题
            content: 章节原始内容
            chapter_number: 章节顺序索引，从1开始
            summary: 章节内容摘要
            characters: 章节中出现的角色列表
            terminologies: 章节中出现的术语列表
            metadata: 章节元数据，存储额外信息
            
        Returns:
            创建成功返回章节数据字典，失败返回None
        """
        chapter_data = {
            "project_id": project_id,
            "title": title,
            "content": content or "",
            "index": chapter_number or 1,
            "summary": summary,
            "characters": characters or [],
            "terminologies": terminologies or [],
            "metadata": metadata or {}
        }
        
        return self.cms.create_item("chapters", chapter_data)
    
    def get_chapter(self, project_id: str, chapter_index: int) -> Optional[Dict[str, Any]]:
        """
        获取单个章节信息
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_index: 章节顺序索引
            
        Returns:
            成功返回章节数据字典，失败返回None
        """
        # 通过项目ID和章节索引查询
        query = f"filter[project_id][_eq]={project_id}&filter[index][_eq]={chapter_index}"
        result = self.cms.get_items("chapters", query)
        
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    
    def update_chapter(self, project_id: str, chapter_index: int, **kwargs) -> Optional[Dict[str, Any]]:
        """
        更新章节信息
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_index: 章节顺序索引
            **kwargs: 要更新的章节字段
            
        Returns:
            更新成功返回章节数据字典，失败返回None
        """
        # 先获取章节ID
        chapter = self.get_chapter(project_id, chapter_index)
        if not chapter:
            logger.error(f"未找到项目 {project_id} 的第 {chapter_index} 章")
            return None
            
        chapter_id = chapter.get("id")
        return self.cms.update_item("chapters", chapter_id, kwargs)
    
    def list_chapters(self, project_id: str, limit: int = 25, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        获取章节列表
        
        Args:
            project_id: 所属项目的唯一标识符
            limit: 返回记录数限制
            offset: 偏移量
            
        Returns:
            成功返回章节数据列表，失败返回None
        """
        query = f"filter[project_id][_eq]={project_id}&limit={limit}&offset={offset}&sort=index"
        result = self.cms.get_items("chapters", query)
        return result if isinstance(result, list) else None
    
    def delete_chapter(self, project_id: str, chapter_index: int) -> bool:
        """
        删除章节
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_index: 章节顺序索引
            
        Returns:
            删除成功返回True，失败返回False
        """
        # 先获取章节ID
        chapter = self.get_chapter(project_id, chapter_index)
        if not chapter:
            logger.error(f"未找到项目 {project_id} 的第 {chapter_index} 章")
            return False
            
        chapter_id = chapter.get("id")
        return self.cms.delete_item("chapters", chapter_id)
    
    # ==================== 术语表相关操作 ====================
    
    def create_glossary(self, project_id: str, source: str, type: Union[str, GlossaryType], 
                       translation: str, notes: str = "", 
                       metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        创建新的术语表条目
        
        Args:
            project_id: 所属项目的唯一标识符
            source: 源语言术语原文
            type: 术语类型（角色或普通术语）
            translation: 目标语言翻译
            notes: 术语翻译备注或说明
            metadata: 术语元数据，存储额外信息
            
        Returns:
            创建成功返回术语表数据字典，失败返回None
        """
        # 处理术语类型
        if isinstance(type, GlossaryType):
            type_str = type.value
        else:
            type_str = type
            
        glossary_data = {
            "project_id": project_id,
            "source": source,
            "type": type_str,
            "translation": translation,
            "notes": notes,
            "metadata": metadata or {}
        }
        
        return self.cms.create_item("glossaries", glossary_data)
    
    def get_glossary(self, project_id: str, glossary_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个术语表条目
        
        Args:
            project_id: 所属项目的唯一标识符
            glossary_id: 术语表条目ID
            
        Returns:
            成功返回术语表数据字典，失败返回None
        """
        return self.cms.get_item("glossaries", glossary_id)
    
    def get_glossary_by_source(self, project_id: str, source: str) -> Optional[Dict[str, Any]]:
        """
        根据源术语获取术语表条目
        
        Args:
            project_id: 所属项目的唯一标识符
            source: 源语言术语原文
            
        Returns:
            成功返回术语表数据字典，失败返回None
        """
        query = f"filter[project_id][_eq]={project_id}&filter[source][_eq]={source}"
        result = self.cms.get_items("glossaries", query)
        
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    
    def update_glossary(self, project_id: str, glossary_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """
        更新术语表条目
        
        Args:
            project_id: 所属项目的唯一标识符
            glossary_id: 术语表条目ID
            **kwargs: 要更新的术语表字段
            
        Returns:
            更新成功返回术语表数据字典，失败返回None
        """
        return self.cms.update_item("glossaries", glossary_id, kwargs)
    
    def list_glossaries(self, project_id: str, limit: int = 25, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        获取术语表条目列表
        
        Args:
            project_id: 所属项目的唯一标识符
            limit: 返回记录数限制
            offset: 偏移量
            
        Returns:
            成功返回术语表数据列表，失败返回None
        """
        query = f"filter[project_id][_eq]={project_id}&limit={limit}&offset={offset}"
        result = self.cms.get_items("glossaries", query)
        return result if isinstance(result, list) else None
    
    def delete_glossary(self, project_id: str, glossary_id: int) -> bool:
        """
        删除术语表条目
        
        Args:
            project_id: 所属项目的唯一标识符
            glossary_id: 术语表条目ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        return self.cms.delete_item("glossaries", glossary_id)
    
    # ==================== 翻译相关操作 ====================
    
    def create_translation(self, project_id: str, chapter_id: int, stage: Union[str, TranslationStage], 
                          content: str, validation: Dict[str, Any] = None,
                          metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        创建新的翻译结果
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_id: 所属章节的唯一标识符
            stage: 当前翻译所处的阶段
            content: 翻译后的内容
            validation: 翻译质量验证信息
            metadata: 翻译元数据，存储额外信息
            
        Returns:
            创建成功返回翻译数据字典，失败返回None
        """
        # 处理翻译阶段
        if isinstance(stage, TranslationStage):
            stage_str = stage.value
        else:
            stage_str = stage
            
        translation_data = {
            "project_id": project_id,
            "chapter_id": chapter_id,
            "stage": stage_str,
            "content": content,
            "validation": validation or {},
            "metadata": metadata or {}
        }
        
        return self.cms.create_item("translations", translation_data)
    
    def get_translation(self, project_id: str, chapter_id: int, stage: Union[str, TranslationStage] = None) -> Optional[Dict[str, Any]]:
        """
        获取翻译结果
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_id: 所属章节的唯一标识符
            stage: 翻译阶段（可选）
            
        Returns:
            成功返回翻译数据字典，失败返回None
        """
        query = f"filter[project_id][_eq]={project_id}&filter[chapter_id][_eq]={chapter_id}"
        
        if stage:
            # 处理翻译阶段
            if isinstance(stage, TranslationStage):
                stage_str = stage.value
            else:
                stage_str = stage
            query += f"&filter[stage][_eq]={stage_str}"
            
        query += "&sort=-updated_at"  # 按更新时间降序排列，获取最新的翻译
        
        result = self.cms.get_items("translations", query)
        
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None
    
    def update_translation(self, project_id: str, chapter_id: int, stage: Union[str, TranslationStage], **kwargs) -> Optional[Dict[str, Any]]:
        """
        更新翻译结果
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_id: 所属章节的唯一标识符
            stage: 当前翻译所处的阶段
            **kwargs: 要更新的翻译字段
            
        Returns:
            更新成功返回翻译数据字典，失败返回None
        """
        # 先获取翻译ID
        translation = self.get_translation(project_id, chapter_id, stage)
        if not translation:
            logger.error(f"未找到项目 {project_id} 章节 {chapter_id} 阶段 {stage} 的翻译")
            return None
            
        translation_id = translation.get("id")
        return self.cms.update_item("translations", translation_id, kwargs)
    
    def list_translations(self, project_id: str, chapter_id: int = None, stage: Union[str, TranslationStage] = None,
                         limit: int = 25, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        获取翻译结果列表
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_id: 所属章节的唯一标识符（可选）
            stage: 翻译阶段（可选）
            limit: 返回记录数限制
            offset: 偏移量
            
        Returns:
            成功返回翻译数据列表，失败返回None
        """
        query = f"filter[project_id][_eq]={project_id}"
        
        if chapter_id:
            query += f"&filter[chapter_id][_eq]={chapter_id}"
            
        if stage:
            # 处理翻译阶段
            if isinstance(stage, TranslationStage):
                stage_str = stage.value
            else:
                stage_str = stage
            query += f"&filter[stage][_eq]={stage_str}"
            
        query += f"&limit={limit}&offset={offset}&sort=-updated_at"
        
        result = self.cms.get_items("translations", query)
        return result if isinstance(result, list) else None
    
    def delete_translation(self, project_id: str, chapter_id: int, stage: Union[str, TranslationStage]) -> bool:
        """
        删除翻译结果
        
        Args:
            project_id: 所属项目的唯一标识符
            chapter_id: 所属章节的唯一标识符
            stage: 当前翻译所处的阶段
            
        Returns:
            删除成功返回True，失败返回False
        """
        # 先获取翻译ID
        translation = self.get_translation(project_id, chapter_id, stage)
        if not translation:
            logger.error(f"未找到项目 {project_id} 章节 {chapter_id} 阶段 {stage} 的翻译")
            return False
            
        translation_id = translation.get("id")
        return self.cms.delete_item("translations", translation_id)