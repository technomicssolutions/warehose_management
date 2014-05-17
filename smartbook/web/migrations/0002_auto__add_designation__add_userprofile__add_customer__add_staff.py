# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Designation'
        db.create_table(u'web_designation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('designation', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'web', ['Designation'])

        # Adding model 'UserProfile'
        db.create_table(u'web_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('user_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('vendor_id', self.gf('django.db.models.fields.IntegerField')()),
            ('contact_person', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('contact_no', self.gf('django.db.models.fields.IntegerField')()),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'web', ['UserProfile'])

        # Adding model 'Customer'
        db.create_table(u'web_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('customer_id', self.gf('django.db.models.fields.IntegerField')()),
            ('cutomer_name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('house_name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('pin', self.gf('django.db.models.fields.IntegerField')()),
            ('mobile', self.gf('django.db.models.fields.IntegerField')()),
            ('land_line', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('email_id', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'web', ['Customer'])

        # Adding model 'Staff'
        db.create_table(u'web_staff', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('salesman_id', self.gf('django.db.models.fields.IntegerField')()),
            ('salesman_name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('mobile', self.gf('django.db.models.fields.IntegerField')()),
            ('land_line', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal(u'web', ['Staff'])

    def backwards(self, orm):
        # Deleting model 'Designation'
        db.delete_table(u'web_designation')

        # Deleting model 'UserProfile'
        db.delete_table(u'web_userprofile')

        # Deleting model 'Customer'
        db.delete_table(u'web_customer')

        # Deleting model 'Staff'
        db.delete_table(u'web_staff')

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
            'city': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'customer_id': ('django.db.models.fields.IntegerField', [], {}),
            'cutomer_name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'email_id': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'house_name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_line': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'mobile': ('django.db.models.fields.IntegerField', [], {}),
            'pin': ('django.db.models.fields.IntegerField', [], {}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'web.designation': {
            'Meta': {'object_name': 'Designation'},
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'web.staff': {
            'Meta': {'object_name': 'Staff'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_line': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'mobile': ('django.db.models.fields.IntegerField', [], {}),
            'salesman_id': ('django.db.models.fields.IntegerField', [], {}),
            'salesman_name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'web.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'contact_no': ('django.db.models.fields.IntegerField', [], {}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'vendor_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['web']