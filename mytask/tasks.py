from celery import shared_task
import time


@shared_task
def example_task(x, y):
    """示例任务，用于测试任务记录功能"""
    time.sleep(5)  # 模拟耗时操作
    return x + y


@shared_task
def failing_task():
    """一个会失败的任务，用于测试错误记录"""
    raise Exception("This is a test exception")