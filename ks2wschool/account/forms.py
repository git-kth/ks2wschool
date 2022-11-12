from django import forms
from account.models import User


import datetime

class CreateUserForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='password confirmation', widget=forms.PasswordInput)
    birth_date = forms.DateField(label='birth_date', widget=forms.DateInput(attrs={
        'type': 'date',
        'max': datetime.date.today(),
        'value': datetime.date.today(),
    }))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if birth_date >= datetime.date.today():
            raise forms.ValidationError("생일 날짜를 확인해주세요.")
        return birth_date

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        PASSWORD_LENGTH = 8
        if len(password1) < PASSWORD_LENGTH:
            raise forms.ValidationError("비밀번호 길이는 최소 8개입니다.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
    class Meta:
        model = User
        fields = ("email", "nickname", "password1", "password2", "name", "birth_date")


class UpdateUserForm(forms.ModelForm):
    birth_date = forms.DateField(label='birth_date', widget=forms.DateInput(attrs={
        'type': 'date',
        'max': datetime.date.today(),
        'value': datetime.date.today(),
    }))
    short_info = forms.CharField(label='short_info', required=False, widget=forms.Textarea(attrs={
        'resize': None,
    }))
    
    class Meta:
        model= User
        fields = ("name", "birth_date", "short_info", "profile_image")
        
    

class LoginUserForm(forms.Form):
    email = forms.EmailField(
        label='email', 
        error_messages={'required': '이메일을 입력해주세요'},
        widget=forms.EmailInput
    )

    password = forms.CharField(
        label='password', 
        error_messages={'required': '비밀번호를 입력해주세요'},
        widget=forms.PasswordInput
    )
    
    def clean(self):                                           
        cleaned_data = super().clean()
        username = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if username and password :
            try:
                user = User.objects.get(email=username)
                if not user.check_password(password):
                    self.add_error('password', '비밀번호를 틀렸습니다.')     
                else:
                    self.user_id = user.id                                 
            except Exception:
                self.add_error('email', '존재하지 않는 이메일입니다.')

