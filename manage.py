#!/usr/bin/env python
if __name__ == '__main__':
    from common.appenginepatch.aecmd import setup_env
    setup_env(manage_py_env=True)

    import settings
    from django.core.management import execute_manager
    execute_manager(settings)
