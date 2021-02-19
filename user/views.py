import json
import bcrypt
import jwt
import re
import my_settings

from django.http      import JsonResponse, HttpResponse
from django.views     import View
from django.db.models import Q

from .models          import User

class SignUpView(View):
    def post(self, request):
        """
        유저 회원가입
        :param request:
            user_name,
            email,
            mobile,
            password,
            profile_image_url,
            introduction
        :return:
            201: success
            400: exception error
            401: key error
        """

        try:
            data = json.loads(request.body)

            if User.objects.filter(email=data["email"]).exists():
                return JsonResponse({"MESSAGE": "EXISTS_EMAIL"}, status=400)

            if User.objects.filter(mobile=data["mobile"]).exists():
                return JsonResponse({"MESSAGE": "EXISTS_MOBILE"}, status=400)

            if len(data["password"]) < 8:
                return JsonResponse({"MESSAGE": "PW_IS_TOO_SHORT"}, status=400)

            if not re.match("^01(0|1|6|7|8|9)([0-9]{3,4})([0-9]{4})$", data["mobile"]):
                return JsonResponse({"MESSAGE": "NOT_IN_PHONE_NUMBER_FROM"}, status=400)

            if not re.match("^[a-zA-Z0-9]([-_\.]?[a-zA-Z0-9])*@[a-zA-Z0-9]([-_\.]?[a-zA-Z0-9])*\.[a-zA-Z]{2,}$", data["email"]):
                return JsonResponse({"MESSAGE": "NOT_IN_EMAIL_FORM"}, status=400)

            hashed_password = bcrypt.hashpw(
                data["password"].encode("UTF-8"), bcrypt.gensalt())
            User.objects.create(
                user_name        = data["user_name"],
                email            = data["email"],
                mobile           = data["mobile"],
                password         = hashed_password.decode("UTF-8"),
                introduction     = data["introduction"],
                profile_image_url= data["profile_image_url"]
            )
            return JsonResponse({"MESSAGE": "SUCCESS"}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR {}".format(e)}, status=401)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERROR {}".format(e)}, status=400)

class LoginView(View):
    def post(self, request):
        """
        유저 로그인
        :param request:
            email,
            password
        :return:
            200: success
            401: input error, key error
            400: exception error
        """

        try:
            data    = json.loads(request.body)
            user    = User.objects.get(email=data["email"])
            user_id = user.id

            if not bcrypt.checkpw(data["password"].encode("UTF-8"), user.password.encode("UTF-8")):
                return JsonResponse({"MESSAGE": "INVALID_INPUT"}, status=401)

            token = jwt.encode(
                    {"user_id": user_id},
                    my_settings.SECRET["secret"],
                    algorithm = my_settings.ALGORITHM["algorithm"]
            )

            return JsonResponse({
                        "MESSAGE"       : "LOGIN_SUCCESS",
                        "Authorization" : token.decode("UTF-8")
                        }, status=200)

        except User.DoesNotExist:
            return JsonResponse({"MESSAGE": "INVALID_INPUT"}, status=401)
        except KeyError as e:
            return JsonResponse({"MESSAGE": f"KEY_ERROR:{e}"}, status=401)
        except Exception as e:
            return JsonResponse({"MESSAGE": f"{e}_ERROR!"}, status=400)
