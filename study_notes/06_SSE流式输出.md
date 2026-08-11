# 06 SSE 流式输出

## 概念
Server-Sent Events：HTTP 长连接上服务端持续推送文本帧的协议。
帧格式 `data: {...}\\n\\n`，`text/event-stream` 媒体类型。
对比 WebSocket：单向、基于 HTTP、浏览器原生 EventSource 支持，
对话打字机效果用它足够。

## 本项目用法（W17 / W20-D1）
- 端点：`POST /api/chat/` 带 `stream=true` 返回 StreamingResponse；
- 帧序列：若干 `{"chunk": "..."}` 内容帧 →
  一帧元数据（session_id/stage）→ `data: [DONE]` 结束帧；
- 错误帧：`[ERROR]` 标记，前端区分渲染；
- 换心后（W20-D1）：状态机先完整跑完一轮，回复按 4 字符切片推送——
  引导式对话的回复短，伪流式的体验与真流式无差别，
  且保证落库的是完整文本。

## 踩坑
1. **curl 验证要加 -N**：不加会缓冲，看不到逐帧效果；
2. **uvicorn 后台启动慢**：sleep<5 时 curl 打在未就绪端口上，
   报错信息（JSONDecodeError）极具误导性；
3. **[DONE] 约定俗成**：OpenAI 风格结束标记，前端按此判断流终止，
   不要用空帧代替；
4. **中文按字符切不按字节切**：Python 字符串切片天然按字符，
   json.dumps(ensure_ascii=False) 保证中文不转义、帧可读。
