from django.db import models
from django.utils import timezone


class TaskRecord(models.Model):
    """
    记录Celery任务执行情况的模型
    """
    task_id = models.CharField(max_length=255, unique=True, verbose_name='任务ID')
    task_name = models.CharField(max_length=255, verbose_name='任务名称')
    status = models.CharField(max_length=50, default='PENDING', verbose_name='任务状态')
    result = models.TextField(blank=True, null=True, verbose_name='任务结果')
    args = models.TextField(blank=True, null=True, verbose_name='任务参数')
    kwargs = models.TextField(blank=True, null=True, verbose_name='任务关键字参数')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    traceback = models.TextField(blank=True, null=True, verbose_name='错误追踪信息')
    
    class Meta:
        verbose_name = '任务记录'
        verbose_name_plural = '任务记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task_name} - {self.task_id}'