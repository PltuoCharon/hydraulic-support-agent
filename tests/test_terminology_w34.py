"""W34-D1 专业术语静态守门。"""

from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8")


def test_modify_view_coal_thickness_not_labeled_mining_height():
    s = read("web/src/views/ModifyView.vue")

    assert (
        'label="煤层厚度">{{ store.conditions?.coal_thickness }} m'
        in s
    )

    assert (
        'label="工况采高">{{ store.conditions?.coal_thickness }} m'
        not in s
    )


def test_qneed_terms_remain_canonical():
    s = read("web/src/views/QNeedView.vue")

    assert "老顶初次来压步距 L1" in s
    assert "基本顶周期来压步距 Lp" in s
    assert "控顶宽度 Bc" in s
    assert "直接顶充填系数 N" in s

    assert "支架中心距 Bc" not in s
    assert "动载系数 N" not in s


def test_match_feature_coal_thickness_label():
    s = read("app/services/match_features.py")

    assert '"coal_thickness": ("coal_thickness", None, "煤层厚度/m")' in s
    assert '"coal_thickness": ("coal_thickness", None, "采高/m")' not in s
