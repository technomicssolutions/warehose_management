# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PurchaseItem.item_frieght'
        db.alter_column(u'purchase_purchaseitem', 'item_frieght', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'PurchaseItem.item_handling'
        db.alter_column(u'purchase_purchaseitem', 'item_handling', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'PurchaseItem.frieght_per_unit'
        db.alter_column(u'purchase_purchaseitem', 'frieght_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'PurchaseItem.expense_per_unit'
        db.alter_column(u'purchase_purchaseitem', 'expense_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'PurchaseItem.expense'
        db.alter_column(u'purchase_purchaseitem', 'expense', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'PurchaseItem.handling_per_unit'
        db.alter_column(u'purchase_purchaseitem', 'handling_per_unit', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'VendorAccount.total_amount'
        db.alter_column(u'purchase_vendoraccount', 'total_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'VendorAccount.paid_amount'
        db.alter_column(u'purchase_vendoraccount', 'paid_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))

        # Changing field 'VendorAccount.balance'
        db.alter_column(u'purchase_vendoraccount', 'balance', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=3))
        # Deleting field 'PurchaseReturn.time'
        db.delete_column(u'purchase_purchasereturn', 'time')

        # Deleting field 'PurchaseReturn.quantity'
        db.delete_column(u'purchase_purchasereturn', 'quantity')

        # Adding field 'PurchaseReturn.return_invoice_number'
        db.add_column(u'purchase_purchasereturn', 'return_invoice_number',
                      self.gf('django.db.models.fields.IntegerField')(default=2, unique=True),
                      keep_default=False)

        # Adding field 'PurchaseReturn.amount'
        db.add_column(u'purchase_purchasereturn', 'amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=3),
                      keep_default=False)

    def backwards(self, orm):

        # Changing field 'PurchaseItem.item_frieght'
        db.alter_column(u'purchase_purchaseitem', 'item_frieght', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PurchaseItem.item_handling'
        db.alter_column(u'purchase_purchaseitem', 'item_handling', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PurchaseItem.frieght_per_unit'
        db.alter_column(u'purchase_purchaseitem', 'frieght_per_unit', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PurchaseItem.expense_per_unit'
        db.alter_column(u'purchase_purchaseitem', 'expense_per_unit', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PurchaseItem.expense'
        db.alter_column(u'purchase_purchaseitem', 'expense', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PurchaseItem.handling_per_unit'
        db.alter_column(u'purchase_purchaseitem', 'handling_per_unit', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'VendorAccount.total_amount'
        db.alter_column(u'purchase_vendoraccount', 'total_amount', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'VendorAccount.paid_amount'
        db.alter_column(u'purchase_vendoraccount', 'paid_amount', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'VendorAccount.balance'
        db.alter_column(u'purchase_vendoraccount', 'balance', self.gf('django.db.models.fields.IntegerField')())

        # User chose to not deal with backwards NULL issues for 'PurchaseReturn.time'
        raise RuntimeError("Cannot reverse this migration. 'PurchaseReturn.time' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PurchaseReturn.quantity'
        raise RuntimeError("Cannot reverse this migration. 'PurchaseReturn.quantity' and its values cannot be restored.")
        # Deleting field 'PurchaseReturn.return_invoice_number'
        db.delete_column(u'purchase_purchasereturn', 'return_invoice_number')

        # Deleting field 'PurchaseReturn.amount'
        db.delete_column(u'purchase_purchasereturn', 'amount')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'inventory.brand': {
            'Meta': {'object_name': 'Brand'},
            'brand': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '51'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        },
        u'purchase.purchase': {
            'Meta': {'object_name': 'Purchase'},
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Brand']", 'null': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'grant_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'purchase_expense': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'purchase_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'purchase_invoice_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'transportation_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.TransportationCompany']", 'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Vendor']", 'null': 'True', 'blank': 'True'}),
            'vendor_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'vendor_do_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vendor_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'vendor_invoice_number': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'purchase.purchaseitem': {
            'Meta': {'object_name': 'PurchaseItem'},
            'cost_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'expense': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'expense_per_unit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'frieght_per_unit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'handling_per_unit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inventory.Item']", 'null': 'True', 'blank': 'True'}),
            'item_frieght': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'item_handling': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'net_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['purchase.Purchase']", 'null': 'True', 'blank': 'True'}),
            'quantity_purchased': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'purchase.purchasereturn': {
            'Meta': {'object_name': 'PurchaseReturn'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['purchase.Purchase']"}),
            'return_invoice_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'purchase.vendoraccount': {
            'Meta': {'object_name': 'VendorAccount'},
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'branch_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_no': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narration': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'paid_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'default': "'cash'", 'max_length': '10'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['web.Vendor']", 'unique': 'True'})
        },
        u'web.transportationcompany': {
            'Meta': {'object_name': 'TransportationCompany'},
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'web.vendor': {
            'Meta': {'object_name': 'Vendor'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['purchase']