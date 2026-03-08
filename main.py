# import requests
# import time
# import json
# import os
# import sys
#
#
# COZE_API_TOKEN = os.getenv("COZE_API_TOKEN", "pat_96pr172pRUV5LAixB2SIYBtffCGLwfbr1bWDE7YBYTAcTLPrXHkGIsVN6AuVw0dm")  # 在这里填入您的API Token
# BOT_ID = os.getenv("COZE_BOT_ID", "7517472759602642944")
#
#
# CHAT_API_URL = "https://api.coze.cn/v3/chat"
# RETRIEVE_CHAT_URL = "https://api.coze.cn/v3/chat/retrieve"
# MESSAGE_LIST_URL = "https://api.coze.cn/v3/chat/message/list"
# FILE_UPLOAD_URL = "https://api.coze.cn/v1/files/upload"
#
# FILE_TO_UPLOAD_PATH = "E:\福软程序\测试\实验代码.docx" # 【请修改】要处理的Word文档路径
# MARKDOWN_OUTPUT_PATH = "E:\福软程序\测试\处理结果.md"   # 【请修改】希望保存Markdown文件的路径
# # --- 1. 定义文本读取函数 ---
# def upload_file_to_coze(file_path: str) -> str:
#     """
#     将文件上传到coze平台并返回 file_id
#     :param file_path:
#     :return:
#     """
#
#     if not os.path.exists(file_path):
#         print(f"错误：找不到文件，请检查路径：{file_path}")
#         return None
#
#     print(f"正在上传文件：{file_path}...")
#
#     headers = {
#         "Authorization":f"Bearer {COZE_API_TOKEN}",
#         "Content-Tpye":"multipart/form-data"
#     }
#     try:
#         with open(file_path,'rb') as f:
#             files = {"file":(os.path.basename(file_path),f)}
#             response = requests.post(FILE_UPLOAD_URL,headers = headers, files = files,timeout=60)
#             response.raise_for_status()
#             response_data = response.json()
#
#         if response_data.get('code') == 0:
#             file_id = response_data.get('data').get('id')
#             print(f'文件上传成功！File_id:{file_id}')
#             return file_id
#         else:
#             print(f"文件上传失败：{response_data.get('msg')}")
#             return None
#     except Exception as e:
#         print(f"上传文件时发生错误：{e}")
#         return None
#
# # --- 2. 定义轮询调用函数 ---
# def call_coze_bot_with_file(file_id: str, user_id: str) -> str:
#     """
#     使用file_id发起对话
#     """
#     if "YOUR_COZE_API_TOKEN" in COZE_API_TOKEN or "YOUR_BOT_ID" in BOT_ID:
#         return "错误：请先在脚本中设置您的 COZE_API_TOKEN 和 BOT_ID。"
#
#     headers = {
#         "Authorization": f"Bearer {COZE_API_TOKEN}",
#         "Content-Type": "application/json",
#     }
#
#     # --- 第一步：提交对话任务 ---
#     initial_payload = {
#         "bot_id": BOT_ID,
#         "user_id": user_id,
#         "stream": False,
#         "auto_save_history": True,
#         "additional_messages": [{"role": "user", "content": prompt, "content_type": "text"}]
#     }
#
#     try:
#         print("正在提交任务...")
#         initial_response = requests.post(CHAT_API_URL, headers=headers, json=initial_payload, timeout=30)
#         initial_response.raise_for_status()
#         initial_data = initial_response.json()
#
#         if initial_data.get('code') != 0:
#             return f"提交任务失败: {initial_data.get('msg')}"
#
#         chat_id = initial_data.get('data', {}).get('id')
#         conversation_id = initial_data.get('data',{}).get('conversation_id')
#         if not chat_id:
#             return f"未能获取 chat_id: {initial_data}"
#
#         print(f"任务已提交，本次聊天ID: {chat_id},本次会话ID:{conversation_id}")
#
#     except requests.exceptions.RequestException as e:
#         return f"提交初始请求时出错: {e}"
#
#     # --- 第二步：轮询任务状态，直到 'completed' ---
#     start_time = time.time()
#     timeout_seconds = 180
#
#     print("正在轮询任务状态...")
#     while time.time() - start_time < timeout_seconds:
#         try:
#             time.sleep(3)  # 等待几秒再查询
#
#             status_params = {'chat_id': chat_id,'conversation_id':conversation_id}
#             status_response = requests.get(RETRIEVE_CHAT_URL, headers=headers, params=status_params, timeout=30)
#             status_response.raise_for_status()
#             status_data = status_response.json()
#
#             if status_data.get('code') == 0:
#                 # 使用 .get() 并提供默认空字典 {} 来安全地访问嵌套数据
#                 status = status_data.get('data').get('status')
#
#                 if status == 'completed':
#                     print("对话已完成！")
#                     # --- 第三步：获取完整的消息列表 ---
#                     print("正在获取最终回复...")
#                     msg_list_params = {'chat_id': chat_id,'conversation_id':conversation_id}
#                     final_response = requests.get(MESSAGE_LIST_URL, headers=headers, params=msg_list_params, timeout=30)
#                     final_response.raise_for_status()
#                     final_data = final_response.json()
#
#                     if final_data.get('code') == 0:
#                         messages = final_data.get('data', [])
#                         for message in messages:
#                             if message.get('type') == 'answer':
#                                 return message.get('content', '')
#                         return "错误：在已完成的对话中未找到助手的回答。"
#                     else:
#                         return f"获取消息列表失败: {final_data.get('msg')}"
#
#                 elif status == 'failed':
#                     return f"错误：对话处理失败。服务器返回状态: failed。详情: {status_data}"
#
#             else:
#                 # 如果API本身返回错误码，则直接报告
#                 return f"查询状态时出错: {status_data.get('msg')}"
#
#         except requests.exceptions.RequestException as e:
#             print(f"轮询请求时出错: {e}")
#
#     return "错误：轮询超时（超过3分钟），任务仍未完成。"
#
#
# # --- 3. 主程序入口 ---
# if __name__ == "__main__":
#     unique_user_id = "terminal_user_polling_12345"
#
#     if len(sys.argv) > 1:
#         user_prompt = " ".join(sys.argv[1:])
#         print(f"您输入的问题是: {user_prompt}")
#     else:
#         try:
#             user_prompt = input("请输入您想对Bot说的话 (输入 'quit' 退出): ")
#         except (KeyboardInterrupt, EOFError):
#             print("\n再见！")
#             sys.exit(0)
#
#     if user_prompt.lower() == 'quit':
#         print("再见！")
#         sys.exit(0)
#
#     bot_response = call_coze_bot_with_polling(user_prompt, unique_user_id)
#
#     print("\n--- 智能体回复 ---\n")
#     print(bot_response)
#     print("\n-------------------\n")

