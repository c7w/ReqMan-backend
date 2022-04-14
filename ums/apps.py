from django.apps import AppConfig
from django.db.utils import OperationalError


class UmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ums"

    def ready(self):
        def try_set_default(key, value):
            from .models import Config

            try:
                obj = Config.objects.filter(key=key).first()
            except OperationalError:
                return
            if obj:
                return
            Config.objects.create(key=key, value=value)

        default_values = {
            "reset_email_template": """您好，
                                <p>
                                请点击下方链接重置您 ReqMan 账户的密码。 <br />
                                <a href="<front_url>/resetpass/<hash1>"><front_url>/resetpass/<hash1></a>
                                </p>
                                <p>
                                该链接将在<expire>后过期。如果您未申请更改密码，则可忽略此邮件，而您的密码也不会被修改。</p>
                                <p style="text-align: right;">ReqMan 运营团队</p>""",
            "front_url": "https://frontend-dev-undefined.app.secoder.net/",
            "reset_email_title": "[ReqMan] 密码重置提醒",
            "email_username": "reqman@foxmail.com",
            "email_host": "smtp.qq.com",
            "email_auth": "ousjljeyregndcab",
            "verify_email_template": """您好，
                                <p>
                                请点击下方链接验证您 ReqMan 账户的邮箱。 <br />
                                <a href="<front_url>/verifyemail/<hash>"><front_url>/verifyemail/<hash></a>
                                </p>
                                <p>
                                该链接将在<expire>后过期。如果您未申请验证该邮箱，则可忽略此邮件。</p>
                                <p style="text-align: right;">ReqMan 运营团队</p>""",
            "verify_email_title": "[ReqMan] 邮箱验证",
        }
        for k, v in default_values.items():
            try_set_default(k, v)

        print("possible default value initialized")
