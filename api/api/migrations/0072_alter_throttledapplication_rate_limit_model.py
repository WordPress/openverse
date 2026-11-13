from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0071_alter_audio_options_alter_deletedaudio_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='throttledapplication',
            name='rate_limit_model',
            field=models.CharField(choices=[('standard', 'standard'), ('enhanced', 'enhanced'), ('exempt', 'exempt'), ('frontend', 'frontend')], default='standard', max_length=20),
        ),
    ]
