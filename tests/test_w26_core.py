import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from decimal import Decimal
from app.core.numparse import parse_number
from app.core.params import Params
from scripts.normalize_enum import MAP_GAS, MAP_ROOF


class TestParseNumber:
    def test_decimal(self):
        assert parse_number(Decimal("10800")) == 10800.0

    def test_range_mid(self):
        assert parse_number("1.13~1.19") == 1.16

    def test_fullwidth_tilde(self):
        assert parse_number("1.0～1.045") == 1.0225

    def test_none_and_garbage(self):
        assert parse_number(None) is None
        assert parse_number("无公开数据") is None


class TestParams:
    def test_to_number(self):
        assert Params._to_number("0.9") == 0.9
        assert Params._to_number("8") == 8
        assert Params._to_number("经验规则") == "经验规则"

    def test_unknown_param_raises(self):
        p = Params()
        with pytest.raises(AttributeError):
            p.不存在的参数

    def test_db_drives_value(self):
        """闭环断言: Params读到eta必须与库里param_dependencies一致"""
        import pymysql
        from app.config import settings
        conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
            password=settings.DB_PASSWORD, database=settings.DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT param_value FROM param_dependencies WHERE param_name='eta'")
            row = cur.fetchone()
        conn.close()
        assert row is not None, "param_dependencies缺eta行"
        assert Params().eta == float(row[0])


class TestEnumMaps:
    def test_gas_aliases(self):
        assert MAP_GAS["高瓦斯(400m3/min)"] == "高瓦斯"
        assert MAP_GAS["高瓦斯突出矿区"] == "突出"
        assert MAP_GAS["低瓦斯煤层涌出量大"] == "低瓦斯"

    def test_gas_honest_null(self):
        assert MAP_GAS["涌出量大"] is None  # 无法判高低,不许猜

    def test_roof_classes(self):
        assert MAP_ROOF["破碎"] == "1类-不稳定"
        assert MAP_ROOF["中等稳定"] == "2类-中等稳定"
        assert MAP_ROOF["坚硬"] == "4类-坚硬"

    def test_roof_wrong_dimension_null(self):
        assert MAP_ROOF["冲击"] is None
        assert MAP_ROOF["浅埋"] is None
