# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Comment'
        db.create_table('eusay_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('lastModified', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.User'], related_name='comments')),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Proposal'], related_name='comments')),
            ('replyTo', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['eusay.Comment'])),
        ))
        db.send_create_signal('eusay', ['Comment'])

        # Adding model 'Vote'
        db.create_table('eusay_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('isVoteUp', self.gf('django.db.models.fields.BooleanField')()),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.User'])),
        ))
        db.send_create_signal('eusay', ['Vote'])

        # Adding model 'Tag'
        db.create_table('eusay_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('eusay', ['Tag'])

        # Adding model 'Proposal'
        db.create_table('eusay_proposal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('proposer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.User'], related_name='proposed')),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True, auto_now_add=True)),
            ('lastModified', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
        ))
        db.send_create_signal('eusay', ['Proposal'])

        # Adding M2M table for field tags on 'Proposal'
        m2m_table_name = db.shorten_name('eusay_proposal_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['eusay.proposal'], null=False)),
            ('tag', models.ForeignKey(orm['eusay.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['proposal_id', 'tag_id'])

        # Adding model 'ProposalVote'
        db.create_table('eusay_proposalvote', (
            ('vote_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['eusay.Vote'], primary_key=True)),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Proposal'], related_name='votes')),
        ))
        db.send_create_signal('eusay', ['ProposalVote'])

        # Adding model 'CommentVote'
        db.create_table('eusay_commentvote', (
            ('vote_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['eusay.Vote'], primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Comment'], related_name='votes')),
        ))
        db.send_create_signal('eusay', ['CommentVote'])

        # Adding model 'User'
        db.create_table('eusay_user', (
            ('sid', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('userStatus', self.gf('django.db.models.fields.CharField')(default='User', max_length=12)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('isModerator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hasProfile', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('eusay', ['User'])

        # Adding model 'HideAction'
        db.create_table('eusay_hideaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('moderator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.User'])),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal('eusay', ['HideAction'])

        # Adding model 'HideCommentAction'
        db.create_table('eusay_hidecommentaction', (
            ('hideaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['eusay.HideAction'], primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Comment'], related_name='hideActions')),
        ))
        db.send_create_signal('eusay', ['HideCommentAction'])

        # Adding model 'HideProposalAction'
        db.create_table('eusay_hideproposalaction', (
            ('hideaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['eusay.HideAction'], primary_key=True)),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Proposal'], related_name='hideActions')),
        ))
        db.send_create_signal('eusay', ['HideProposalAction'])

        # Adding model 'Report'
        db.create_table('eusay_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reporter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.User'])),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal('eusay', ['Report'])

        # Adding model 'CommentReport'
        db.create_table('eusay_commentreport', (
            ('report_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['eusay.Report'], primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Comment'], related_name='reports')),
        ))
        db.send_create_signal('eusay', ['CommentReport'])

        # Adding model 'ProposalReport'
        db.create_table('eusay_proposalreport', (
            ('report_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['eusay.Report'], primary_key=True)),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eusay.Proposal'], related_name='reports')),
        ))
        db.send_create_signal('eusay', ['ProposalReport'])


    def backwards(self, orm):
        # Deleting model 'Comment'
        db.delete_table('eusay_comment')

        # Deleting model 'Vote'
        db.delete_table('eusay_vote')

        # Deleting model 'Tag'
        db.delete_table('eusay_tag')

        # Deleting model 'Proposal'
        db.delete_table('eusay_proposal')

        # Removing M2M table for field tags on 'Proposal'
        db.delete_table(db.shorten_name('eusay_proposal_tags'))

        # Deleting model 'ProposalVote'
        db.delete_table('eusay_proposalvote')

        # Deleting model 'CommentVote'
        db.delete_table('eusay_commentvote')

        # Deleting model 'User'
        db.delete_table('eusay_user')

        # Deleting model 'HideAction'
        db.delete_table('eusay_hideaction')

        # Deleting model 'HideCommentAction'
        db.delete_table('eusay_hidecommentaction')

        # Deleting model 'HideProposalAction'
        db.delete_table('eusay_hideproposalaction')

        # Deleting model 'Report'
        db.delete_table('eusay_report')

        # Deleting model 'CommentReport'
        db.delete_table('eusay_commentreport')

        # Deleting model 'ProposalReport'
        db.delete_table('eusay_proposalreport')


    models = {
        'eusay.comment': {
            'Meta': {'object_name': 'Comment'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.Proposal']", 'related_name': "'comments'"}),
            'replyTo': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['eusay.Comment']"}),
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
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastModified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'proposer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eusay.User']", 'related_name': "'proposed'"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['eusay.Tag']", 'symmetrical': 'False', 'related_name': "'proposals'"}),
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
            'sid': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '20'}),
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