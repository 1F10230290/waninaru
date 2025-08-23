from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Profile
import re

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        error_messages={
            'invalid': '正しいメールアドレスを入力してください。',
        }
    )

    password2 = forms.CharField(
        required=True,
        error_messages={
            'required': '確認用パスワードは必須です。'
        }
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if not password:
            raise forms.ValidationError("パスワードを入力してください。")
        # 条件チェック
        if len(password) < 10:
            raise forms.ValidationError("パスワードは10文字以上にしてください。")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("パスワードには大文字を含めてください。")
        if not any(c.islower() for c in password):
            raise forms.ValidationError("パスワードには小文字を含めてください。")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("パスワードには数字を含めてください。")

        return password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("正しいメールアドレスを入力してください。")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'icon', 'bio', 'role']
