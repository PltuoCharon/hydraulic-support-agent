import os
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 直接设置密钥（确保是纯 ASCII）
API_KEY = "ec24f88d070a4042b82d0e457bd4249e.VDfxzQukrp4r7DvZ"  # 替换为实际密钥

llm = ChatOpenAI(
    api_key=API_KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    model="glm-4-flash",
    temperature=0
)

# ---------- 第 1 步链：工况描述 → 结构化参数 ----------
class Condition(BaseModel):
    mining_height: float = Field(description="采高，米")
    roof: str = Field(description="顶板条件：破碎/中等稳定/稳定/坚硬")
    dip_angle: float = Field(description="煤层倾角，度，未知填0")

parser = JsonOutputParser(pydantic_object=Condition)
prompt1 = PromptTemplate(
    template="从工况描述中提取参数，未提及的数值填0。\n{format_instructions}\n\n描述：{text}\n",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()})
chain1 = prompt1 | llm | parser

# ---------- 中间：Python 查库（Excel）筛选候选架型 ----------
def select_supports(cond):
    df = pd.read_excel("data/支架型号.xlsx")
    M = cond["mining_height"]
    cand = df[(df.height_min <= 0.9 * M) & (df.height_max >= 1.1 * M)]
    if cond["roof"] in ("破碎",):
        cand = cand[cand.type.str.contains("掩护")]
    elif cond["roof"] in ("稳定", "坚硬"):
        cand = cand[cand.type.str.contains("支撑|掩护")]
    return cand.sort_values("resistance", ascending=False).head(3)

# ---------- 第 2 步链：参数+候选 → 架型建议 ----------
prompt2 = PromptTemplate(
    template="你是液压支架选型专家。工况：采高{mining_height}m，顶板{roof}，倾角{dip_angle}°。"
             "候选架型：{candidates}。请给出推荐型号及2-3条理由（支护强度匹配、架型适应性、高度余量）。",
    input_variables=["mining_height", "roof", "dip_angle", "candidates"])
chain2 = prompt2 | llm

# ---------- 跑通 ----------
text = "某矿工作面采高3.0m，直接顶破碎，煤层倾角6°，低瓦斯。"
try:
    cond = chain1.invoke({"text": text})
    print("提取结果：", cond)
    
    cand = select_supports(cond)
    cand_str = cand[["model", "type", "resistance"]].to_string(index=False)
    print("候选架型：\n", cand_str)
    
    answer = chain2.invoke({**cond, "candidates": cand_str})
    print("架型建议：\n", answer.content)
except Exception as e:
    print(f"错误: {e}")
    print(f"密钥类型: {type(API_KEY)}")
    print(f"密钥长度: {len(API_KEY)}")
    print(f"密钥前20位: {repr(API_KEY[:20])}")
