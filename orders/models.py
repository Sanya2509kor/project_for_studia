from django.db import models
from django.conf import settings
from django.core.cache import cache
from main.models import Color, Product


class AvailableDate(models.Model):
    date = models.DateField(verbose_name='Дата', db_index=True)
    
    specific_products = models.ManyToManyField(
        Product, 
        verbose_name='Выберите для каких услуг',
        blank=True,
        help_text='<span style="color: #28a745; font-weight: bold;">✅ Если не выбрано - дата доступна для всех услуг</span><br><br>'
    )
    
    exclude_products = models.ManyToManyField(
        Product,
        verbose_name='Исключить для этих услуг',
        blank=True,
        related_name='excluded_dates',
        help_text='Эти услуги НЕ будут видеть эту дату'
    )
    
    class Meta:
        verbose_name = 'Дата'
        verbose_name_plural = 'Даты'
        ordering = ['date']
        indexes = [models.Index(fields=['date'])]
    
    def __str__(self):
        return str(self.date)
    
    def is_available_for_product(self, product):
        """Проверяет, доступна ли дата для конкретной услуги"""
        # Если есть список конкретных услуг
        if self.specific_products.exists():
            if product not in self.specific_products.all():
                return False
        
        # Если услуга в списке исключений
        if product in self.exclude_products.all():
            return False
        
        # Проверяем, есть ли хотя бы одно доступное время для этой услуги
        for time_slot in self.available_times.all():
            if time_slot.is_available_for_product(product):
                return True
        
        return False


class AvailableTime(models.Model):
    """Время с возможностью привязки к услугам"""
    date = models.ForeignKey(
        AvailableDate, 
        on_delete=models.CASCADE, 
        related_name='available_times', 
        verbose_name='Дата'
    )
    time = models.TimeField(verbose_name='Время')
    
    # Какие услуги могут использовать это время (пусто = все услуги)
    available_for_products = models.ManyToManyField(
        Product,
        verbose_name='Доступно для услуг',
        blank=True,
        help_text='Если не выбрано - время доступно для всех услуг'
    )
    
    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'
        unique_together = ('date', 'time')
        ordering = ['time']
        indexes = [
            models.Index(fields=['date', 'time']),
        ]
    
    def __str__(self):
        return f"{self.time.strftime('%H:%M')}"
    
    def is_available_for_product(self, product):
        """Проверяет, доступно ли время для конкретной услуги"""
        # Проверяем, разрешено ли это время для данной услуги
        if self.available_for_products.exists():
            if product not in self.available_for_products.all():
                return False
        
        # Проверяем, есть ли уже запись на ЭТУ ЖЕ услугу в это время
        existing_appointment = Appointment.objects.filter(
            date=self.date,
            time=self,
            product=product
        ).exists()
        
        return not existing_appointment


class Appointment(models.Model):
    """Запись на услугу"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        verbose_name='Пользователь',
        null=True, 
        blank=True, 
        related_name='appointments'
    )
    name = models.CharField('Имя', max_length=100, db_index=True)
    phone = models.CharField('Телефон', max_length=12, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Услуга')
    colors = models.ManyToManyField(Color, verbose_name='Выбранные цвета', blank=True)
    date = models.ForeignKey(AvailableDate, on_delete=models.CASCADE, verbose_name='Дата')
    time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE, verbose_name='Время', related_name='appointments')
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)

    reminder_2h_sent = models.BooleanField(default=False, verbose_name='Напоминание за 2 часа')
    day_reminder_sent = models.BooleanField(default=False, verbose_name='Дневное напоминание')
    
    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('-created_at',)
        # Убираем unique_together, так как разные услуги могут быть в одно время
        indexes = [
            models.Index(fields=['date', 'time', 'product']),  # Индекс для быстрой проверки
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['phone']),
            models.Index(fields=['product', 'date']),
        ]
    
    def __str__(self):
        return f'Запись #{self.id} - {self.product.name} - {self.name}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'appointment_{self.id}')
        cache.delete('appointments_list')