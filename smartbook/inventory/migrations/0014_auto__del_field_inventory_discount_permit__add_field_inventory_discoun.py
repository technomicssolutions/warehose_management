# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Inventory.discount_permit'
        db.delete_column(u'inventory_inventory', 'discount_permit')

        # Adding field 'Inventory.discount_permit_percentage'
        db.add_column(u'inventory_inventory', 'discount_permit_percentage',
                      self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=3, blank=True),
                      keep_default=False)

        # Adding field 'Inventory.discount_permit_amount'
        db.add_column(u'inventory_inventory', 'discount_permit_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=3, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Adding field 'Inventory.discount_permit'
        db.add_column(u'inventory_inventory', 'discount_permit',
                      self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=2, blank=True),
                      keep_default=False)

        # Deleting field 'Inventory.discount_permit_percentage'
        db.delete_column(u'inventory_inventory', 'discount_permit_percentage')

        # Deleting field 'Inventory.discount_permit_amount'
        db.delete_column(u'inventory_inventory', 'discount_permit_amount')

    models = {
        u'inventory.brand': {
            'Meta': {'object_name': 'Brand'},
            'brand': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '51'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inventory.inventory': {
            'Meta': {'object_name': 'Inventory'},
            'discount_permit_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3', 'blank': 'True'}),
            'discount_permit_percentage': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'})
        },
        u'inventory.item': {
            'Meta': {'object_name': 'Item'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Brand']"}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'uom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.UnitOfMeasure']"})
        },
        u'inventory.unitofmeasure': {
            'Meta': {'object_name': 'UnitOfMeasure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['inventory']