from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from ...models import Task

class Command(BaseCommand):

      def handle(self, *args, **kwargs):
        fake = Faker()
        User = get_user_model()

        try:
            kbr_user = User.objects.get(username='Kbr')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User kbr does not exist'))
            return

        for i in range(100000):
            task = Task(
                user=kbr_user,
                title=fake.sentence(),
                
            )
            task.save()

        self.stdout.write(self.style.SUCCESS('Successfully created tasks for user kbr'))

