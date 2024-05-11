from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('store/', views.StoreView.as_view(), name='store'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.Checkout.as_view(), name='checkout'),
    path('add_item/', views.add_item, name="add_item"),
    path('cart/add_item/', views.add_item, name="add_item"),
    path('store/<int:id>/', views.ProductDetail.as_view(), name="product_details"),
    path('comments/<int:id>/', views.ProductCommentsView.as_view(), name="comments"),
    path('create-comment/<int:id>', views.CreateCommentView.as_view(), name="create-comment"),
    path('', views.FacePageView.as_view(), name="face-page"),
    path('about/', views.AboutView.as_view(), name="about"),
    path('contacts/', views.ContactsView.as_view(), name="contacts"),
    path('feedback/', views.FeedbackView.as_view(), name="feedback"),
    path('achievements/', views.Achievements.as_view(), name="achievements"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

