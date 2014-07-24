from haystack import indexes
from eusay.models import Proposal

"""
See http://django-haystack.readthedocs.org/en/latest/tutorial.html for details.
"""


class ProposalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)  # in templates/search/indexes/eusay/proposal_text.txt
    date = indexes.DateTimeField(model_attr='createdAt')
    comments = indexes.MultiValueField()

    def get_model(self):
        return Proposal

    def prepare_comments(self, object):
        return [comment.text for comment in object.comments.all()]