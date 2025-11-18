from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_alter_workarea_options_remove_workarea_priority_and_more'),  # <-- cseréld a megfelelő utolsó migration-re
    ]

    operations = [
        migrations.RunSQL(
            'DROP TABLE IF EXISTS "app_workrole_work_areas";',
            reverse_sql=migrations.RunSQL.noop  # nem visszafordítható; ha kell, adj meg CREATE TABLE SQL-t
        ),
    ]