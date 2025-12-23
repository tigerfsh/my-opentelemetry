try:
    from celery.app import shared_task
    print('shared_task from celery.app import successful')
except ImportError as e:
    print(f'Import error from celery.app: {e}')

try:
    from celery import shared_task
    print('shared_task from celery import successful')
except ImportError as e:
    print(f'Import error from celery: {e}')

