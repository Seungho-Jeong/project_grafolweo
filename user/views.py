import json
import bcrypt
import jwt
import my_settings

from django.http        import JsonResponse, HttpResponse
from django.views       import View
from django.db.models   import Q

from .models        import User

class SignUpView(View): # 클래스명 협의 필요
    def post(self, request):
        data = json.loads(request.body)

        try:
            if not (data["email"] and data["mobile"] and data["user_name"]):
                return JsonResponse({"message": "NO_VALUES"}, status = 400)

            if User.objects.filter(email = data["email"]).exists():
                return JsonResponse({"message": "EXISTS_EMAIL"}, status = 400)

            if User.objects.filter(mobile = data["mobile"]).exists():
                return JsonResponse({"message": "EXISTS_MOBILE"}, status = 400)

            if len(data["password"]) < 8:
                return JsonResponse({"message": "PW_IS_TOO_SHORT"}, status = 400)

            if "@" not in str(data["email"]) or "." not in str(data["email"]):
                return JsonResponse({"message": "NOT_IN_EMAIL_FORM"}, status = 400)

            else:
                hashed_password = bcrypt.hashpw(data["password"].encode("UTF-8"), bcrypt.gensalt())
                User.objects.create(
                    user_name   = data["user_name"],
                    email       = data["email"],
                    mobile      = data["mobile"],
                    password    = hashed_password.decode("UTF-8")
                )
                return JsonResponse({"message": "SUCCESS"}, status = 200)

        except KeyError as e:
            return JsonResponse({"message": f"KEY_ERROR:{e}"}, status = 400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status = 400)

        except:
            return JsonResponse({"message": "INVALID_ERROR"}, status = 400)

    def get(self, request):
        try:
            user_data = User.objects.values()
            return JsonResponse({"user": list(user_data)}, status = 200)

        except KeyError as e:
            return JsonResponse({"message": f"KEY_ERROR:{e}"}, status = 400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status = 400)

        except:
            return JsonResponse({"message": "INVALID_ERROR"}, status = 400)

class LoginView(View):
    def post(self, request):

        try:
            data        = json.loads(request.body)
            given_email = data["email"]
            given_pw    = data["password"]

            if User.objects.filter(email = given_email).exists():
                account = User.objects.get(email = given_email)

                if account:

                    if bcrypt.checkpw(given_pw.encode("UTF-8"), account.password.encode("UTF-8")):
                        token = jwt.encode(
                            {"email": given_email},
                            my_settings.SECRET["secret"],
                            algorithm = my_settings.ALGORITHM["algorithm"]
                                          )
                        token = token.decode("UTF-8")
                        return JsonResponse({"message": "SUCCESS", "token": token}, status = 200)

                    else:
                        return JsonResponse({"message": "WRONG_PASSWORD"}, status = 401)

            else:
                return JsonResponse({"message": "DOES_NOT_EXIST_USER"}, status = 401)

        except KeyError as e:
            return JsonResponse({"message": f"KEY_ERROR:{e}"}, status = 400)

        except ValueError as e:
            return JsonResponse({"message": f"VALUE_ERROR:{e}"}, status = 400)

        except:
            return JsonResponse({"message": "INVALID_ERROR"}, status = 400)
