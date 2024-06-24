# Generated by Django 5.0.6 on 2024-06-12 21:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopWeb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='Img',
        ),
        migrations.AlterField(
            model_name='producto',
            name='descripcion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='id_categoria',
            field=models.ForeignKey(db_column='idCategoria', on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='shopWeb.categoria'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='id_producto',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='SubCategoria',
            fields=[
                ('id_subcategoria', models.AutoField(db_column='idSubCategoria', primary_key=True, serialize=False)),
                ('subcategoria', models.CharField(max_length=15)),
                ('id_categoria', models.ForeignKey(db_column='idCategoria', on_delete=django.db.models.deletion.CASCADE, to='shopWeb.categoria')),
            ],
        ),
        migrations.AddField(
            model_name='producto',
            name='id_subcategoria',
            field=models.ForeignKey(db_column='idSubCategoria', default=1, on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='shopWeb.subcategoria'),
        ),
        migrations.AddField(
            model_name='producto',
            name='img',
            field=models.ImageField(default=1, upload_to='productos/'),
            preserve_default=False,
        ),
    ]