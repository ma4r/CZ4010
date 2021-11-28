from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError,APIException,PermissionDenied
from privateSharing.models import PrivateSharingModel
from django.db.models import Q
from dataSet.models import DataSetModel
from . import serializers
from .psi_service import do_psi
import base64
# import pdb
# pdb.set_trace()


class PrivateSharingView(viewsets.ModelViewSet,LoginRequiredMixin):
    http_method_names = ['get', 'post','patch']


    def get_queryset(self):
        get =  PrivateSharingModel.objects.filter(Q(client1= self.request.user)
                                                  |Q(client2=self.request.user))

        if self.action == "update" or self.action == "partial_update":
            return PrivateSharingModel.objects.filter(status="WAITING")
            # return get
        else:
            return get

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreatePrivateSharingSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return  serializers.UpdateSessionSerializer
        else:
            return serializers.PrivateSharingSerializer

    def create(self, request:Request, *args, **kwargs):
        user = request.user
        dataId = request.data["data"]


        try:
            DataSetModel.objects.filter(user=user).get(pk = dataId)
        except:
            raise ValidationError({"data":"Data not found"})

        return super(PrivateSharingView,self).create(request,*args,**kwargs)


    def partial_update(self, request, *args, **kwargs):

        pk = kwargs['pk']
        model = PrivateSharingModel.objects.get(pk=pk)
        if model.status == "STARTED":
            raise ValidationError({"Id": "PSI in progress"})

        userI = request.user

        dataId = request.data["data"]
        decoded = base64.b64decode(dataId)
        request.data.update({"client2": userI.id,
                             "enc_data": decoded,
                             "status": "STARTED",})


        response = super(PrivateSharingView, self).partial_update(request, *args, **kwargs)

        # try:
        self.start_psi(pk,request.data["n"])
        # except Exception as e:
        #     raise APIException("PSI FAILED TO START")


        return response

    def start_psi(self,pk,n):
        session = PrivateSharingModel.objects.get(pk=pk)
        data = session.data.data['data']
        enc_data = session.enc_data

        setup,response = do_psi(data,enc_data,n)
        encoded_resp = base64.b64encode(response).decode("ascii")
        encoded_setup = base64.b64encode(setup).decode("ascii")

        session.status = "FINISHED"
        session.res = {"setup":encoded_setup,
                       "response":encoded_resp}

        session.save()
        return

    def retrieve(self, request, *args, **kwargs):
        response  = super(PrivateSharingView,self).retrieve(request,*args,*kwargs)

        if request.user.id != response.data["client2"]:
            response.data.pop("res")

        return response


    def list(self, request, *args, **kwargs):
        response  = super(PrivateSharingView,self).list(request,*args,*kwargs)

        if len(response.data) == 0:
            return response

        for sess in response.data:
            if sess["client2"] != request.user.id:
                sess.pop("res")
        return response

