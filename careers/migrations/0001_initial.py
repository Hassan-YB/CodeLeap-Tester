# Generated by Django 4.1.2 on 2024-01-12 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('basedatetimemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.basedatetimemodel')),
                ('username', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
            ],
            bases=('core.basedatetimemodel',),
        ),
    ]
