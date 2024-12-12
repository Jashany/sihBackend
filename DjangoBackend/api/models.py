from django.db import models

class CaseInfo(models.Model):
    caseId = models.CharField(max_length=100, unique=True, verbose_name="Case ID")
    caseTitle = models.CharField(max_length=255, blank=True, null=True, verbose_name="Case Title")

    def __str__(self):
        return self.caseTitle if self.caseTitle else f"Case {self.caseId}"


