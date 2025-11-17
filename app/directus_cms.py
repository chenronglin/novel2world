import requests
import logging
from typing import Optional, Dict, Any, Union

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectusCms:
    """
    CMS内容管理系统CRUD操作封装类
    
    提供对Directus CMS的基本操作，包括创建、读取、更新和删除数据项
    """
    
    def __init__(self, base_url: str = None, token: str = None, timeout: int = 30):
        """
        初始化CMS客户端
        
        Args:
            base_url: CMS服务的基础URL
            token: 认证令牌
            timeout: 请求超时时间（秒）
        """
        self.cms_base_url = base_url or 'http://118.195.150.71:8055'
        self.token = token or '23d3JXNyv4w09ZHtzKStqfDPoaA-aQ6z'
        self.timeout = timeout
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return

    @staticmethod
    def _handle_response(response: requests.Response) -> Optional[Dict[str, Any]]:
        """
        处理API响应
        
        Args:
            response: requests响应对象
            
        Returns:
            成功时返回数据字典，失败时返回None
        """
        try:
            response.raise_for_status()
            response_data = response.json()
            if 'data' in response_data:
                return response_data['data']
            elif 'errors' in response_data:
                logger.error(f"API错误: {response_data['errors']}")
                return None
            return response_data
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
        except ValueError as e:
            logger.error(f"JSON解析错误: {e}")
        return None

    def create_item(self, table_name: str, value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建一个数据项
        
        Args:
            table_name: 表名
            value: 要创建的数据
            
        Returns:
            创建成功返回数据项，失败返回None
        """
        cms_url = f'{self.cms_base_url}/items/{table_name}'
        try:
            response = requests.post(
                url=cms_url, 
                headers=self.headers, 
                json=value,
                timeout=self.timeout
            )
            return DirectusCms._handle_response(response)
        except Exception as e:
            logger.error(f"创建数据项失败: {e}")
            return None

    def get_items(self, table_name: str, query: str = "") -> Optional[Union[Dict[str, Any], list]]:
        """
        获取数据项列表
        
        Args:
            table_name: 表名
            query: 查询参数字符串
            
        Returns:
            成功返回数据列表或字典，失败返回None
        """
        cms_url = f'{self.cms_base_url}/items/{table_name}'
        if query:
            cms_url += f"?{query}"
            
        try:
            response = requests.get(
                url=cms_url, 
                headers=self.headers,
                timeout=self.timeout
            )
            return DirectusCms._handle_response(response)
        except Exception as e:
            logger.error(f"获取数据项失败: {e}")
            return None

    def get_item(self, table_name: str, item_id: int|str) -> Optional[Dict[str, Any]]:
        """
        获取单个数据项
        
        Args:
            table_name: 表名
            item_id: 数据项ID
            
        Returns:
            成功返回数据项，失败返回None
        """
        cms_url = f'{self.cms_base_url}/items/{table_name}/{item_id}'
        try:
            response = requests.get(
                url=cms_url, 
                headers=self.headers,
                timeout=self.timeout
            )
            return DirectusCms._handle_response(response)
        except Exception as e:
            logger.error(f"获取单个数据项失败: {e}")
            return None

    def update_item(self, table_name: str, item_id: int|str, value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新数据项
        
        Args:
            table_name: 表名
            item_id: 数据项ID
            value: 要更新的数据
            
        Returns:
            更新成功返回数据项，失败返回None
        """
        cms_url = f'{self.cms_base_url}/items/{table_name}/{item_id}'
        try:
            response = requests.patch(
                url=cms_url, 
                headers=self.headers, 
                json=value,
                timeout=self.timeout
            )
            return DirectusCms._handle_response(response)
        except Exception as e:
            logger.error(f"更新数据项失败: {e}")
            return None

    def delete_item(self, table_name: str, item_id: int|str) -> bool:
        """
        删除数据项
        
        Args:
            table_name: 表名
            item_id: 数据项ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        cms_url = f'{self.cms_base_url}/items/{table_name}/{item_id}'
        try:
            response = requests.delete(
                url=cms_url, 
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 204:  # No Content表示成功删除
                return True
            else:
                logger.error(f"删除失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"删除数据项失败: {e}")
            return False
