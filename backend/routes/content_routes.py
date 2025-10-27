"""
内容生成和管理路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List
from datetime import datetime, timedelta
import yaml

from backend.database import get_db
from backend.models import User, ContentStructure, GeneratedContent
from backend.schemas import (
    ContentStructureCreate,
    ContentStructureUpdate,
    ContentStructureResponse,
    ContentGenerateRequest,
    GeneratedContentResponse,
    HotSearchRequest,
    HotSearchResponse,
    HistoryListResponse
)
from backend.auth import get_current_active_user
from backend.services.ai_service import ai_service
from backend.services.hot_search_service import hot_search_service

router = APIRouter(prefix="/api/content", tags=["内容管理"])

# 加载平台配置
with open("config/platforms.yaml", "r", encoding="utf-8") as f:
    platforms_config = yaml.safe_load(f)


@router.post("/structures", response_model=ContentStructureResponse)
async def create_structure(
    structure_data: ContentStructureCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建内容结构"""
    # 如果设置为默认，取消其他默认结构
    if structure_data.is_default:
        result = await db.execute(
            select(ContentStructure).where(
                ContentStructure.user_id == current_user.id,
                ContentStructure.is_default == True
            )
        )
        for old_default in result.scalars():
            old_default.is_default = False

    new_structure = ContentStructure(
        user_id=current_user.id,
        **structure_data.model_dump()
    )

    db.add(new_structure)
    await db.commit()
    await db.refresh(new_structure)

    return ContentStructureResponse.from_orm(new_structure)


@router.get("/structures", response_model=List[ContentStructureResponse])
async def get_structures(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的内容结构列表"""
    result = await db.execute(
        select(ContentStructure)
        .where(ContentStructure.user_id == current_user.id)
        .order_by(ContentStructure.is_default.desc(), ContentStructure.created_at.desc())
    )
    structures = result.scalars().all()
    return [ContentStructureResponse.from_orm(s) for s in structures]


@router.get("/structures/{structure_id}", response_model=ContentStructureResponse)
async def get_structure(
    structure_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取特定内容结构"""
    result = await db.execute(
        select(ContentStructure).where(
            ContentStructure.id == structure_id,
            ContentStructure.user_id == current_user.id
        )
    )
    structure = result.scalar_one_or_none()
    if not structure:
        raise HTTPException(status_code=404, detail="结构不存在")

    return ContentStructureResponse.from_orm(structure)


@router.put("/structures/{structure_id}", response_model=ContentStructureResponse)
async def update_structure(
    structure_id: int,
    structure_data: ContentStructureUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新内容结构"""
    result = await db.execute(
        select(ContentStructure).where(
            ContentStructure.id == structure_id,
            ContentStructure.user_id == current_user.id
        )
    )
    structure = result.scalar_one_or_none()
    if not structure:
        raise HTTPException(status_code=404, detail="结构不存在")

    # 更新字段
    for key, value in structure_data.model_dump(exclude_unset=True).items():
        setattr(structure, key, value)

    # 如果设置为默认，取消其他默认结构
    if structure_data.is_default:
        result = await db.execute(
            select(ContentStructure).where(
                ContentStructure.user_id == current_user.id,
                ContentStructure.id != structure_id,
                ContentStructure.is_default == True
            )
        )
        for old_default in result.scalars():
            old_default.is_default = False

    await db.commit()
    await db.refresh(structure)

    return ContentStructureResponse.from_orm(structure)


@router.delete("/structures/{structure_id}")
async def delete_structure(
    structure_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除内容结构"""
    result = await db.execute(
        select(ContentStructure).where(
            ContentStructure.id == structure_id,
            ContentStructure.user_id == current_user.id
        )
    )
    structure = result.scalar_one_or_none()
    if not structure:
        raise HTTPException(status_code=404, detail="结构不存在")

    await db.delete(structure)
    await db.commit()

    return {"message": "结构已删除"}


@router.post("/search-hot", response_model=HotSearchResponse)
async def search_hot_topics(
    request: HotSearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """搜索热点话题"""
    try:
        topics = await hot_search_service.search(
            keyword=request.keyword,
            platforms=request.platforms,
            max_results=request.max_results
        )

        from backend.schemas import HotTopicItem
        topic_items = [HotTopicItem(**topic) for topic in topics]

        return HotSearchResponse(
            keyword=request.keyword,
            topics=topic_items,
            total=len(topic_items)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/generate", response_model=GeneratedContentResponse)
async def generate_content(
    request: ContentGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """生成内容"""
    # 获取内容结构
    result = await db.execute(
        select(ContentStructure).where(
            ContentStructure.id == request.structure_id,
            ContentStructure.user_id == current_user.id
        )
    )
    structure = result.scalar_one_or_none()
    if not structure:
        raise HTTPException(status_code=404, detail="结构不存在")

    # 如果没有提供热点素材，先搜索
    if not request.hot_topics:
        topics = await hot_search_service.search(
            keyword=request.keyword,
            max_results=10
        )
        hot_materials = topics
    else:
        hot_materials = [topic.model_dump() for topic in request.hot_topics]

    try:
        # 生成内容
        generated_content = await ai_service.generate_content(
            hot_materials=hot_materials,
            structure=structure.structure,
            user_style=request.user_style,
            model=request.ai_model
        )

        # 适配到各平台
        platform_adaptations = {}
        for platform_key in request.target_platforms:
            if platform_key in platforms_config["platforms"]:
                platform_config = platforms_config["platforms"][platform_key]
                adapted_content = await ai_service.adapt_to_platform(
                    content=generated_content,
                    platform_config=platform_config,
                    model=request.ai_model
                )
                platform_adaptations[platform_key] = {
                    "content": adapted_content,
                    "length": len(adapted_content),
                    "platform_name": platform_config["name"]
                }

        # 保存到数据库
        new_content = GeneratedContent(
            user_id=current_user.id,
            structure_id=structure.id,
            keyword=request.keyword,
            hot_materials=hot_materials,
            generated_content=generated_content,
            platform_adaptations=platform_adaptations,
            ai_model=request.ai_model,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

        db.add(new_content)
        await db.commit()
        await db.refresh(new_content)

        return GeneratedContentResponse.from_orm(new_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容生成失败: {str(e)}")


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取历史记录"""
    # 只返回未过期的记录
    result = await db.execute(
        select(GeneratedContent)
        .where(
            GeneratedContent.user_id == current_user.id,
            or_(
                GeneratedContent.expires_at.is_(None),
                GeneratedContent.expires_at > datetime.utcnow()
            )
        )
        .order_by(GeneratedContent.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    contents = result.scalars().all()

    # 获取总数
    count_result = await db.execute(
        select(GeneratedContent)
        .where(
            GeneratedContent.user_id == current_user.id,
            or_(
                GeneratedContent.expires_at.is_(None),
                GeneratedContent.expires_at > datetime.utcnow()
            )
        )
    )
    total = len(count_result.scalars().all())

    return HistoryListResponse(
        items=[GeneratedContentResponse.from_orm(c) for c in contents],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/history/{content_id}", response_model=GeneratedContentResponse)
async def get_history_item(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取特定历史记录"""
    result = await db.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="记录不存在")

    return GeneratedContentResponse.from_orm(content)


@router.delete("/history/{content_id}")
async def delete_history_item(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除历史记录"""
    result = await db.execute(
        select(GeneratedContent).where(
            GeneratedContent.id == content_id,
            GeneratedContent.user_id == current_user.id
        )
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(content)
    await db.commit()

    return {"message": "记录已删除"}
