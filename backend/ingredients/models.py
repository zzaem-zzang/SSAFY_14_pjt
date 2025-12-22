from django.db import models
from django.conf import settings

class Drug(models.Model):
    name = models.CharField(max_length=100)
    effect = models.TextField(blank=True)
    usage = models.TextField(blank=True)
    warning = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Symptom(models.Model):
    name = models.CharField(max_length=50)
    drugs = models.ManyToManyField(
        'Drug',               
        related_name='symptoms'
    )

    def __str__(self):
        return self.name



class DrugComment(models.Model):
    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.drug.name} - {self.author}'


# ==================================================
# ⭐ 의약품 사용자 반응 모델 (도움됐어요 / 도움 안 됐어요)
# ==================================================
class DrugReaction(models.Model):
    drug = models.ForeignKey(
        Drug,
        related_name='reactions',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    reaction = models.CharField(
        max_length=10,
        choices=[('helpful', '도움됨'), ('unhelpful', '도움 안됨')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'drug')
