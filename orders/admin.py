from django.contrib import admin
from django.utils.html import format_html
from .models import AvailableDate, AvailableTime, Appointment


class AvailableTimeInline(admin.TabularInline):
    model = AvailableTime
    extra = 1
    fields = ('time', 'available_for_products_display')
    readonly_fields = ('available_for_products_display',)
    
    def available_for_products_display(self, obj):
        if obj.pk and obj.available_for_products.exists():
            return ", ".join([p.name for p in obj.available_for_products.all()])
        return "✅ Все услуги"
    available_for_products_display.short_description = 'Доступно для'


@admin.register(AvailableDate)
class AvailableDateAdmin(admin.ModelAdmin):
    inlines = [AvailableTimeInline]
    list_display = ('date', 'products_display', 'times_count')
    list_filter = ('date', 'specific_products', 'exclude_products')
    search_fields = ('date',)
    exclude = ('exclude_products',) 
    # filter_horizontal = ('specific_products', 'exclude_products')
    
    def products_display(self, obj):
        products = obj.specific_products.all()
        if not products:
            return "✅ Все услуги"
        return ", ".join([p.name for p in products[:3]])
    products_display.short_description = 'Доступно для'
    
    def excluded_products_display(self, obj):
        products = obj.exclude_products.all()
        if not products:
            return "-"
        return ", ".join([p.name for p in products[:2]])
    excluded_products_display.short_description = 'Исключено'
    
    def times_count(self, obj):
        return obj.available_times.count()
    times_count.short_description = 'Слотов'


@admin.register(AvailableTime)
class AvailableTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'time', 'available_for_products_display', 'bookings_count')
    list_filter = ('date__date',)
    search_fields = ('date__date',)
    filter_horizontal = ('available_for_products',)
    
    def available_for_products_display(self, obj):
        products = obj.available_for_products.all()
        if not products:
            return "✅ Все услуги"
        return ", ".join([p.name for p in products[:2]])
    available_for_products_display.short_description = 'Доступно для'
    
    def bookings_count(self, obj):
        count = obj.appointments.count()
        if count == 0:
            return format_html('<span style="color: green;">0 записей</span>')
        else:
            services = ", ".join([a.product.name for a in obj.appointments.all()])
            return format_html('<span style="color: orange;">{} запись(ей): {}</span>', count, services)
    bookings_count.short_description = 'Записи'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'product', 'date_display', 'time_display', 'created_at')
    list_filter = ('product', 'date__date', 'created_at')
    search_fields = ('name', 'phone', 'comment')
    readonly_fields = ('created_at',)
    filter_horizontal = ('colors',)
    date_hierarchy = 'created_at'
    
    def date_display(self, obj):
        return obj.date.date.strftime('%d.%m.%Y')
    date_display.short_description = 'Дата'
    
    def time_display(self, obj):
        return obj.time.time.strftime('%H:%M')
    time_display.short_description = 'Время'