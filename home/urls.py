from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # reference
    path("reference/" , views.reference_view , name="reference"),
    path("reference/update/<int:pk>/", views.update_reference, name="update_reference"),
    path("reference/delete/<int:pk>/", views.delete_reference, name="delete_reference"),
    # shoe models
    path("shoe_model/create" , views.shoe_model_create , name="shoe_model_create"),
    path("shoe_model/read/<int:pk>" , views.shoe_model_read , name="shoe_model_read"),
    path("shoe_model/update/<int:pk>" , views.shoe_model_update , name="shoe_model_update"),
    path("shoe_model/delete/<int:pk>" , views.shoe_model_delete , name="shoe_model_delete"),
    
    # staff
    path("staff" , views.staff_view ,  name="staff_view"),
    path("staff/create" , views.staff_create , name="staff_create"),
    path("staff/update/<int:pk>" , views.staff_update , name="staff_update"),
    path("staff/delete/<int:pk>" , views.staff_delete , name="staff_delete"),
    
    # clients
    path('clients' , views.clients_view , name="clients_view"),
    path('clients/create' , views.clients_create, name="clients_create"),
    path('clients/update/<int:pk>' , views.clients_update , name="clients_update"),
    path('clients/delete/<int:pk>' , views.clients_delete , name="clients_delete"),
    
    # ordars
    path("orders" , views.orders_view , name="orders_view"),
    path("orders/create" , views.orders_create , name="orders_create"),
    path("orders/read/<int:pk>" ,views.order_read , name="order_read"),
    path('orders/update/<int:pk>' , views.orders_update , name="orders_update"),
    path('orders/delete/<int:pk>' , views.orders_delete , name="orders_delete"),
    
    # producement
    path('producement' , views.producement_view , name="producement_view"),
    path('producement/create' , views.producement_create , name='producement_create'),
    path('producement/read/<int:pk>' , views.producement_read , name='producement_read'),
    path('producement/update/<int:pk>' , views.producement_update , name="producement_update"),
    path('producement/delete/<int:pk>', views.producement_delete , name="producement_delete")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

