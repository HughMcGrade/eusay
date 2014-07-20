# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Proposal.slug'
        db.alter_column('eusay_proposal', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'Proposal.slug'
        db.alter_column('eusay_proposal', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50))

    models = {
        'eusay.comment': {
            'Meta': {'object_name': 'Comment'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Proposal']", 'related_name': "'comments'"}),
            'replyTo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Comment']", 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']", 'related_name': "'comments'"})
        },
        'eusay.commentreport': {
            'Meta': {'_ormbases': ['eusay.Report'], 'object_name': 'CommentReport'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Comment']", 'related_name': "'reports'"}),
            'report_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Report']", 'primary_key': 'True'})
        },
        'eusay.commentvote': {
            'Meta': {'_ormbases': ['eusay.Vote'], 'object_name': 'CommentVote'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Comment']", 'related_name': "'votes'"}),
            'vote_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Vote']", 'primary_key': 'True'})
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
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Comment']", 'related_name': "'hideActions'"}),
            'hideaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.HideAction']", 'primary_key': 'True'})
        },
        'eusay.hideproposalaction': {
            'Meta': {'_ormbases': ['eusay.HideAction'], 'object_name': 'HideProposalAction'},
            'hideaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.HideAction']", 'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Proposal']", 'related_name': "'hideActions'"})
        },
        'eusay.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'proposer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']", 'related_name': "'proposed'"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'default': "''"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['eusay.Tag']", 'related_name': "'proposals'"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'eusay.proposalreport': {
            'Meta': {'_ormbases': ['eusay.Report'], 'object_name': 'ProposalReport'},
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Proposal']", 'related_name': "'reports'"}),
            'report_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Report']", 'primary_key': 'True'})
        },
        'eusay.proposalvote': {
            'Meta': {'_ormbases': ['eusay.Vote'], 'object_name': 'ProposalVote'},
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Proposal']", 'related_name': "'votes'"}),
            'vote_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Vote']", 'primary_key': 'True'})
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
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'userStatus': ('django.db.models.fields.CharField', [], {'max_length': '12', 'default': "'User'"})
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