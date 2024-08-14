from django.contrib import admin
from .models import Cuenta
from meli_api.apicon import MeliAPI
from meli_api.admin import resp_ok
from unfold.admin import ModelAdmin



# Register your models here.
@admin.register(Cuenta)
class CuentaAdmin(ModelAdmin):
    list_display = ['name','user','user']
    actions = ('get_credenciales',)

    @admin.action(description='Get Token')
    def get_credenciales(self,request,objetos):
        for obj in objetos:
            resp = MeliAPI(obj).auth_token()
            if resp_ok(resp, 'Autorizar Token'):
                obj.access_token = resp.json()['access_token']
                obj.refresh_secret = resp.json()['refresh_token']
                self.message_user(
                    request,
                    'Access token conseguido'
                )
            else:
                resp = MeliAPI(obj).renew_token()
                if resp_ok(resp, 'Renovar token'):
                    obj.access_token = resp.json()['access_token']
                    obj.refresh_secret = resp.json()['refresh_token']
                    self.message_user(request,f'Access Token renovado{resp.text}')
                else:
                    self.message_user(
                        request,
                        f'{str(resp.text)}', level="ERROR"
                    )
            obj.save()
            resp_user = MeliAPI(obj).get_user_me()
            if resp_ok(resp_user, 'Carga user ID'):
                obj.user_meli = resp_user.json()['id']
                self.message_user(request,'User id cargado')
            else:
                self.message_user(request,f'User id no identificado {resp_user.text}')
            obj.save()