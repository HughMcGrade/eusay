from haystack import indexes
from eusay.models import Proposal

"""
See http://django-haystack.readthedocs.org/en/latest/tutorial.html for details.
"""


class ProposalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)  # in templates/search/indexes/eusay/proposal_text.txt
    date = indexes.DateTimeField(model_attr='createdAt')
    # TODO: decide whether users can search by proposer. if yes, add the following line:
    # user = indexes.CharField(model_attr='proposer')

    # TODO: decide whether a proposal's comments should be included in its index.

    # TODO: include tags/category fields in search template.

    def get_model(self):
        return Proposal