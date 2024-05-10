# Generated by Django 3.2 on 2024-04-15 08:03

import apps.accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import utils.methods
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('fullname', models.CharField(blank=True, max_length=50, null=True)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile/pics')),
                ('notification_token', models.CharField(blank=True, max_length=500, null=True)),
                ('language', models.CharField(default='am', max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('telegram_id', models.CharField(blank=True, max_length=255, null=True)),
                ('referral_code', models.CharField(default=apps.accounts.models.rand, max_length=10)),
                ('role', models.CharField(choices=[('CUSTOMER', 'CUSTOMER'), ('SALES', 'SALES'), ('DEVELOPER', 'DEVELOPER'), ('ACCOUNT_MANAGER', 'ACCOUNT_MANAGER'), ('ADMIN', 'ADMIN'), ('SUPER_ADMIN', 'SUPER_ADMIN'), ('CUSTOMER_SERVICE', 'CUSTOMER_SERVICE'), ('MARKETING', 'MARKETING'), ('CONTENT_MANAGER', 'CONTENT_MANAGER')], default='CUSTOMER', max_length=60)),
                ('old_phone', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('referred_code', models.CharField(blank=True, max_length=20, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=100, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='custom_user_set', to='auth.Group', verbose_name='groups')),
                # ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_set', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'auth_user',
                'swappable': 'AUTH_USER_MODEL',
            },
        ),
        migrations.CreateModel(
            name='EmailSubscription',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='HelpVideo',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('video_url', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReferralCodeType',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('points', models.PositiveIntegerField(default=0)),
                ('type', models.CharField(choices=[('SIGNUP', 'SIGNUP'), ('ORDER', 'ORDER')], default='SIGNUP', max_length=60)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('resources', models.JSONField(default=dict)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NotificationSchedule',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('ONE_TIME', 'ONE_TIME'), ('WEEK', 'WEEK'), ('MONTH', 'MONTH'), ('EVERY_DAY', 'EVERY_DAY')], default='ONE_TIME', max_length=60)),
                ('time', models.TimeField()),
                ('notification_type', models.CharField(choices=[('USER', 'USER'), ('VENDOR', 'VENDOR'), ('SINGLE_USER', 'SINGLE_USER')], default='USER', max_length=60)),
                ('single_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NotificationHistory',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('SINGLE', 'SINGLE'), ('GROUP', 'GROUP'), ('CART', 'CART')], default='SINGLE', max_length=60)),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notify', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResetCode',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('code', models.CharField(default=utils.methods.reset_code, max_length=10)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'phone')},
            },
        ),
    ]
