from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='display_rating',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='highlight_tag',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
