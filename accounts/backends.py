from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    """Authenticate using email instead of username."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"EmailAuthBackend attempting to authenticate: {username}")
        try:
            user = User.objects.get(email=username)
            print(f"User found with email: {username}")
            if user.check_password(password):
                print("Password check successful")
                return user
            else:
                print("Password check failed")
        except User.DoesNotExist:
            print(f"No user found with email: {username}")
            return None