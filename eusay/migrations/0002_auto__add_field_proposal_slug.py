# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Proposal.slug'
        db.add_column('eusay_proposal', 'slug',
                      self.gf('django.db.models.fields.SlugField')(max_length=50, default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Proposal.slug'
        db.delete_column('eusay_proposal', 'slug')


    models = {
        'eusay.comment': {
            'Meta': {'object_name': 'Comment'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['eusay.Proposal']"}),
            'replyTo': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['eusay.Comment']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['eusay.User']"})
        },
        'eusay.commentreport': {
            'Meta': {'object_name': 'CommentReport', '_ormbases': ['eusay.Report']},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': "orm['eusay.Comment']"}),
            'report_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Report']", 'primary_key': 'True'})
        },
        'eusay.commentvote': {
            'Meta': {'object_name': 'CommentVote', '_ormbases': ['eusay.Vote']},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['eusay.Comment']"}),
            'vote_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Vote']", 'primary_key': 'True'})
        },
        'eusay.hideaction': {
            'Meta': {'object_name': 'HideAction'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        'eusay.hidecommentaction': {
            'Meta': {'object_name': 'HideCommentAction', '_ormbases': ['eusay.HideAction']},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hideActions'", 'to': "orm['eusay.Comment']"}),
            'hideaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.HideAction']", 'primary_key': 'True'})
        },
        'eusay.hideproposalaction': {
            'Meta': {'object_name': 'HideProposalAction', '_ormbases': ['eusay.HideAction']},
            'hideaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.HideAction']", 'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hideActions'", 'to': "orm['eusay.Proposal']"})
        },
        'eusay.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'proposer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proposed'", 'to': "orm['eusay.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'default': "''"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'proposals'", 'symmetrical': 'False', 'to': "orm['eusay.Tag']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'eusay.proposalreport': {
            'Meta': {'object_name': 'ProposalReport', '_ormbases': ['eusay.Report']},
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reports'", 'to': "orm['eusay.Proposal']"}),
            'report_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Report']", 'primary_key': 'True'})
        },
        'eusay.proposalvote': {
            'Meta': {'object_name': 'ProposalVote', '_ormbases': ['eusay.Vote']},
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['eusay.Proposal']"}),
            'vote_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['eusay.Vote']", 'primary_key': 'True'})
        },
        'eusay.report': {
            'Meta': {'object_name': 'Report'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'userStatus': ('django.db.models.fields.CharField', [], {'max_length': '12', 'default': "'User'"})
        },
        'eusay.vote': {
            'Meta': {'object_name': 'Vote'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isVoteUp': ('django.db.models.fields.BooleanField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']"})
        }
    }

    complete_apps = ['eusay']