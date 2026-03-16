from django.db import models
import uuid

class Ticket(models.Model):
    # Уникален код на билета. Ползваме UUID за сигурност, за да не се налучкват кодовете
    code = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    # За какво събитие/артикул е този билет (по желание)
    event_name = models.CharField(max_length=200, default="General Event")
    # Статус дали е използван
    is_used = models.BooleanField(default=False)
    # Кога е създаден и кога е използван
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Билет: {self.code} - Използван: {self.is_used}"


class ScanLog(models.Model):
    # Записваме всяко сканиране (дори и неуспешно) за историята
    scanned_text = models.CharField(max_length=500, null=True, blank=True)
    is_successful = models.BooleanField(default=False)
    message = models.CharField(max_length=250, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Скан: {self.scanned_text} - Успех: {self.is_successful} ({self.scanned_at.strftime('%Y-%m-%d %H:%M')})"