# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Uom'
        db.delete_table(u'inventory_uom')

        # Adding model 'Unit_of_measure'
        db.create_table(u'inventory_unit_of_measure', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uom', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'inventory', ['Unit_of_measure'])

        # Deleting field 'Item.vendor'
        db.delete_column(u'inventory_item', 'vendor_id')

        # Deleting field 'Item.brand'
        db.delete_column(u'inventory_item', 'brand_id')


        # Changing field 'Item.description'
        db.alter_column(u'inventory_item', 'description', self.gf('django.db.models.fields.TextField')(max_length=50, null=True))

        # Changing field 'Item.barcode'
        db.alter_column(u'inventory_item', 'barcode', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'Item.uom'
        db.alter_column(u'inventory_item', 'uom_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Unit_of_measure']))
        # Adding field 'Inventory.discount_permit'
        db.add_column(u'inventory_inventory', 'discount_permit',
                      self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=2, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Adding model 'Uom'
        db.create_table(u'inventory_uom', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uom', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'inventory', ['Uom'])

        # Deleting model 'Unit_of_measure'
        db.delete_table(u'inventory_unit_of_measure')


        # User chose to not deal with backwards NULL issues for 'Item.vendor'
        raise RuntimeError("Cannot reverse this migration. 'Item.vendor' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Item.brand'
        raise RuntimeError("Cannot reverse this migration. 'Item.brand' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Item.description'
        raise RuntimeError("Cannot reverse this migration. 'Item.description' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Item.barcode'
        raise RuntimeError("Cannot reverse this migration. 'Item.barcode' and its values cannot be restored.")

        # Changing field 'Item.uom'
        db.alter_column(u'inventory_item', 'uom_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Uom']))
        # Deleting field 'Inventory.discount_permit'
        db.delete_column(u'inventory_inventory', 'discount_permit')

    models = {
        u'inventory.brand': {
            'Meta': {'object_name': 'Brand'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'inventory.inventory': {
            'Meta': {'object_name': 'Inventory'},
            'discount_permit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'})
        },
        u'inventory.item': {
            'Meta': {'object_name': 'Item'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'uom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Unit_of_measure']"})
        },
        u'inventory.unit_of_measure': {
            'Meta': {'object_name': 'Unit_of_measure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uom': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['inventory']