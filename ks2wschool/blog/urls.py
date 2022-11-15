from django.urls import path, include
from blog import views

urlpatterns = [
    path('', views.index, name='index'),
]

# category
urlpatterns += [
    path('create_category/', views.create_category, name="create_category"),
    path('view_posts/<str:nickname>/<str:category_name>', views.view_posts, name="view_posts"),
    
]

# post
urlpatterns += [
    path('post/<int:post_id>/', views.detail_post, name="detail_post"),
    path('create_post/', views.create_post, name="create_post"),
]

# comment, reply
urlpatterns += [
    path('create_comment/', views.create_comment, name="create_comment"),
    path('create_reply/', views.create_reply, name="create_reply"),
]

