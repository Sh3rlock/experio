from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(
                blank=True,
                choices=[(code, label) for code, label in settings.LANGUAGES],
                default=settings.LANGUAGE_CODE,
                max_length=10,
            ),
        ),
    ]
