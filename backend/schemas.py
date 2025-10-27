"""
Pydantic数据模型（用于API请求和响应）
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ========== 用户相关 ==========

class UserCreate(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ========== AI对话相关 ==========

class ChatMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: Optional[int] = None  # 会话ID，如果是新对话则为None
    message: str
    ai_model: str = Field(default="openai", pattern="^(openai|deepseek)$")


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: int
    message: ChatMessage
    suggestions: Optional[List[str]] = None  # AI建议（如：建议保存为模板）


class ChatSessionResponse(BaseModel):
    """对话会话响应"""
    id: int
    title: str
    messages: List[Dict[str, str]]
    structure_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 内容结构相关 ==========

class ContentSection(BaseModel):
    """内容片段"""
    name: str
    type: str
    max_length: Optional[int] = None
    count: Optional[int] = None
    required: bool = True
    placeholder: Optional[str] = None


class ContentStructureCreate(BaseModel):
    """创建内容结构"""
    name: str
    description: Optional[str] = None
    structure: Dict[str, Any]  # {"sections": [ContentSection]}
    is_default: bool = False


class ContentStructureUpdate(BaseModel):
    """更新内容结构"""
    name: Optional[str] = None
    description: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


class ContentStructureResponse(BaseModel):
    """内容结构响应"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    structure: Dict[str, Any]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 热点搜索相关 ==========

class HotSearchRequest(BaseModel):
    """热点搜索请求"""
    keyword: str
    platforms: Optional[List[str]] = None  # 指定平台，如果为None则搜索所有平台
    max_results: int = Field(default=10, ge=1, le=50)


class HotTopicItem(BaseModel):
    """热点话题项"""
    platform: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    hot_score: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class HotSearchResponse(BaseModel):
    """热点搜索响应"""
    keyword: str
    topics: List[HotTopicItem]
    total: int


# ========== 内容生成相关 ==========

class ContentGenerateRequest(BaseModel):
    """内容生成请求"""
    keyword: str
    structure_id: int
    hot_topics: Optional[List[HotTopicItem]] = None  # 可以手动提供热点素材
    target_platforms: List[str] = Field(default=["wechat_official", "xiaohongshu", "douyin"])
    ai_model: str = Field(default="openai", pattern="^(openai|deepseek)$")
    user_style: Optional[str] = None  # 用户风格指南


class GeneratedContentResponse(BaseModel):
    """生成的内容响应"""
    id: int
    keyword: str
    generated_content: Dict[str, Any]
    platform_adaptations: Dict[str, Any]
    ai_model: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 历史记录相关 ==========

class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    items: List[GeneratedContentResponse]
    total: int
    page: int
    page_size: int


# ========== 系统配置相关 ==========

class PlatformInfo(BaseModel):
    """平台信息"""
    key: str
    name: str
    name_en: str
    category: str
    max_length: int
    title_length: Optional[int] = None
    style: str
    features: List[str]
    tips: str


class PlatformsResponse(BaseModel):
    """平台列表响应"""
    platforms: List[PlatformInfo]
    categories: Dict[str, Any]
