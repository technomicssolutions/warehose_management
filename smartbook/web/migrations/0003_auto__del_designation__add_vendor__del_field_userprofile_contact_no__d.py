# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Designation'
        db.delete_table(u'web_designation')

        # Adding model 'Vendor'
        db.create_table(u'web_vendor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('contact_person', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'web', ['Vendor'])

        # Deleting field 'UserProfile.contact_no'
        db.delete_column(u'web_userprofile', 'contact_no')

        # Deleting field 'UserProfile.address'
        db.delete_column(u'web_userprofile', 'address')

        # Deleting field 'UserProfile.contact_person'
        db.delete_column(u'web_userprofile', 'contact_person')

        # Deleting field 'UserProfile.vendor_id'
        db.delete_column(u'web_userprofile', 'vendor_id')

        # Deleting field 'UserProfile.email'
        db.delete_column(u'web_userprofile', 'email')

        # Adding field 'UserProfile.house_name'
        db.add_column(u'web_userprofile', 'house_name',
                      self.gf('django.db.models.fields.CharField')(default='gh', max_length=15),
                      keep_default=False)

        # Adding field 'UserProfile.street'
        db.add_column(u'web_userprofile', 'street',
                      self.gf('django.db.models.fields.CharField')(default='ss', max_length=10),
                      keep_default=False)

        # Adding field 'UserProfile.city'
        db.add_column(u'web_userprofile', 'city',
                      self.gf('django.db.models.fields.CharField')(default='ss', max_length=10),
                      keep_default=False)

        # Adding field 'UserProfile.district'
        db.add_column(u'web_userprofile', 'district',
                      self.gf('django.db.models.fields.CharField')(default='ss', max_length=10),
                      keep_default=False)

        # Adding field 'UserProfile.pin'
        db.add_column(u'web_userprofile', 'pin',
                      self.gf('django.db.models.fields.IntegerField')(default=21),
                      keep_default=False)

        # Adding field 'UserProfile.mobile'
        db.add_column(u'web_userprofile', 'mobile',
                      self.gf('django.db.models.fields.IntegerField')(default=22),
                      keep_default=False)

        # Adding field 'UserProfile.land_line'
        db.add_column(u'web_userprofile', 'land_line',
                      self.gf('django.db.models.fields.IntegerField')(default=22, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.email_id'
        db.add_column(u'web_userprofile', 'email_id',
                      self.gf('django.db.models.fields.CharField')(default='ss', max_length=25),
                      keep_default=False)

        # Deleting field 'Customer.cutomer_name'
        db.delete_column(u'web_customer', 'cutomer_name')

        # Deleting field 'Customer.pin'
        db.delete_column(u'web_customer', 'pin')

        # Deleting field 'Customer.email_id'
        db.delete_column(u'web_customer', 'email_id')

        # Deleting field 'Customer.street'
        db.delete_column(u'web_customer', 'street')

        # Deleting field 'Customer.user'
        db.delete_column(u'web_customer', 'user_id')

        # Deleting field 'Customer.city'
        db.delete_column(u'web_customer', 'city')

        # Deleting field 'Customer.house_name'
        db.delete_column(u'web_customer', 'house_name')

        # Deleting field 'Customer.district'
        db.delete_column(u'web_customer', 'district')

        # Deleting field 'Customer.mobile'
        db.delete_column(u'web_customer', 'mobile')

        # Deleting field 'Customer.land_line'
        db.delete_column(u'web_customer', 'land_line')

        # Deleting field 'Customer.customer_id'
        db.delete_column(u'web_customer', 'customer_id')

        # Adding field 'Customer.userprofile'
        db.add_column(u'web_customer', 'userprofile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']),
                      keep_default=False)

        # Deleting field 'Staff.land_line'
        db.delete_column(u'web_staff', 'land_line')

        # Deleting field 'Staff.address'
        db.delete_column(u'web_staff', 'address')

        # Deleting field 'Staff.mobile'
        db.delete_column(u'web_staff', 'mobile')

        # Deleting field 'Staff.user'
        db.delete_column(u'web_staff', 'user_id')

        # Deleting field 'Staff.salesman_name'
        db.delete_column(u'web_staff', 'salesman_name')

        # Deleting field 'Staff.salesman_id'
        db.delete_column(u'web_staff', 'salesman_id')

        # Adding field 'Staff.userprofile'
        db.add_column(u'web_staff', 'userprofile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Staff.designation'
        db.add_column(u'web_staff', 'designation',
                      self.gf('django.db.models.fields.CharField')(default='dd', max_length=10),
                      keep_default=False)

    def backwards(self, orm):
        # Adding model 'Designation'
        db.create_table(u'web_designation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('designation', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'web', ['Designation'])

        # Deleting model 'Vendor'
        db.delete_table(u'web_vendor')


        # User chose to not deal with backwards NULL issues for 'UserProfile.contact_no'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.contact_no' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'UserProfile.address'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.address' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'UserProfile.contact_person'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.contact_person' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'UserProfile.vendor_id'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.vendor_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'UserProfile.email'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.email' and its values cannot be restored.")
        # Deleting field 'UserProfile.house_name'
        db.delete_column(u'web_userprofile', 'house_name')

        # Deleting field 'UserProfile.street'
        db.delete_column(u'web_userprofile', 'street')

        # Deleting field 'UserProfile.city'
        db.delete_column(u'web_userprofile', 'city')

        # Deleting field 'UserProfile.district'
        db.delete_column(u'web_userprofile', 'district')

        # Deleting field 'UserProfile.pin'
        db.delete_column(u'web_userprofile', 'pin')

        # Deleting field 'UserProfile.mobile'
        db.delete_column(u'web_userprofile', 'mobile')

        # Deleting field 'UserProfile.land_line'
        db.delete_column(u'web_userprofile', 'land_line')

        # Deleting field 'UserProfile.email_id'
        db.delete_column(u'web_userprofile', 'email_id')


        # User chose to not deal with backwards NULL issues for 'Customer.cutomer_name'
        raise RuntimeError("Cannot reverse this migration. 'Customer.cutomer_name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.pin'
        raise RuntimeError("Cannot reverse this migration. 'Customer.pin' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.email_id'
        raise RuntimeError("Cannot reverse this migration. 'Customer.email_id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.street'
        raise RuntimeError("Cannot reverse this migration. 'Customer.street' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.user'
        raise RuntimeError("Cannot reverse this migration. 'Customer.user' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.city'
        raise RuntimeError("Cannot reverse this migration. 'Customer.city' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.house_name'
        raise RuntimeError("Cannot reverse this migration. 'Customer.house_name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.district'
        raise RuntimeError("Cannot reverse this migration. 'Customer.district' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.mobile'
        raise RuntimeError("Cannot reverse this migration. 'Customer.mobile' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.land_line'
        raise RuntimeError("Cannot reverse this migration. 'Customer.land_line' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Customer.customer_id'
        raise RuntimeError("Cannot reverse this migration. 'Customer.customer_id' and its values cannot be restored.")
        # Deleting field 'Customer.userprofile'
        db.delete_column(u'web_customer', 'userprofile_id')


        # User chose to not deal with backwards NULL issues for 'Staff.land_line'
        raise RuntimeError("Cannot reverse this migration. 'Staff.land_line' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Staff.address'
        raise RuntimeError("Cannot reverse this migration. 'Staff.address' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Staff.mobile'
        raise RuntimeError("Cannot reverse this migration. 'Staff.mobile' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Staff.user'
        raise RuntimeError("Cannot reverse this migration. 'Staff.user' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Staff.salesman_name'
        raise RuntimeError("Cannot reverse this migration. 'Staff.salesman_name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Staff.salesman_id'
        raise RuntimeError("Cannot reverse this migration. 'Staff.salesman_id' and its values cannot be restored.")
        # Deleting field 'Staff.userprofile'
        db.delete_column(u'web_staff', 'userprofile_id')

        # Deleting field 'Staff.designation'
        db.delete_column(u'web_staff', 'designation')

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
        u'web.customer': {
            'Meta': {'object_name': 'Customer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'web.staff': {
            'Meta': {'object_name': 'Staff'},
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'web.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'email_id': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'house_name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_line': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'mobile': ('django.db.models.fields.IntegerField', [], {}),
            'pin': ('django.db.models.fields.IntegerField', [], {}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'web.vendor': {
            'Meta': {'object_name': 'Vendor'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['web']