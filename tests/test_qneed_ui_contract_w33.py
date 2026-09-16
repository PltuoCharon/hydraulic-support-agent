"""W33-D6：QNeed 前后端语义/范围静态守门。

目的：
防止 Vue 输入范围再次小于计算内核有效范围，
以及物理参数中文标签再次错位。
"""

from pathlib import Path


VUE = Path("web/src/views/QNeedView.vue").read_text(encoding="utf-8")


def test_qneed_ui_physical_labels():
    assert '老顶初次来压步距 L1' in VUE
    assert '基本顶周期来压步距 Lp' in VUE
    assert '控顶宽度 Bc' in VUE
    assert '直接顶充填系数 N' in VUE

    # 已确认的错误叫法不得回来
    assert '支架中心距 Bc' not in VUE
    assert '动载系数 N' not in VUE


def test_qneed_ui_range_covers_backend_domain():
    assert 'v-model="form.l1" :min="5" :max="100"' in VUE
    assert 'v-model="form.lp" :min="3" :max="60"' in VUE
    assert 'v-model="form.bc" :min="1" :max="15"' in VUE
    assert 'v-model="form.n" :min="0.2" :max="5"' in VUE
