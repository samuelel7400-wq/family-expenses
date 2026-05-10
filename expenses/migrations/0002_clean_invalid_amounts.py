from decimal import Decimal, InvalidOperation

from django.db import migrations


AMOUNT_PLACES = Decimal('0.01')


def clean_invalid_amounts(apps, schema_editor):
    Expense = apps.get_model('expenses', 'Expense')
    table_name = Expense._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'SELECT id, amount FROM {table_name}')
        rows = cursor.fetchall()

        for row_id, raw_amount in rows:
            try:
                amount = Decimal(str(raw_amount).strip()).quantize(AMOUNT_PLACES)
            except (InvalidOperation, TypeError, ValueError):
                amount = Decimal('0.00')

            if not amount.is_finite() or amount < 0 or amount > Decimal('99999999.99'):
                amount = Decimal('0.00')

            cursor.execute(
                f'UPDATE {table_name} SET amount = %s WHERE id = %s',
                [str(amount), row_id],
            )


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clean_invalid_amounts, migrations.RunPython.noop),
    ]
