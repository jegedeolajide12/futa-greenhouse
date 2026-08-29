from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_category_product_category_fk'),
    ]

    operations = [
        # 1. Remove the old unique_together (which includes the old 'category' CharField)
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set(),
        ),
        # 2. Drop the old category CharField
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        # 3. Rename the new ForeignKey 'category_fk' to 'category'
        migrations.RenameField(
            model_name='product',
            old_name='category_fk',
            new_name='category',
        ),
        # 4. Make the new category field required (non-nullable)
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                to='products.Category',
                on_delete=models.PROTECT,
                related_name='products',
                help_text='Product category',
                blank=False,
                null=False,
            ),
        ),
        # 5. Re-add the unique_together with the new ForeignKey
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('category', 'color', 'grade', 'unit')},
        ),
    ]