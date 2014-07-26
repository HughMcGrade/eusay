from haystack import indexes
from eusay.models import Proposal

"""
See http://django-haystack.readthedocs.org/en/latest/tutorial.html for details.
"""


class ProposalIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr="title", boost=1.1)
    date = indexes.DateTimeField(model_attr='createdAt')
    comments = indexes.MultiValueField()

    # template in templates/search/indexes/eusay/proposal_text.txt
    text = indexes.CharField(document=True, use_template=True)

    # Use EdgeNgramField to enable autocomplete
    title_auto = indexes.EdgeNgramField(model_attr="title")

    def get_model(self):
        return Proposal

    def prepare_comments(self, object):
        return [comment.text for comment in object.comments.all()]