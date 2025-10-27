"""
AI服务模块 - 支持OpenAI和DeepSeek
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import yaml

load_dotenv()


class AIService:
    """AI服务统一接口"""

    def __init__(self):
        # OpenAI客户端
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # DeepSeek客户端（使用OpenAI SDK，只需修改base_url）
        self.deepseek_client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        )

        # 加载提示词配置
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            self.prompts_config = yaml.safe_load(f)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        对话接口

        Args:
            messages: 对话历史 [{"role": "user", "content": "..."}]
            model: 使用的模型 ("openai" 或 "deepseek")
            temperature: 温度参数
            max_tokens: 最大令牌数

        Returns:
            AI回复内容
        """
        try:
            if model == "openai":
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif model == "deepseek":
                response = await self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",  # DeepSeek V3
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                raise ValueError(f"不支持的模型: {model}")

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"AI服务调用失败: {str(e)}")

    async def create_structure_suggestion(
        self,
        conversation_history: List[Dict[str, str]],
        model: str = "openai"
    ) -> Dict:
        """
        根据对话历史，建议内容结构

        Args:
            conversation_history: 对话历史
            model: 使用的模型

        Returns:
            结构建议 {"name": "...", "description": "...", "structure": {...}}
        """
        system_prompt = """你是一个内容结构设计专家。请根据用户的对话内容，总结并建议一个内容结构模板。

返回格式必须是JSON：
{
    "name": "模板名称",
    "description": "模板描述",
    "structure": {
        "sections": [
            {"name": "标题", "type": "title", "max_length": 30, "required": true, "placeholder": "请输入标题"},
            {"name": "开场钩子", "type": "hook", "max_length": 50, "required": true, "placeholder": "吸引读者的开场"},
            ...
        ]
    }
}

可用的section类型：
- title: 标题
- hook: 开场钩子
- content: 正文内容
- cta: 行动号召
- hashtags: 话题标签
- subtitle: 副标题
- summary: 摘要
- custom: 自定义
"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({
            "role": "user",
            "content": "请根据我们的对话，总结一个内容结构模板。直接返回JSON格式，不要有其他说明文字。"
        })

        response = await self.chat(messages, model=model, temperature=0.5)

        # 解析JSON
        import json
        try:
            # 尝试提取JSON部分
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            structure = json.loads(response.strip())
            return structure
        except:
            # 如果解析失败，返回一个默认结构
            return {
                "name": "基础内容结构",
                "description": "从对话中提取的结构",
                "structure": {
                    "sections": [
                        {"name": "标题", "type": "title", "max_length": 30, "required": True},
                        {"name": "正文", "type": "content", "max_length": 500, "required": True}
                    ]
                }
            }

    async def generate_content(
        self,
        hot_materials: List[Dict],
        structure: Dict,
        user_style: Optional[str] = None,
        model: str = "openai"
    ) -> Dict:
        """
        根据热点素材和结构生成内容

        Args:
            hot_materials: 热点素材列表
            structure: 内容结构
            user_style: 用户风格指南
            model: 使用的模型

        Returns:
            生成的内容
        """
        # 准备热点素材文本
        materials_text = "\n\n".join([
            f"【{m.get('platform', '未知平台')}】{m.get('title', '')}\n{m.get('content', '')}"
            for m in hot_materials
        ])

        # 准备结构说明
        sections = structure.get("structure", {}).get("sections", [])
        structure_text = "\n".join([
            f"- {s['name']}（类型：{s['type']}，"
            f"{'必填' if s.get('required') else '可选'}，"
            f"最大长度：{s.get('max_length', '不限')}字）"
            for s in sections
        ])

        # 构建提示词
        prompt = f"""请根据以下热点素材，创作一篇内容。

## 热点素材
{materials_text}

## 内容结构要求
{structure_text}

## 用户风格指南
{user_style if user_style else '自然、易读、有价值'}

## 输出要求
请按照结构要求，生成内容。返回JSON格式：
{{
    "section_name_1": "内容...",
    "section_name_2": "内容...",
    ...
}}

注意：
1. 内容要结合热点素材，但不要照抄
2. 遵循用户的风格指南
3. 每个部分的长度要符合要求
4. 内容要有价值，不要空洞
"""

        messages = [
            {"role": "system", "content": "你是一个专业的内容创作者，擅长将热点素材改写成高质量的内容。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.chat(messages, model=model, temperature=0.8, max_tokens=3000)

        # 解析JSON
        import json
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            content = json.loads(response.strip())
            return content
        except Exception as e:
            # 如果解析失败，返回原始响应
            return {"raw_content": response, "error": f"解析失败: {str(e)}"}

    async def adapt_to_platform(
        self,
        content: Dict,
        platform_config: Dict,
        model: str = "openai"
    ) -> str:
        """
        将内容适配到特定平台

        Args:
            content: 原始内容
            platform_config: 平台配置
            model: 使用的模型

        Returns:
            适配后的内容
        """
        content_text = "\n".join([f"{k}: {v}" for k, v in content.items()])

        prompt = f"""请将以下内容适配到{platform_config['name']}平台。

## 原始内容
{content_text}

## 平台要求
- 最大长度：{platform_config['max_length']}字
- 风格：{platform_config['style']}
- 特点：{', '.join(platform_config.get('features', []))}
- 建议：{platform_config.get('tips', '')}

请直接返回适配后的完整内容，不要有其他说明。
"""

        messages = [
            {"role": "system", "content": "你是一个多平台内容运营专家。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.chat(messages, model=model, temperature=0.7)
        return response.strip()


# 创建全局实例
ai_service = AIService()
