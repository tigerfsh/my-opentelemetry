from django.contrib import admin
from .models import TaskRecord


@admin.register(TaskRecord)
class TaskRecordAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'task_id', 'status', 'created_at', 'started_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('task_id', 'task_name')
    readonly_fields = ('task_id', 'task_name', 'status', 'result', 'args', 'kwargs', 'created_at', 'started_at', 'completed_at', 'traceback')
    ordering = ('-created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        # 所有字段都是只读的，防止意外修改任务记录
        return self.readonly_fields