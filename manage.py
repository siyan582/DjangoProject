#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    # 注意：这里的 'DjangoProject' 必须和你文件夹里的 settings 所在文件夹名字一致
    # 你的项目叫 DjangoProject，所以这里是对的
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()