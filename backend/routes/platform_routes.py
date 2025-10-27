"""
平台信息路由
"""
from fastapi import APIRouter
from typing import List
import yaml

from backend.schemas import PlatformInfo, PlatformsResponse

router = APIRouter(prefix="/api/platforms", tags=["平台信息"])

# 加载平台配置
with open("config/platforms.yaml", "r", encoding="utf-8") as f:
    platforms_config = yaml.safe_load(f)


@router.get("", response_model=PlatformsResponse)
async def get_platforms():
    """获取所有平台信息"""
    platforms = []

    for key, config in platforms_config["platforms"].items():
        platforms.append(PlatformInfo(
            key=key,
            name=config["name"],
            name_en=config["name_en"],
            category=config["category"],
            max_length=config["max_length"],
            title_length=config.get("title_length"),
            style=config["style"],
            features=config["features"],
            tips=config["tips"]
        ))

    return PlatformsResponse(
        platforms=platforms,
        categories=platforms_config.get("categories", {})
    )


@router.get("/{platform_key}", response_model=PlatformInfo)
async def get_platform(platform_key: str):
    """获取特定平台信息"""
    if platform_key not in platforms_config["platforms"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="平台不存在")

    config = platforms_config["platforms"][platform_key]
    return PlatformInfo(
        key=platform_key,
        name=config["name"],
        name_en=config["name_en"],
        category=config["category"],
        max_length=config["max_length"],
        title_length=config.get("title_length"),
        style=config["style"],
        features=config["features"],
        tips=config["tips"]
    )
