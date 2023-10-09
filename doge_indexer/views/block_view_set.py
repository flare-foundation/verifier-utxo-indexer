from rest_framework import mixins, viewsets

from doge_indexer.models import DogeBlock
from doge_indexer.serializers import DogeBlockSerializer


class DogeBlockViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    permission_classes = ()
    base_model = DogeBlock
    serializer_class = DogeBlockSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = self.base_model.objects.all()
        return queryset
