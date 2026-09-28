from django.db import migrations

# Auditoria não pode ser alterada nem apagada, nem por consultas em lote
# (QuerySet.update/delete) que ignoram o model. O trigger aplica a regra no banco.
CREATE_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION audit_auditevent_block_changes() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_auditevent é somente inserção: % bloqueado', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_auditevent_block_changes
BEFORE UPDATE OR DELETE ON audit_auditevent
FOR EACH ROW EXECUTE FUNCTION audit_auditevent_block_changes();
"""

DROP_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS audit_auditevent_block_changes ON audit_auditevent;
DROP FUNCTION IF EXISTS audit_auditevent_block_changes();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(CREATE_TRIGGER_SQL, reverse_sql=DROP_TRIGGER_SQL),
    ]
