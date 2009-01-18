#!/usr/bin/env python
if __name__ == '__main__':
    from common.appenginepatch.aecmd import setup_env
    setup_env(manage_py_env=True)

    # Recompile translation files
    from mediautils.compilemessages import updatemessages
    updatemessages()

    # Regenerate media files
    import sys
    from mediautils.generatemedia import updatemedia, generatemedia
    if len(sys.argv) < 2 or sys.argv[1] not in ('generatemedia', 'update'):
        updatemedia()

    # Generate compressed media files for manage.py update
    if len(sys.argv) >= 2 and sys.argv[1] == 'update':
        generatemedia(True)

    import settings
    from django.core.management import execute_manager
    try:
        execute_manager(settings)
    finally:
        # Regenerate uncompressed media files after manage.py update
        import sys
        from mediautils.generatemedia import generatemedia
        if len(sys.argv) >= 2 and sys.argv[1] == 'update':
            print 'Regenerating uncompressed media'
            generatemedia(False, silent=True)
