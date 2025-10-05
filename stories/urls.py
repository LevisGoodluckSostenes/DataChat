from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('upload/', views.upload_story, name='upload_story'),
    path('<int:pk>/', views.story_detail, name='story_detail'),
    path('<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('reply/<int:reply_id>/edit/', views.edit_reply, name='edit_reply'),
]


