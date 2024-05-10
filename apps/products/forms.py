from django import forms
from .models import ProductsModel, Category, Colors

class ProductForm(forms.ModelForm):
    category_input = forms.ModelChoiceField(queryset=Category.objects.all())
    color_input = forms.ModelMultipleChoiceField(queryset=Colors.objects.all(),to_field_name='name')
    class Meta:
        model = ProductsModel
        fields = '__all__'
        exclude = ['slug','category','color']  # Exclude slug field

    def clean_category_input(self):
        category = self.cleaned_data.get('category_input')
        if not category:
            raise forms.ValidationError("Please select a category.")
        return category
    def clean_color_input(self):
        color = self.cleaned_data.get('color_input')
        if not color:
            raise forms.ValidationError("Please select a color.")
        return color

    def save(self, commit=True):
        product = super().save(commit=False)
        product.category = self.cleaned_data['category_input']
        product.color = self.cleaned_data['color_input']
        if commit:
            product.save()
            self.save_m2m()
        return product