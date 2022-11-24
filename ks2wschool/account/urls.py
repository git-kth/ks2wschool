from django.urls import path
from account import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name="activate"),
    path('<str:nickname>', views.profile, name='profile'),
    path('update/<str:nickname>', views.profile_update, name='profile_update'),
    path('delete/<str:nickname>', views.profile_delete, name='profile_delete'),
    path('follow/<str:nickname>/',views.follow,name='follow'),
    path('view_follow/<str:nickname>/',views.view_follow,name='view_follow'),
    # path('follower/<str:nickname>/',views.follower,name='follower'),
]