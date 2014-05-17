# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Expense.bank_name'
        db.alter_column(u'expenses_expense', 'bank_name', self.gf('django.db.models.fields.CharField')(max_length=15, null=True))

        # Changing field 'Expense.date'
        db.alter_column(u'expenses_expense', 'date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Expense.cheque_date'
        db.alter_column(u'expenses_expense', 'cheque_date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Expense.cheque_no'
        db.alter_column(u'expenses_expense', 'cheque_no', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Expense.amount'
        db.alter_column(u'expenses_expense', 'amount', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Expense.branch'
        db.alter_column(u'expenses_expense', 'branch', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'Expense.expense_head'
        db.alter_column(u'expenses_expense', 'expense_head_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['expenses.ExpenseHead'], null=True))
        # Adding unique constraint on 'Expense', fields ['voucher_no']
        db.create_unique(u'expenses_expense', ['voucher_no'])

    def backwards(self, orm):
        # Removing unique constraint on 'Expense', fields ['voucher_no']
        db.delete_unique(u'expenses_expense', ['voucher_no'])


        # User chose to not deal with backwards NULL issues for 'Expense.bank_name'
        raise RuntimeError("Cannot reverse this migration. 'Expense.bank_name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Expense.date'
        raise RuntimeError("Cannot reverse this migration. 'Expense.date' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Expense.cheque_date'
        raise RuntimeError("Cannot reverse this migration. 'Expense.cheque_date' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Expense.cheque_no'
        raise RuntimeError("Cannot reverse this migration. 'Expense.cheque_no' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Expense.amount'
        raise RuntimeError("Cannot reverse this migration. 'Expense.amount' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Expense.branch'
        raise RuntimeError("Cannot reverse this migration. 'Expense.branch' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Expense.expense_head'
        raise RuntimeError("Cannot reverse this migration. 'Expense.expense_head' and its values cannot be restored.")
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
        u'expenses.expense': {
            'Meta': {'object_name': 'Expense'},
            'amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bank_name': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'cheque_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cheque_no': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'expense_head': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['expenses.ExpenseHead']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narration': ('django.db.models.fields.TextField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'payment_mode': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'voucher_no': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'expenses.expensehead': {
            'Meta': {'object_name': 'ExpenseHead'},
            'expense_head': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['expenses']