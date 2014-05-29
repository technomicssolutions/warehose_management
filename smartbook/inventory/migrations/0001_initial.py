# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UnitOfMeasure'
        db.create_table(u'inventory_unitofmeasure', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uom', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'inventory', ['UnitOfMeasure'])

        # Adding model 'Brand'
        db.create_table(u'inventory_brand', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('brand', self.gf('django.db.models.fields.CharField')(unique=True, max_length=51)),
        ))
        db.send_create_signal(u'inventory', ['Brand'])

        # Adding model 'InventoryItem'
        db.create_table(u'inventory_inventoryitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=50, null=True, blank=True)),
            ('uom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.UnitOfMeasure'], null=True, blank=True)),
            ('brand', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.Brand'], null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('unit_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('selling_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('discount_permit_percentage', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=3, blank=True)),
            ('discount_permit_amount', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=3, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['InventoryItem'])

        # Adding model 'OpeningStock'
        db.create_table(u'inventory_openingstock', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.InventoryItem'])),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('unit_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('selling_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('discount_permit_percentage', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=3, blank=True)),
            ('discount_permit_amount', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=14, decimal_places=3, blank=True)),
        ))
        db.send_create_signal(u'inventory', ['OpeningStock'])

    def backwards(self, orm):
        # Deleting model 'UnitOfMeasure'
        db.delete_table(u'inventory_unitofmeasure')

        # Deleting model 'Brand'
        db.delete_table(u'inventory_brand')

        # Deleting model 'InventoryItem'
        db.delete_table(u'inventory_inventoryitem')

        # Deleting model 'OpeningStock'
        db.delete_table(u'inventory_openingstock')

    models = {
        u'inventory.brand': {
            'Meta': {'object_name': 'Brand'},
            'brand': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '51'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inventory.inventoryitem': {
            'Meta': {'object_name': 'InventoryItem'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Brand']", 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'discount_permit_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3', 'blank': 'True'}),
            'discount_permit_percentage': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'uom': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.UnitOfMeasure']", 'null': 'True', 'blank': 'True'})
        },
        u'inventory.openingstock': {
            'Meta': {'object_name': 'OpeningStock'},
            'discount_permit_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3', 'blank': 'True'}),
            'discount_permit_percentage': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.InventoryItem']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'})
        },
        u'inventory.unitofmeasure': {
            'Meta': {'object_name': 'UnitOfMeasure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uom': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['inventory']