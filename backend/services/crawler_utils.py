"""
爬虫工具类
提供通用的爬虫功能：请求管理、重试机制、反爬处理等
"""
import asyncio
import random
from typing import Dict, Optional, List
import httpx
from bs4 import BeautifulSoup
import json


class CrawlerUtils:
    """爬虫工具类"""

    # User-Agent池
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    @staticmethod
    def get_random_user_agent() -> str:
        """获取随机User-Agent"""
        return random.choice(CrawlerUtils.USER_AGENTS)

    @staticmethod
    def get_common_headers(referer: Optional[str] = None) -> Dict[str, str]:
        """获取通用请求头"""
        headers = {
            "User-Agent": CrawlerUtils.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    @staticmethod
    async def fetch_with_retry(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        data: Optional[Dict] = None,
        max_retries: int = 3,
        timeout: float = 10.0,
        delay: float = 1.0
    ) -> Optional[httpx.Response]:
        """
        带重试机制的HTTP请求

        Args:
            url: 请求URL
            headers: 请求头
            method: 请求方法
            data: POST数据
            max_retries: 最大重试次数
            timeout: 超时时间
            delay: 重试延迟

        Returns:
            Response对象或None
        """
        if headers is None:
            headers = CrawlerUtils.get_common_headers()

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    else:
                        raise ValueError(f"不支持的HTTP方法: {method}")

                    if response.status_code == 200:
                        return response
                    elif response.status_code == 429:  # Too Many Requests
                        print(f"请求过于频繁，等待{delay * (attempt + 1)}秒后重试...")
                        await asyncio.sleep(delay * (attempt + 1))
                    else:
                        print(f"请求失败，状态码: {response.status_code}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(delay)

            except httpx.TimeoutException:
                print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
            except Exception as e:
                print(f"请求出错: {e} (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)

        return None

    @staticmethod
    def parse_json_response(response: httpx.Response) -> Optional[Dict]:
        """解析JSON响应"""
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None

    @staticmethod
    def parse_html_response(response: httpx.Response) -> Optional[BeautifulSoup]:
        """解析HTML响应"""
        try:
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"HTML解析失败: {e}")
            return None

    @staticmethod
    def extract_text(element, default: str = "") -> str:
        """安全提取元素文本"""
        if element:
            return element.get_text(strip=True)
        return default

    @staticmethod
    def extract_attr(element, attr: str, default: str = "") -> str:
        """安全提取元素属性"""
        if element:
            return element.get(attr, default)
        return default


class RateLimiter:
    """请求频率限制器"""

    def __init__(self, max_requests: int = 10, time_window: float = 60.0):
        """
        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """获取请求许可"""
        async with self.lock:
            now = asyncio.get_event_loop().time()

            # 清理过期的请求记录
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

            # 如果达到限制，等待
            if len(self.requests) >= self.max_requests:
                oldest_request = self.requests[0]
                wait_time = self.time_window - (now - oldest_request)
                if wait_time > 0:
                    print(f"请求频率限制，等待 {wait_time:.2f} 秒...")
                    await asyncio.sleep(wait_time)
                    # 重新清理
                    now = asyncio.get_event_loop().time()
                    self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

            # 记录本次请求
            self.requests.append(now)
