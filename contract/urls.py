from django.urls import path, include
from django.conf.urls import handler404
from django.shortcuts import render
from contract.views.cpf_view import cpf_view
from contract.views.session_view import session_view
from contract.views.contact_view import contact_view
from contract.views.login_view import login_view
from contract.views.enem_view import enem_upload_view, EnemDataViewSet 
from contract.views.enem_result_view import enem_result_view
from contract.views.confirm_send_view import confirm_send_view
from contract.views.messages_view import confirm_success_view, confirm_error_view
from contract.views.messages_view import render_message
from contract.views.merito_academico_view import merito_academico_input, MeritoAcademicoViewSet
from contract.views.merito_academico_confirm import merito_academico_confirm
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'enemdata', EnemDataViewSet)
router.register(r'meritoacademico', MeritoAcademicoViewSet, basename='meritoacademico')


# Função para a página 404
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

urlpatterns = [
    path('session/', session_view, name='session_view'),
    path('contact/', contact_view, name='contact_view'),
    path('login/', login_view, name='login_view'),
    path('', cpf_view, name='cpf_view'),
    path('enem-upload/', enem_upload_view, name='enem_upload'),
    path('enem-result/', enem_result_view, name='enem_result_view'),
    path('confirm-send/', confirm_send_view, name='confirm_send'),
    path('merito-academico/input/', merito_academico_input, name='merito_academico_input'),
    path('merito-academico/confirm/', merito_academico_confirm, name='merito_academico_confirm'),
    path('message/<str:message_type>/', render_message, name='message_view'),
    path('confirm-success/', confirm_success_view, name='confirm_success'),
    path('confirm-error/', confirm_error_view, name='confirm_error'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]

# Definindo o handler
handler404 = custom_404_view
