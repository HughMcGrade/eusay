# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Proposal.slug'
        db.alter_column('eusay_proposal', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50))
        # Adding field 'User.slug'
        db.add_column('eusay_user', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='slug', max_length=50),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Proposal.slug'
        db.alter_column('eusay_proposal', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=100))
        # Deleting field 'User.slug'
        db.delete_column('eusay_user', 'slug')


    models = {
        'eusay.comment': {
            'Meta': {'object_name': 'Comment'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['eusay.Proposal']"}),
            'replyTo': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['eusay.Comment']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['eusay.User']"})
        },
        'eusay.commentreport': {
            'Meta': {'_ormbases': ['eusay.Report'], 'object_name': 'CommentReport'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': "orm['eusay.Comment']"}),
            'report_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['eusay.Report']"})
        },
        'eusay.commentvote': {
            'Meta': {'_ormbases': ['eusay.Vote'], 'object_name': 'CommentVote'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['eusay.Comment']"}),
            'vote_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['eusay.Vote']"})
        },
        'eusay.hideaction': {
            'Meta': {'object_name': 'HideAction'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        'eusay.hidecommentaction': {
            'Meta': {'_ormbases': ['eusay.HideAction'], 'object_name': 'HideCommentAction'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hideActions'", 'to': "orm['eusay.Comment']"}),
            'hideaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['eusay.HideAction']"})
        },
        'eusay.hideproposalaction': {
            'Meta': {'_ormbases': ['eusay.HideAction'], 'object_name': 'HideProposalAction'},
            'hideaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['eusay.HideAction']"}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hideActions'", 'to': "orm['eusay.Proposal']"})
        },
        'eusay.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'proposer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proposed'", 'to': "orm['eusay.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "'slug'", 'max_length': '50'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'proposals'", 'to': "orm['eusay.Tag']", 'symmetrical': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'eusay.proposalreport': {
            'Meta': {'_ormbases': ['eusay.Report'], 'object_name': 'ProposalReport'},
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': "orm['eusay.Proposal']"}),
            'report_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['eusay.Report']"})
        },
        'eusay.proposalvote': {
            'Meta': {'_ormbases': ['eusay.Vote'], 'object_name': 'ProposalVote'},
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['eusay.Proposal']"}),
            'vote_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['eusay.Vote']"})
        },
        'eusay.report': {
            'Meta': {'object_name': 'Report'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']"})
        },
        'eusay.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'eusay.user': {
            'Meta': {'object_name': 'User'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hasProfile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isModerator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'sid': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "'slug'", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'userStatus': ('django.db.models.fields.CharField', [], {'default': "'User'", 'max_length': '12'})
        },
        'eusay.vote': {
            'Meta': {'object_name': 'Vote'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isVoteUp': ('django.db.models.fields.BooleanField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']"})
        }
    }

    complete_apps = ['eusay']