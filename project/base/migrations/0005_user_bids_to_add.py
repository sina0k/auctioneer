# Generated by Django 3.2.19 on 2023-06-28 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bids_to_add',
            field=models.IntegerField(default=0),
        ),
    ]