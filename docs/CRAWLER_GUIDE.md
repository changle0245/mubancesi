# 爬虫功能使用指南

## 概述

系统已实现真实的爬虫功能，支持从以下平台获取热点数据：

- ✅ **微博热搜** - 实时热搜榜
- ✅ **知乎热榜** - 热榜 + 搜索
- ✅ **百度热搜** - 实时热点榜
- ✅ **抖音热点** - 热搜榜
- ✅ **今日头条** - 热点板

## 功能特性

### 1. 智能搜索
- **关键词匹配**：自动匹配包含关键词的热点
- **模糊搜索**：不区分大小写
- **热度排序**：自动按热度值排序结果

### 2. 反爬虫处理
- **User-Agent轮换**：使用6个不同的UA随机切换
- **请求重试机制**：最多3次重试，支持指数退避
- **频率限制**：60秒内最多20个请求，防止被封
- **请求延迟**：自动延迟，避免触发反爬

### 3. 错误处理
- **超时处理**：10秒超时，自动重试
- **异常捕获**：优雅处理网络错误
- **降级策略**：失败时返回空结果，不影响其他平台

## 使用方法

### 基础搜索

```python
from backend.services.hot_search_service import hot_search_service

# 搜索包含"人工智能"的热点
results = await hot_search_service.search(
    keyword="人工智能",
    platforms=["weibo", "zhihu", "baidu"],  # 可选，默认搜索所有
    max_results=10  # 每个平台的最大结果数
)
```

### 获取平台热榜

```python
# 获取微博热搜榜（前20条）
hot_list = await hot_search_service.get_hot_list(
    platform="weibo",
    limit=20
)
```

### API调用

通过API接口调用：

```bash
POST /api/content/search-hot
Content-Type: application/json
Authorization: Bearer <token>

{
    "keyword": "人工智能",
    "platforms": ["weibo", "zhihu", "baidu"],
    "max_results": 10
}
```

## 各平台详解

### 1. 微博热搜

**数据来源**：`https://weibo.com/ajax/side/hotSearch`

**返回数据**：
- `title`: 热搜关键词
- `hot_score`: 热度值（raw_hot）
- `rank`: 排名
- `category`: 分类
- `label`: 标签（如"热"、"新"）

**特点**：
- 实时更新
- 热度值准确
- 包含排名信息

**示例结果**：
```json
{
    "platform": "weibo",
    "title": "AI技术突破",
    "content": "微博热搜第1位",
    "url": "https://s.weibo.com/weibo?q=%23AI技术突破%23",
    "hot_score": 5234567,
    "metadata": {
        "rank": 1,
        "category": "科技",
        "label": "热"
    }
}
```

### 2. 知乎热榜

**数据来源**：
- 热榜：`https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total`
- 搜索：`https://www.zhihu.com/api/v4/search_v3`

**返回数据**：
- `title`: 问题标题
- `content`: 内容摘要
- `url`: 知乎链接
- `hot_score`: 热度值（如"100万热度"）

**特点**：
- 双重搜索（热榜 + 搜索）
- 内容质量高
- 自动去除HTML标签

### 3. 百度热搜

**数据来源**：`https://top.baidu.com/board?tab=realtime`

**返回数据**：
- `title`: 热搜关键词
- `hot_score`: 热度值
- `rank`: 排名

**特点**：
- 爬取HTML页面
- 实时更新
- 全民关注的热点

### 4. 抖音热点

**数据来源**：`https://www.douyin.com/aweme/v1/web/hot/search/list/`

**返回数据**：
- `title`: 热点关键词
- `content`: 描述标签
- `hot_score`: 热度值
- `position`: 位置

**特点**：
- 年轻化热点
- 短视频相关
- 娱乐性强

### 5. 今日头条

**数据来源**：`https://www.toutiao.com/hot-event/hot-board/`

**返回数据**：
- `title`: 热点标题
- `content`: 摘要
- `url`: 详情链接
- `hot_score`: 热度值

**特点**：
- 综合类新闻
- 内容丰富
- 带有图片和摘要

## 注意事项

### ⚠️ 法律合规

1. **遵守robots.txt**：爬虫会尊重网站的robots.txt规则
2. **频率限制**：已内置频率限制，避免给服务器造成压力
3. **用途合规**：仅用于个人内容创作参考，不得用于商业数据买卖
4. **数据隐私**：不爬取用户隐私数据

### ⚠️ 技术限制

1. **反爬虫**：部分平台有严格的反爬虫机制
   - 微博：可能需要登录cookie（当前未实现）
   - 抖音：API可能变化
   - 百度：HTML结构可能变化

