from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .forms import (
    ProducementKroyForms,
    ProducementLazirForms,
    ProducementZakatopForms,
    ProducementTuquvchiForms,
    ProducementKosibForms,
    ProducementUpakovkachiForms,
)

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
    path("staff/read/<int:pk>", views.staff_read, name="staff_read"),
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
    # path('producement/create' , views.producement_create , name='producement_create'),
    path('producement/create/kroy' , lambda request: views.producement_create(request, ProducementKroyForms), name='producement_create_kroy'),
    path('producement/create/lazir' , lambda request: views.producement_create(request, ProducementLazirForms), name='producement_create_lazir'),
    path('producement/create/zakatop' , lambda request: views.producement_create(request, ProducementZakatopForms), name='producement_create_zakatop'),
    path('producement/create/tuquvchi' , lambda request: views.producement_create(request, ProducementTuquvchiForms), name='producement_create_tuquvchi'),
    path('producement/create/kosib' , lambda request: views.producement_create(request, ProducementKosibForms), name='producement_create_kosib'),
    path('producement/create/upakovkachi' , lambda request: views.producement_create(request, ProducementUpakovkachiForms), name='producement_create_upakovkachi'),

    path('producement/read/<int:pk>' , views.producement_read , name='producement_read'),
    path('producement/update/<int:pk>' , views.producement_update , name="producement_update"),
    
    path('producement/update/kroy/<int:pk>', lambda request, pk: views.producement_update(request, pk, ProducementKroyForms), name='producement_update_kroy'),
    path('producement/update/lazir/<int:pk>', lambda request, pk: views.producement_update(request, pk, ProducementLazirForms), name='producement_update_lazir'),
    path('producement/update/zakatop/<int:pk>', lambda request, pk: views.producement_update(request, pk, ProducementZakatopForms), name='producement_update_zakatop'),
    path('producement/update/tuquvchi/<int:pk>', lambda request, pk: views.producement_update(request, pk, ProducementTuquvchiForms), name='producement_update_tuquvchi'),
    path('producement/update/kosib/<int:pk>', lambda request, pk: views.producement_update(request, pk, ProducementKosibForms), name='producement_update_kosib'),
    path('producement/update/upakovkachi/<int:pk>', lambda request, pk: views.producement_update(request, pk, ProducementUpakovkachiForms), name='producement_update_upakovkachi'),

    path('producement/delete/<int:pk>', views.producement_delete , name="producement_delete"),
    
    # staff_payment
    path("staff_payment/create", views.staff_payment_create, name="staff_payment_create"),
    path("staff_payment_read/create/<int:pk>", views.staff_payment_read_create, name="staff_payment_read_create"),
    path("staff_payment/update/<int:pk>", views.staff_payment_update, name="staff_payment_update"),
    path("staff_payment/delete/<int:pk>", views.staff_payment_delete, name="staff_payment_delete"),

    # Sale
    path('Sale/', views.sales_view, name="sale"),
    path('Sale/create', views.sales_create, name="sale_create"),
    path('Sale/update/<int:pk>', views.sales_update, name="sale_update"),
    path('Sale/delete/<int:pk>', views.sales_delete, name="sale_delete"),

    # order_details
    path("order/detail/create/<int:pk>", views.order_detail_create, name="order_detail_create"),
    path("order/detail/update/<int:pk>", views.order_detail_update, name="order_detail_update"),
    path("order/detail/delete/<int:pk>", views.order_detail_delete, name="order_detail_delete"),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

