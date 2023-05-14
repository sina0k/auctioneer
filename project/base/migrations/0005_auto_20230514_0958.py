# Generated by Django 3.2.19 on 2023-05-14 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_auction_start_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='bids',
            new_name='bids_number',
        ),
        migrations.RemoveField(
            model_name='deal',
            name='buyer',
        ),
        migrations.AddField(
            model_name='deal',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='base.user'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Electronics and Computers', 'ELEC'), ('Cars', 'CAR'), ('Bid Packs', 'BID'), ('Home, Garden and Tools', 'HOME'), ('Fashion, Health and Beauty', 'FASHION'), ('Gift Cards', 'CARD'), ('Kitchen and Dining', 'KITCHEN'), ('Other', 'OTHER')], default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='deal',
            name='deal_type',
            field=models.CharField(choices=[('Auction', 'AUCTION'), ('Buy', 'BUY')], max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('time', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='base.user')),
            ],
        ),
    ]