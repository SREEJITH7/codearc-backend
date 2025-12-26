

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings


class LogoutView(APIView):
    def post(self,request):
        print("------logout view camee---")
        response = Response(
            {"success" : True , "message": "Logged out Successfully"}
        )
        response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")

        return response


