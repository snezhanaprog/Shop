from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('store/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_item/', views.add_item, name="add_item"),
    path('cart/add_item/', views.add_item, name="add_item"),
    path('store/<int:id>/', views.product_details, name="product_details"),
    path('comments/<int:id>/', views.comments, name="comments"),
    path('create-comment/<int:id>', views.create_comment, name="create-comment"),
    path('', views.face_page, name="face-page"),
    path('about/', views.about, name="about"),
    path('contacts/', views.contacts, name="contacts"),
    path('feedback/', views.feedback, name="feedback"),
    path('achievements/', views.achievements, name="achievements"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

