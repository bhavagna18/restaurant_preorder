from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        import os

        if os.getenv("CREATE_SUPERUSER") == "true":
            from django.contrib.auth import get_user_model

            User = get_user_model()

            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    "admin",
                    "admin@example.com",
                    "admin123"
                )
