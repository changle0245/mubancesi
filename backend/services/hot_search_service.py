"""
热点搜索服务 - 真实爬虫实现
支持从多个平台搜索热点内容
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from urllib.parse import quote
from backend.services.crawler_utils import CrawlerUtils, RateLimiter


class HotSearchService:
    """热点搜索服务"""

    def __init__(self):
        self.cache = {}  # 简单的内存缓存
        self.cache_duration = timedelta(minutes=30)
        self.rate_limiter = RateLimiter(max_requests=20, time_window=60.0)

    async def search(
        self,
        keyword: str,
        platforms: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        搜索热点内容

        Args:
            keyword: 搜索关键词
            platforms: 平台列表，如果为None则搜索所有平台
            max_results: 每个平台的最大结果数

        Returns:
            热点列表
        """
        # 默认搜索的平台
        if platforms is None:
            platforms = ["weibo", "zhihu", "baidu", "douyin", "toutiao"]

        # 并发搜索多个平台
        tasks = []
        for platform in platforms:
            if hasattr(self, f"search_{platform}"):
                tasks.append(getattr(self, f"search_{platform}")(keyword, max_results))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        hot_topics = []
        for result in results:
            if isinstance(result, list):
                hot_topics.extend(result)
            elif isinstance(result, Exception):
                print(f"搜索错误: {result}")

        # 按热度排序
        hot_topics.sort(key=lambda x: x.get("hot_score", 0), reverse=True)

        return hot_topics

    async def search_weibo(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """搜索微博热搜"""
        await self.rate_limiter.acquire()

        try:
            # 微博热搜榜API
            url = "https://weibo.com/ajax/side/hotSearch"
            headers = CrawlerUtils.get_common_headers(referer="https://weibo.com")

            response = await CrawlerUtils.fetch_with_retry(url, headers=headers)

            if response:
                data = CrawlerUtils.parse_json_response(response)
                if data:
                    hot_list = data.get("data", {}).get("realtime", [])

                    results = []
                    for item in hot_list:
                        word = item.get("word", "")
                        # 关键词匹配（不区分大小写）
                        if keyword.lower() in word.lower():
                            results.append({
                                "platform": "weibo",
                                "title": word,
                                "content": item.get("note", ""),
                                "url": f"https://s.weibo.com/weibo?q=%23{quote(word)}%23",
                                "hot_score": item.get("raw_hot", 0),
                                "metadata": {
                                    "rank": item.get("rank", 0),
                                    "category": item.get("category", ""),
                                    "label": item.get("label_name", ""),
                                    "flag": item.get("flag", 0)
                                }
                            })

                    # 如果没有找到匹配的，返回前N条热搜供参考
                    if not results and hot_list:
                        for item in hot_list[:max_results]:
                            word = item.get("word", "")
                            results.append({
                                "platform": "weibo",
                                "title": word,
                                "content": item.get("note", f"微博热搜第{item.get('rank', 0)}位"),
                                "url": f"https://s.weibo.com/weibo?q=%23{quote(word)}%23",
                                "hot_score": item.get("raw_hot", 0),
                                "metadata": {
                                    "rank": item.get("rank", 0),
                                    "category": item.get("category", ""),
                                }
                            })

                    return results[:max_results]

        except Exception as e:
            print(f"微博搜索失败: {e}")

        return []

    async def search_zhihu(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """搜索知乎热榜和内容"""
        await self.rate_limiter.acquire()

        results = []

        try:
            # 方法1: 知乎热榜API
            hot_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            headers = CrawlerUtils.get_common_headers(referer="https://www.zhihu.com")

            response = await CrawlerUtils.fetch_with_retry(hot_url, headers=headers)

            if response:
                data = CrawlerUtils.parse_json_response(response)
                if data:
                    hot_list = data.get("data", [])

                    for item in hot_list:
                        target = item.get("target", {})
                        title = target.get("title", "")

                        # 关键词匹配
                        if keyword.lower() in title.lower():
                            results.append({
                                "platform": "zhihu",
                                "title": title,
                                "content": target.get("excerpt", ""),
                                "url": target.get("url", ""),
                                "hot_score": int(item.get("detail_text", "0").replace("万热度", "").replace("热度", "") or 0),
                                "metadata": {
                                    "type": target.get("type", ""),
                                    "id": target.get("id", ""),
                                }
                            })

            # 方法2: 如果热榜没找到，搜索知乎内容
            if len(results) < max_results:
                search_url = f"https://www.zhihu.com/api/v4/search_v3?q={quote(keyword)}&t=general&offset=0&limit={max_results}"
                headers = CrawlerUtils.get_common_headers(referer="https://www.zhihu.com")

                response = await CrawlerUtils.fetch_with_retry(search_url, headers=headers)

                if response:
                    data = CrawlerUtils.parse_json_response(response)
                    if data:
                        items = data.get("data", [])

                        for item in items:
                            obj = item.get("object", {})
                            highlight = item.get("highlight", {})

                            title = highlight.get("title", obj.get("title", ""))
                            # 移除HTML标签
                            title = re.sub(r'<[^>]+>', '', title)

                            results.append({
                                "platform": "zhihu",
                                "title": title,
                                "content": obj.get("excerpt", "")[:200],
                                "url": obj.get("url", ""),
                                "hot_score": 0,
                                "metadata": {
                                    "type": item.get("type", ""),
                                    "id": obj.get("id", ""),
                                }
                            })

                            if len(results) >= max_results:
                                break

        except Exception as e:
            print(f"知乎搜索失败: {e}")

        return results[:max_results]

    async def search_baidu(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """搜索百度热搜"""
        await self.rate_limiter.acquire()

        try:
            # 百度实时热点榜
            url = "https://top.baidu.com/board?tab=realtime"
            headers = CrawlerUtils.get_common_headers(referer="https://top.baidu.com")

            response = await CrawlerUtils.fetch_with_retry(url, headers=headers)

            if response:
                soup = CrawlerUtils.parse_html_response(response)
                if soup:
                    results = []

                    # 查找热搜列表
                    hot_items = soup.select(".category-wrap_iQLoo .c-single-text-ellipsis")

                    for idx, item in enumerate(hot_items):
                        title = CrawlerUtils.extract_text(item)

                        # 关键词匹配
                        if keyword.lower() in title.lower() or not keyword:
                            # 尝试获取热度值
                            hot_score = 0
                            hot_element = item.find_next("div", class_="hot-index_1Bl1a")
                            if hot_element:
                                hot_text = CrawlerUtils.extract_text(hot_element)
                                # 提取数字
                                numbers = re.findall(r'\d+', hot_text)
                                if numbers:
                                    hot_score = int(numbers[0])

                            results.append({
                                "platform": "baidu",
                                "title": title,
                                "content": f"百度热搜第{idx + 1}位",
                                "url": f"https://www.baidu.com/s?wd={quote(title)}",
                                "hot_score": hot_score,
                                "metadata": {
                                    "rank": idx + 1
                                }
                            })

                        if len(results) >= max_results:
                            break

                    return results

        except Exception as e:
            print(f"百度搜索失败: {e}")

        return []

    async def search_douyin(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """搜索抖音热点"""
        await self.rate_limiter.acquire()

        try:
            # 抖音热点榜 - 使用移动端API
            url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
            headers = CrawlerUtils.get_common_headers(referer="https://www.douyin.com")

            response = await CrawlerUtils.fetch_with_retry(url, headers=headers)

            if response:
                data = CrawlerUtils.parse_json_response(response)
                if data:
                    word_list = data.get("data", {}).get("word_list", [])

                    results = []
                    for item in word_list:
                        word = item.get("word", "")

                        # 关键词匹配
                        if keyword.lower() in word.lower():
                            results.append({
                                "platform": "douyin",
                                "title": word,
                                "content": item.get("sentence_tag", ""),
                                "url": f"https://www.douyin.com/search/{quote(word)}",
                                "hot_score": item.get("hot_value", 0),
                                "metadata": {
                                    "position": item.get("position", 0),
                                    "label": item.get("label", ""),
                                }
                            })

                    # 如果没找到匹配的，返回前N条
                    if not results and word_list:
                        for item in word_list[:max_results]:
                            word = item.get("word", "")
                            results.append({
                                "platform": "douyin",
                                "title": word,
                                "content": item.get("sentence_tag", ""),
                                "url": f"https://www.douyin.com/search/{quote(word)}",
                                "hot_score": item.get("hot_value", 0),
                                "metadata": {
                                    "position": item.get("position", 0),
                                }
                            })

                    return results[:max_results]

        except Exception as e:
            print(f"抖音搜索失败: {e}")

        return []

    async def search_toutiao(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """搜索今日头条热点"""
        await self.rate_limiter.acquire()

        try:
            # 今日头条热榜
            url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
            headers = CrawlerUtils.get_common_headers(referer="https://www.toutiao.com")

            response = await CrawlerUtils.fetch_with_retry(url, headers=headers)

            if response:
                data = CrawlerUtils.parse_json_response(response)
                if data:
                    hot_list = data.get("data", [])

                    results = []
                    for item in hot_list:
                        title = item.get("Title", "")

                        # 关键词匹配
                        if keyword.lower() in title.lower():
                            results.append({
                                "platform": "toutiao",
                                "title": title,
                                "content": item.get("Abstract", ""),
                                "url": item.get("Url", ""),
                                "hot_score": item.get("HotValue", 0),
                                "metadata": {
                                    "cluster_id": item.get("ClusterId", ""),
                                    "image_url": item.get("Image", {}).get("url", ""),
                                }
                            })

                    # 如果没找到匹配的，返回前N条
                    if not results and hot_list:
                        for item in hot_list[:max_results]:
                            results.append({
                                "platform": "toutiao",
                                "title": item.get("Title", ""),
                                "content": item.get("Abstract", ""),
                                "url": item.get("Url", ""),
                                "hot_score": item.get("HotValue", 0),
                                "metadata": {
                                    "cluster_id": item.get("ClusterId", ""),
                                }
                            })

                    return results[:max_results]

        except Exception as e:
            print(f"今日头条搜索失败: {e}")

        return []

    async def get_hot_list(self, platform: str, limit: int = 20) -> List[Dict]:
        """
        获取指定平台的热榜列表（不需要关键词）

        Args:
            platform: 平台名称
            limit: 返回数量

        Returns:
            热点列表
        """
        if hasattr(self, f"search_{platform}"):
            # 传入空关键词来获取热榜
            return await getattr(self, f"search_{platform}")("", limit)
        return []


# 创建全局实例
hot_search_service = HotSearchService()
