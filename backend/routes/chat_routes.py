"""
AI对话路由（用于创建内容结构）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.database import get_db
from backend.models import User, ChatSession
from backend.schemas import ChatRequest, ChatResponse, ChatMessage, ChatSessionResponse
from backend.auth import get_current_active_user
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发送对话消息"""
    # 获取或创建会话
    if request.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        # 创建新会话
        session = ChatSession(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
            messages=[]
        )
        db.add(session)
        await db.flush()

    # 添加用户消息
    messages = session.messages.copy() if session.messages else []
    messages.append({"role": "user", "content": request.message})

    # 调用AI
    try:
        system_message = {
            "role": "system",
            "content": "你是一个内容结构设计助手。帮助用户设计和优化内容创作的结构模板。当用户确定了一个满意的结构后，建议他们保存为模板。"
        }
        ai_messages = [system_message] + messages

        ai_response = await ai_service.chat(ai_messages, model=request.ai_model)

        # 添加AI回复
        messages.append({"role": "assistant", "content": ai_response})

        # 更新会话
        session.messages = messages
        await db.commit()
        await db.refresh(session)

        # 判断是否建议保存为模板
        suggestions = []
        if any(keyword in request.message.lower() for keyword in ["确定", "就这样", "很好", "可以", "保存"]):
            suggestions.append("是否要将这个结构保存为模板？")

        return ChatResponse(
            session_id=session.id,
            message=ChatMessage(role="assistant", content=ai_response),
            suggestions=suggestions if suggestions else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")


@router.post("/sessions/{session_id}/save-structure")
async def save_structure_from_chat(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """从对话中保存内容结构"""
    # 获取会话
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 使用AI分析对话并生成结构
    try:
        structure = await ai_service.create_structure_suggestion(
            session.messages,
            model="openai"
        )

        # 创建内容结构
        from backend.models import ContentStructure
        new_structure = ContentStructure(
            user_id=current_user.id,
            name=structure.get("name", "未命名结构"),
            description=structure.get("description"),
            structure=structure.get("structure", {}),
            is_default=False
        )

        db.add(new_structure)
        session.structure_id = new_structure.id
        await db.commit()
        await db.refresh(new_structure)

        from backend.schemas import ContentStructureResponse
        return ContentStructureResponse.from_orm(new_structure)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存结构失败: {str(e)}")


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的对话会话列表"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [ChatSessionResponse.from_orm(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取特定对话会话"""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return ChatSessionResponse.from_orm(session)


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除对话会话"""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    await db.delete(session)
    await db.commit()

    return {"message": "会话已删除"}
