# Generated by Django 5.1.6 on 2025-03-02 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link', '0002_rename_created_at_profile_date_joined_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirm_password',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
