# Generated by Django 3.1.7 on 2021-04-01 17:03

from django.db import migrations, models
import portfolio_tracking.models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio_tracking', '0003_remove_trade_portfolio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='shares',
            field=models.PositiveIntegerField(validators=[portfolio_tracking.models.validateShares]),
        ),
        migrations.AlterField(
            model_name='trade',
            name='shares',
            field=models.PositiveIntegerField(validators=[portfolio_tracking.models.validateShares]),
        ),
    ]
