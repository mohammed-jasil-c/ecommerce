from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response({
            "access": str(access)
        })

        # Set refresh token in HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,  # True in production (HTTPS)
            samesite="Lax"
        )

        return response


from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

User = get_user_model()

class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)

            # Generate new access token
            new_access = refresh.access_token

            # Get user from token payload
            user_id = refresh["user_id"]
            user = User.objects.get(id=user_id)

            # Blacklist old refresh
            refresh.blacklist()

            # Create new refresh
            new_refresh = RefreshToken.for_user(user)

            response = Response({
                "access": str(new_access)
            })

            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                httponly=True,
                secure=False,
                samesite="Lax"
            )

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=400)


from rest_framework.permissions import IsAuthenticated


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except:
                pass

        response = Response({"message": "Logged out"})
        response.delete_cookie("refresh_token")
        return response
    
    
from rest_framework.permissions import IsAuthenticated

class TestProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Authenticated successfully",
            "user": request.user.email
        })

