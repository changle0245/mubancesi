"""
数据库模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    content_structures = relationship("ContentStructure", back_populates="user", cascade="all, delete-orphan")
    generated_contents = relationship("GeneratedContent", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ContentStructure(Base):
    """内容结构模板"""
    __tablename__ = "content_structures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 模板名称
    description = Column(Text)  # 模板描述
    structure = Column(JSON, nullable=False)  # 结构定义（JSON格式）
    # structure格式示例：
    # {
    #   "sections": [
    #     {"name": "标题", "type": "title", "max_length": 30, "required": true},
    #     {"name": "开场钩子", "type": "hook", "max_length": 50, "required": true},
    #     {"name": "主要内容", "type": "content", "max_length": 500, "required": true},
    #     {"name": "行动号召", "type": "cta", "max_length": 30, "required": false},
    #     {"name": "话题标签", "type": "hashtags", "count": 5, "required": false}
    #   ]
    # }
    is_default = Column(Boolean, default=False)  # 是否为默认模板
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="content_structures")
    generated_contents = relationship("GeneratedContent", back_populates="structure")


class ChatSession(Base):
    """AI对话会话（用于创建内容结构）"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), default="新对话")
    messages = Column(JSON, nullable=False, default=list)  # 对话历史
    # messages格式: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    structure_id = Column(Integer, ForeignKey("content_structures.id"), nullable=True)  # 关联的结构ID（如果已保存）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="chat_sessions")


class GeneratedContent(Base):
    """生成的内容历史"""
    __tablename__ = "generated_contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    structure_id = Column(Integer, ForeignKey("content_structures.id"), nullable=True)
    keyword = Column(String(200), nullable=False)  # 搜索的关键词
    hot_materials = Column(JSON)  # 收集的热点素材
    generated_content = Column(JSON, nullable=False)  # 生成的内容
    # generated_content格式:
    # {
    #   "title": "...",
    #   "hook": "...",
    #   "content": "...",
    #   "cta": "...",
    #   "hashtags": ["tag1", "tag2"]
    # }
    platform_adaptations = Column(JSON)  # 各平台适配版本
    # platform_adaptations格式:
    # {
    #   "wechat": {"content": "...", "length": 1500},
    #   "xiaohongshu": {"content": "...", "length": 800},
    #   ...
    # }
    ai_model = Column(String(50))  # 使用的AI模型 (openai/deepseek)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # 过期时间（30天后）

    # 关系
    user = relationship("User", back_populates="generated_contents")
    structure = relationship("ContentStructure", back_populates="generated_contents")


class HotTopic(Base):
    """热点话题缓存"""
    __tablename__ = "hot_topics"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)  # 平台名称 (weibo/zhihu/douyin等)
    keyword = Column(String(200), nullable=False, index=True)  # 关键词
    title = Column(String(500), nullable=False)  # 热点标题
    content = Column(Text)  # 热点内容摘要
    url = Column(String(500))  # 来源URL
    hot_score = Column(Integer)  # 热度分数
    metadata = Column(JSON)  # 其他元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # 缓存过期时间

    def __repr__(self):
        return f"<HotTopic {self.platform}:{self.keyword}>"
