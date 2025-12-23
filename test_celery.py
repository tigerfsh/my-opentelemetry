try:
    from celery import shared_task
    print('shared_task import successful')
except ImportError as e:
    print(f'Import error: {e}')
    
try:
    from celery import Celery
    print('Celery import successful')
except ImportError as e:
    print(f'Import error: {e}')

