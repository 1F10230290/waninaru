from django import forms
from .models import Project, CraftTag, Reward
from django.forms.models import inlineformset_factory

# プロジェクト用フォーム
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'goal_amount', 'end_date', 'image', 'tags']
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'date'}),
            'tags': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'title': 'タイトル',
            'description': '説明',
            'goal_amount': '目標金額',
            'end_date': '終了日',
            'image': '画像',
            'tags': 'タグ'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = CraftTag.objects.filter(name__in=['有田焼', '江戸切子', '輪島塗'])

# リターン用フォーム
class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['title', 'description', 'amount', 'limit']
        labels = {
            'title': 'タイトル',
            'description': '説明',
            'amount': '値段',
            'limit': '個数',
        }

RewardFormSet = inlineformset_factory(
    Project,  # 親モデル（1）
    Reward,   # 子モデル（多）
    form=RewardForm,
    extra=1,          # 新規で表示する空フォームの数
    can_delete=True   # 既存のリターンを削除できるようにする
)