import json
import os
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="规则审查服务")

# 定义存放规则的本地文件路径
RULES_FILE_PATH = "rules.json"


def load_rules_from_file():
    """
    辅助函数：负责打开并读取本地的 JSON 文件
    """
    # 1. 检查文件存不存在，防止报错卡死
    if not os.path.exists(RULES_FILE_PATH):
        print(f"警告：找不到文件 {RULES_FILE_PATH}")
        return {}

    # 2. 打开文件并解析 JSON。注意 encoding="utf-8" 必须加，否则中文会乱码
    with open(RULES_FILE_PATH, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("错误：JSON 文件格式不正确！")
            return {}


@app.get("/api/rules/{filename}")
async def get_rules(filename: str, category: Optional[str] = Query(None)):
    """
    根据文件名和可选的分类获取对应的审查规则
    """
    # 每次收到请求时，都去读取一次最新的本地文件
    # 这样你在测试时，修改了 rules.json 保存后，不用重启服务立马就能生效！
    rules_db = load_rules_from_file()

    # 处理传过来的文件名，比如去掉 ".txt" 后缀
    db_key = filename.split('.')[0]

    # 从读取到的字典中获取对应规则，没有就返回空列表
    rules = rules_db.get(db_key, [])

    # 如果客户端传了 category 参数，可以进一步过滤（如果你未来的规则里加了 category 字段的话）
    if category and rules:
        rules = [r for r in rules if r.get("category") == category]
    return rules