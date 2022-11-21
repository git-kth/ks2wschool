from django.urls import path, include
from blog import views

urlpatterns = [
    path('', views.index, name='index'),
]

# category
urlpatterns += [
    path('create_category/', views.create_category, name="create_category"),
    path('view_posts/<str:nickname>/<str:category_name>', views.view_posts, name="view_posts"),
    path('update_category/<str:nickname>/<str:category_name>',views.update_category,name="update_category"),
    path('delete_category/<str:nickname>/<str:category_name>',views.delete_category,name="delete_category"),
]

# post
urlpatterns += [
    path('post/<int:post_id>/', views.detail_post, name="detail_post"),
    path('create_post/', views.create_post, name="create_post"),
    path('update_post/<int:post_id>',views.update_post,name="update_post"),
    path('delete_post/<int:post_id>/', views.delete_post, name="delete_post"),
    path('post_vote/<int:post_id>', views.post_vote ,name="post_vote"),
]
# comment, reply
urlpatterns += [
    path('create_comment/', views.create_comment, name="create_comment"),
    path('update_comment/<int:comment_id>',views.update_comment,name="update_comment"),
    path('delete_comment/<int:comment_id>',views.delete_comment, name="delete_comment"),
    path('create_reply/', views.create_reply, name="create_reply"),
    path('delete_reply/<int:reply_id>',views.delete_reply,name="delete_reply"),
]

