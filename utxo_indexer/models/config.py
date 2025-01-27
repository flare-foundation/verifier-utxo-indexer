from django.db import models


class Version(models.Model):
    node_version = models.CharField(max_length=256)
    git_tag = models.CharField(max_length=256)
    git_hash = models.CharField(max_length=40)
    build_date = models.PositiveIntegerField()
    num_confirmations = models.PositiveIntegerField()
    history_seconds = models.PositiveIntegerField()

    def __str__(self):
        node_configurations = (
            "Node configurations:\n"
            + f"node_version: {self.node_version}\n"
            + f"git_tag: {self.git_tag}\n"
            + f"git_hash: {self.git_hash}\n"
            + f"build_date: {self.build_date}\n"
            + f"num_confirmations: {self.num_confirmations}\n"
            + f"history_seconds: {self.history_seconds}\n"
        )
        return node_configurations
