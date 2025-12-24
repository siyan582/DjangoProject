import os
import django
from django.db import connection

# 1. 这里的 DjangoProject.settings 改成你自己项目的名字
# 如果你的文件夹叫 DjangoProject，那就不用改
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()


def reset_database():
    print("正在连接 MySQL 数据库并准备清空所有表...")
    try:
        with connection.cursor() as cursor:
            # 关闭外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # 获取所有表
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            if not tables:
                print("数据库已经是空的，无需操作。")
            else:
                for table in tables:
                    table_name = table[0]
                    print(f"正在删除表: {table_name}")
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

            # 恢复外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        print("-" * 30)
        print("✅ 数据库已成功清空！")
        print("请继续在 Terminal 运行: python manage.py migrate")

    except Exception as e:
        print(f"❌ 出错啦: {e}")
        print("请检查你的数据库是否启动，或者密码是否正确。")


if __name__ == '__main__':
    reset_database()