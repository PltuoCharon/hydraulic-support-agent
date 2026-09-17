from pathlib import Path


def read(path):
    return Path(path).read_text(
        encoding="utf-8"
    )


def test_agent_runtime_reuses_existing_chat_capabilities():
    s = read(
        "web/src/composables/useEngineeringAgent.js"
    )

    assert "streamChat" in s
    assert "postMatch" in s
    assert "AbortController" in s
    assert "marked" in s

    assert "confirm_pending" not in s

    assert "sending = ref(false)" in s
    assert "session_id: store.sessionId" in s


def test_agent_conversation_keeps_selection_workflow():
    s = read(
        "web/src/components/AgentConversation.vue"
    )

    assert "confirm_pending" in s
    assert "推荐结果" in s
    assert "查看推荐结果" in s
    assert "停止" in s
    assert "清空" in s


def test_agent_dock_is_global_and_context_aware():
    shell = read(
        "web/src/layouts/AppShell.vue"
    )

    dock = read(
        "web/src/components/AgentDock.vue"
    )

    assert "AgentDock" in shell
    assert "agentContextLabel" in shell
    assert "route.query.m" in shell

    assert "液压支架助手" in dock
    assert "当前能力：工况问答与选型" in dock
    assert "最小化" in dock
    assert "关闭" in dock


def test_chat_view_no_longer_duplicates_stream_logic():
    s = read(
        "web/src/views/ChatView.vue"
    )

    assert "AgentConversation" in s

    assert "streamChat" not in s
    assert "postMatch" not in s
    assert "AbortController" not in s
    assert "marked" not in s


def test_legacy_chat_route_is_preserved():
    s = read(
        "web/src/router/index.js"
    )

    assert "path: '/chat'" in s
    assert (
        "redirect: '/select?tab=chat'"
        in s
    )
