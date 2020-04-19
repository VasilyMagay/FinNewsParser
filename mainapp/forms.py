"""
mainapp/forms.py
"""
import django.forms as forms
from mainapp.models import Topic, TopicSite


class TopicEditForm(forms.ModelForm):
    class Meta:
        model = Topic
        # fields = '__all__'
        exclude = ('user',)  # Чтобы вывести поле discount

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # field.help_text = ''


class TopicSiteEditForm(forms.ModelForm):
    class Meta:
        model = TopicSite
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
