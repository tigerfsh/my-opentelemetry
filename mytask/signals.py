import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from celery.signals import task_prerun, task_postrun, task_failure
from .models import TaskRecord
from django.utils import timezone


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """
    Celery任务开始执行前的处理函数
    """
    # 检查任务记录是否已存在，如果不存在则创建
    task_record, created = TaskRecord.objects.get_or_create(
        task_id=task_id,
        defaults={
            'task_name': task.name,
            'status': 'STARTED',
            'args': json.dumps(list(args)) if args else None,
            'kwargs': json.dumps(kwargs) if kwargs else None,
            'started_at': timezone.now()
        }
    )
    
    if not created:
        # 如果记录已存在，更新状态和开始时间
        task_record.status = 'STARTED'
        task_record.started_at = timezone.now()
        task_record.task_name = task.name
        task_record.save()


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """
    Celery任务执行后的处理函数
    """
    try:
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_record.status = state
        task_record.result = json.dumps(retval) if retval is not None else None
        task_record.completed_at = timezone.now()
        task_record.save()
    except TaskRecord.DoesNotExist:
        # 如果任务记录不存在，则创建一个新的记录
        TaskRecord.objects.create(
            task_id=task_id,
            task_name=task.name,
            status=state,
            result=json.dumps(retval) if retval is not None else None,
            args=json.dumps(list(args)) if args else None,
            kwargs=json.dumps(kwargs) if kwargs else None,
            completed_at=timezone.now()
        )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """
    Celery任务执行失败时的处理函数
    """
    try:
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_record.status = 'FAILURE'
        task_record.result = str(exception)
        task_record.traceback = str(einfo)
        task_record.completed_at = timezone.now()
        task_record.save()
    except TaskRecord.DoesNotExist:
        # 如果任务记录不存在，则创建一个新的记录
        TaskRecord.objects.create(
            task_id=task_id,
            task_name=getattr(sender, 'name', 'Unknown'),
            status='FAILURE',
            result=str(exception),
            traceback=str(einfo),
            completed_at=timezone.now()
        )