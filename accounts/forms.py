from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Profile, CraftsmanProfile
import re

# ユーザー登録フォーム (CustomUser用)
class SignUpForm(UserCreationForm):
    # メールアドレス
    email = forms.EmailField(
        error_messages={
            'invalid': '正しいメールアドレスを入力してください。',
        }
    )

    # パスワード
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
        error_messages={
            'required': 'パスワードは必須です。'
        }
    )

    # 確認用パスワード
    password2 = forms.CharField(
        required=True,
        label="確認用パスワード",
        widget=forms.PasswordInput,
        error_messages={
            'required': '確認用パスワードは必須です。'
        }
    )

    class Meta:
        model = CustomUser  # このフォームは CustomUser モデルを利用
        fields = ('email', 'password1', 'password2')  # フィールドとして使用する項目

    # パスワードのバリデーション
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if not password:
            raise forms.ValidationError("パスワードを入力してください。")

        # セキュリティ条件チェック
        if len(password) < 10:
            raise forms.ValidationError("パスワードは10文字以上にしてください。")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("パスワードには大文字を含めてください。")
        if not any(c.islower() for c in password):
            raise forms.ValidationError("パスワードには小文字を含めてください。")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("パスワードには数字を含めてください。")

        return password  # 問題なければそのまま返す

    # メールアドレスのバリデーション
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)  # Django 標準のバリデーションでチェック
            except ValidationError:
                raise forms.ValidationError("正しいメールアドレスを入力してください。")
        return email  # 問題なければそのまま返す


# プロフィール編集フォーム (Profileモデル用)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile  # このフォームは Profile モデルを利用
        fields = ['name', 'icon', 'bio', 'role']  # 編集可能なフィールド

# 工芸士情報登録フォーム
class CraftsmanProfileForm(forms.ModelForm):
    class Meta:
        model = CraftsmanProfile
        fields = ['specialty', 'experience_years', 'workshop_location', 'bio']