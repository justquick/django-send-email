from contextlib import contextmanager

from django.test import TestCase
from django.conf import settings
from django.core.management import CommandError, call_command
from django.core import mail


class SettingDoesNotExist:
    pass


@contextmanager
def patch_settings(**kwargs):
    old_settings = []
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings.append((key, old_value))
        setattr(settings, key, new_value)
    yield
    for key, old_value in old_settings:
        if old_value is SettingDoesNotExist:
            delattr(settings, key)
        else:
            setattr(settings, key, old_value)


class ErrorTest(TestCase):
    def test_noargs(self):
        self.assertRaises(CommandError, call_command, 'send_email_message')

    def test_bad_address(self):
        self.assertRaises(CommandError, call_command, 'send_email_message', 'subject', 'message', 'bogus')

    def test_bad_cop_addresses(self):
        self.assertRaises(CommandError, call_command, 'send_email_message', 'subject', 'message', 'user@example.com',
                          bcc='bogus', cc='bogus')


class BaseEmailTest(TestCase):
    subject = 'subject'
    body = 'message'
    recipients = ['user@example.com']
    options = {}
    message = {}
    new_settings = {}

    def test_send_email(self):
        self.options.update(interactive=False)
        with patch_settings(**self.new_settings):
            if self.__class__.__name__ != 'BaseEmailTest':
                call_command('send_email_message', self.subject, self.body, *self.recipients, **self.options)
            self.validate_outbox(mail.outbox)

    def validate_outbox(self, outbox):
        self.assertEqual(len(outbox), 1 if self.message else 0)
        for key, value in self.message.items():
            self.assertEqual(getattr(outbox[0], key), value)


class BasicEmailTest(BaseEmailTest):
    message = {
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'to': ['user@example.com'],
        'body': 'message',
        'subject': '[Django] subject'
    }


class SubjectEmailTest(BaseEmailTest):
    subject = 'Text'
    new_settings = {
        'EMAIL_SUBJECT_PREFIX': 'Prefix '
    }
    message = {
        'subject': 'Prefix Text'
    }


class NoPrefixEmailTest(BaseEmailTest):
    options = {
        'noprefix': True
    }
    message = {
        'subject': 'subject'
    }


class MessageFileEmailTest(BaseEmailTest):
    body = __file__
    message = {
        'body': open(__file__).read()
    }


class RecipientsEmailTest(BaseEmailTest):
    recipients = ['user1@example.com', 'user1@example.com']
    message = {
        'to': ['user1@example.com', 'user1@example.com']
    }


class DefaultFromEmailTest(BaseEmailTest):
    new_settings = {
        'DEFAULT_FROM_EMAIL': 'user@example.com'
    }
    message = {
        'from_email': 'user@example.com'
    }


class FromEmailTest(BaseEmailTest):
    options = {
        'from_email': 'webmaster@example.com'
    }
    message = {
        'from_email': 'webmaster@example.com'
    }


class CCEmailTest(BaseEmailTest):
    options = {
        'cc': 'user1@example.com,user2@example.com'
    }
    message = {
        'cc': ['user1@example.com', 'user2@example.com']
    }


class BCCEmailTest(BaseEmailTest):
    options = {
        'bcc': 'user1@example.com,user2@example.com'
    }
    message = {
        'bcc': ['user1@example.com', 'user2@example.com']
    }
