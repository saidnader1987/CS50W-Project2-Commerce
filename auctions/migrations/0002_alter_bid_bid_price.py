# Generated by Django 4.1.3 on 2022-11-06 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bid",
            name="bid_price",
            field=models.FloatField(),
        ),
    ]
