from django.db import models
from django.contrib.auth import get_user_model
from dataSet.models import DataSetModel
from django.utils.translation import gettext_lazy as _

import uuid
from json import JSONEncoder,JSONDecoder

class PrivateSharingModel(models.Model):
    class status(models.TextChoices):
        WAITING = 'WAITING',_('Waiting for other party')
        STARTED = 'STARTED',_('PSI started')
        FINISHED = 'FINISHED',_('PSI Finished')
        ABORTED = 'ABORTED', _('PSI Session Aborted')

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    client1 = models.ForeignKey(get_user_model(),
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="user_id1")
    client2 = models.ForeignKey(get_user_model(),
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="user_id2")
    data = models.ForeignKey(DataSetModel,
                              on_delete=models.RESTRICT,
                              null=True)
    enc_data = models.BinaryField(null=True,max_length=2000,editable=True )
    status = models.CharField(max_length=10,
                              choices=status.choices,
                              default=status.WAITING,
    )
    res = models.JSONField(encoder=JSONEncoder,decoder=JSONDecoder,null=True)




