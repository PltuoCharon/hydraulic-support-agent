"""ORM 测试脚本"""

import sys
sys.path.insert(0, '.')

from core.db import SessionLocal, SupportModel, MiningArea, Stent


def test_support_model():
    """测试 SupportModel"""
    with SessionLocal() as session:
        # 1. 基本查询
        count = session.query(SupportModel).count()
        print(f"✓ 支架总数: {count}")
        assert count > 0, "支架表为空"
        
        # 2. 按采高查询
        results = SupportModel.find_by_height(session, 2.0, 4.0)
        print(f"✓ 采高 2.0-4.0m: {len(results)} 条")
        
        # 3. 按阻力查询
        results = SupportModel.find_by_resistance(session, 10000)
        print(f"✓ 阻力 ≥10000kN: {len(results)} 条")
        
        # 4. 按类型查询
        results = SupportModel.find_by_type(session, "掩护")
        print(f"✓ 掩护式: {len(results)} 条")
        
        # 5. 兼容性测试（Stent 别名）
        results = Stent.find_by_height(session, 2.0, 4.0)
        print(f"✓ Stent 别名: {len(results)} 条")


def test_mining_area():
    """测试 MiningArea"""
    with SessionLocal() as session:
        # 1. 基本查询
        count = session.query(MiningArea).count()
        print(f"✓ 矿区总数: {count}")
        
        # 2. 训练集/盲测集
        train = MiningArea.get_train_set(session)
        test = MiningArea.get_test_set(session)
        print(f"✓ 训练集: {len(train)} 条")
        print(f"✓ 盲测集: {len(test)} 条")
        assert len(test) == 5, "盲测集应为 5 条"


def main():
    print("=" * 50)
    print("ORM 测试")
    print("=" * 50)
    
    try:
        test_support_model()
        test_mining_area()
        print("\n" + "=" * 50)
        print("✅ 所有测试通过")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
