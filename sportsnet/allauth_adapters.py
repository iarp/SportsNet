from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

# from django_templated_emailer.models import EmailQueue
# from django_templated_emailer import utils, tasks
# from iarp.celery_helper import call_celery_task
#
# from core_data.models import Setting


class MyOverriddenDefaultAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False

    # def send_mail(self, template_prefix, email, context):
    #     msg = self.render_mail(template_prefix, email, context)
    #
    #     try:
    #         eq = EmailQueue.queue_email(
    #             template_name=f'allauth - {template_prefix}',
    #
    #             send_to=utils.unique_emails(msg.to, joiner=';'),
    #             cc_to=utils.unique_emails(msg.cc, joiner=';'),
    #             bcc_to=utils.unique_emails(msg.bcc, joiner=';'),
    #             send_after_minutes=0,
    #
    #             **context
    #         )
    #         if not eq:
    #             raise ValueError(f'No template found for allauth-{template_prefix}')
    #     except:
    #
    #         print('allauth EmailQueue failure')
    #
    #         eq = EmailQueue.objects.create(
    #             template_name=template_prefix,
    #
    #             send_to=utils.unique_emails(msg.to, joiner=';'),
    #             cc_to=utils.unique_emails(msg.cc, joiner=';'),
    #             bcc_to=utils.unique_emails(msg.bcc, joiner=';'),
    #             send_after_minutes=0,
    #
    #             subject=msg.subject,
    #             body=msg.body
    #         )
    #
    #     if eq:
    #         call_celery_task(tasks.send_emailqueue_items)


class MyOverriddenDefaultSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return False