2. **数据时效性**：
   - 热榜数据实时变化
   - 建议缓存30分钟
   - 不要频繁刷新

3. **请求限制**：
   - 系统限制：60秒内最多20次请求
   - 建议间隔：每次请求间隔3秒以上

### ⚠️ 故障处理

如果某个平台爬取失败：
1. 检查网络连接
2. 检查平台是否更新了API
3. 查看控制台错误日志
4. 系统会自动跳过失败的平台，不影响其他平台

### ⚠️ 维护建议

爬虫可能需要定期维护：

1. **API变化**：平台可能修改API接口
2. **HTML结构变化**：页面结构可能改版
3. **反爬虫升级**：可能需要更新UA或添加cookie

**如何更新**：
编辑 `backend/services/hot_search_service.py`，修改对应平台的搜索方法。

## 扩展开发

### 添加新平台

1. 在 `HotSearchService` 类中添加新方法：

```python
async def search_newplatform(self, keyword: str, max_results: int = 10) -> List[Dict]:
    """搜索新平台热点"""
    await self.rate_limiter.acquire()

    try:
        url = "新平台API地址"
        headers = CrawlerUtils.get_common_headers()
        response = await CrawlerUtils.fetch_with_retry(url, headers=headers)

        if response:
            data = CrawlerUtils.parse_json_response(response)
            # 处理数据...
            return results

    except Exception as e:
        print(f"新平台搜索失败: {e}")

    return []
```

2. 在 `search()` 方法的默认平台列表中添加：

```python
if platforms is None:
    platforms = ["weibo", "zhihu", "baidu", "douyin", "toutiao", "newplatform"]
```

### 自定义User-Agent

编辑 `backend/services/crawler_utils.py`：

```python
USER_AGENTS = [
    "你的User-Agent 1",
    "你的User-Agent 2",
    ...
]
```

### 调整频率限制

在 `HotSearchService.__init__()` 中修改：

```python
self.rate_limiter = RateLimiter(
    max_requests=30,  # 增加到30次
    time_window=60.0  # 60秒窗口
)
```

## 性能优化

### 1. 添加缓存

当前使用内存缓存，可以升级到Redis：

```python
# 安装Redis
pip install redis aioredis

# 修改缓存实现
import aioredis

class HotSearchService:
    def __init__(self):
        self.redis = await aioredis.create_redis_pool('redis://localhost')

    async def get_cached(self, key):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_cache(self, key, value, expire=1800):
        await self.redis.setex(key, expire, json.dumps(value))
```

### 2. 并发优化

系统已使用 `asyncio.gather` 实现并发搜索，可以进一步优化：

```python
# 使用信号量限制并发数
semaphore = asyncio.Semaphore(5)  # 最多5个并发

async def search_with_semaphore(platform, keyword, max_results):
    async with semaphore:
        return await getattr(self, f"search_{platform}")(keyword, max_results)
```

### 3. 代理支持

如果需要使用代理：

```python
async with httpx.AsyncClient(
    timeout=timeout,
    proxies="http://proxy.example.com:8080"
) as client:
    response = await client.get(url, headers=headers)
```

## 问题排查

### 问题1：爬取失败

**现象**：所有平台都返回空结果

**排查步骤**：
1. 检查网络连接
2. 查看控制台日志
3. 手动访问API地址测试
4. 检查是否被平台封禁IP

**解决方案**：
- 增加请求间隔
- 使用代理
- 更新User-Agent

### 问题2：数据不准确

**现象**：返回的热点数据与网站不一致

**原因**：
- 热榜实时变化
- API缓存延迟
- 地域差异

**解决方案**：
- 缩短缓存时间
- 直接访问网站对比

### 问题3：请求频率限制

**现象**：提示"请求过于频繁"

**原因**：触发了系统的频率限制

**解决方案**：
- 等待60秒后重试
- 调整 `RateLimiter` 参数
- 减少搜索频率

## 最佳实践

1. **合理使用**：
   - 不要频繁刷新
   - 尽量使用缓存
   - 批量搜索多个关键词时，添加延迟

2. **错误处理**：
   - 始终检查返回结果是否为空
   - 为用户提供友好的错误提示
   - 记录错误日志便于排查

3. **性能考虑**：
   - 使用缓存减少请求
   - 并发搜索多个平台
   - 异步处理，不阻塞主线程

4. **合规运营**：
   - 添加来源标注
   - 尊重原创内容
   - 不抄袭，仅作参考

## 联系支持

如果遇到技术问题或有新功能建议：

1. 查看本文档
2. 查看代码注释
3. 提交Issue到GitHub

---

**慕班策思爬虫系统** - 高效、智能、合规 🚀
