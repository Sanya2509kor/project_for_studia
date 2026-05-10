from django import forms
from django.core.cache import cache
from main.models import Color, Product
from .models import AvailableDate, AvailableTime, Appointment
from django.utils import timezone


class AppointmentForm(forms.ModelForm):
    colors = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Можете написать свои пожелания',
            'class': 'form-control',
            'rows': 3
        }),
        required=False,
        label='Комментарий'
    )
    
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'name', 'phone', 'product', 'colors', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 999-99-99'}),
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'id_product'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Получаем выбранный продукт
        selected_product_id = None
        if self.data.get('product'):
            try:
                selected_product_id = int(self.data.get('product'))
            except (ValueError, TypeError):
                pass
        elif self.initial.get('product'):
            try:
                selected_product_id = int(self.initial.get('product'))
            except (ValueError, TypeError):
                pass
        
        current_date = timezone.localtime(timezone.now()).date()
        
        # Фильтруем даты по доступности для услуги
        if selected_product_id:
            try:
                product = Product.objects.get(id=selected_product_id)
                available_dates = []
                for date_obj in AvailableDate.objects.filter(date__gte=current_date).order_by('date'):
                    if date_obj.is_available_for_product(product):
                        available_dates.append(date_obj.id)
                
                self.fields['date'].queryset = AvailableDate.objects.filter(
                    id__in=available_dates
                ).order_by('date')
            except Product.DoesNotExist:
                self.fields['date'].queryset = AvailableDate.objects.filter(
                    date__gte=current_date
                ).order_by('date')
        else:
            self.fields['date'].queryset = AvailableDate.objects.filter(
                date__gte=current_date
            ).order_by('date')
        
        # Инициализируем пустой queryset для времени
        self.fields['time'].queryset = AvailableTime.objects.none()
        
        # Если дата и продукт выбраны, загружаем доступное время
        if selected_product_id and self.data.get('date'):
            try:
                product = Product.objects.get(id=selected_product_id)
                date_id = int(self.data.get('date'))
                date_obj = AvailableDate.objects.get(id=date_id)
                
                available_times = []
                for time_slot in date_obj.available_times.order_by('time'):
                    if time_slot.is_available_for_product(product):
                        available_times.append(time_slot.id)
                
                self.fields['time'].queryset = AvailableTime.objects.filter(
                    id__in=available_times
                ).order_by('time')
            except (Product.DoesNotExist, AvailableDate.DoesNotExist, ValueError, TypeError):
                pass
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        cleaned = phone.replace('+', '').replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
        if len(cleaned) not in [11, 12]:
            raise forms.ValidationError('Введите корректный номер телефона')
        return cleaned
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        date_obj = cleaned_data.get('date')
        time_slot = cleaned_data.get('time')
        
        if product and time_slot and not time_slot.is_available_for_product(product):
            self.add_error('time', 'Это время уже занято для выбранной услуги')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance