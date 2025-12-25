from django.db import models
from django.conf import settings


class Drug(models.Model):
    # 의약품 이름
    name = models.CharField(max_length=100)

    # 효능 / 효과
    effect = models.TextField(blank=True, null=True)

    # 용법 / 용량
    usage = models.TextField(blank=True, null=True)

    # 주의사항
    warning = models.TextField(blank=True, null=True)

    # 외부 이미지 URL (API 제공 이미지 등)
    image_url = models.URLField(blank=True, null=True)

    # 직접 업로드한 이미지
    image = models.ImageField(
        upload_to='drugs/',
        blank=True,
        null=True
    )

    # 조회수
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        # 관리자/쉘에서 의약품 이름으로 표시
        return self.name


class DrugComment(models.Model):
    # 어떤 의약품에 대한 댓글인지
    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # 댓글 작성자
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # 댓글 내용
    content = models.TextField()

    # 사용자 별점 (1~5점, 선택)
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        null=True,
        blank=True
    )

    # 댓글 작성 시각
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # 의약품 이름 - 작성자 형태로 표시
        return f'{self.drug.name} - {self.author}'


# ==================================================
# ⭐ 의약품 사용자 반응 모델 (도움됐어요 / 도움 안 됐어요)
# ==================================================
class DrugReaction(models.Model):
    # 반응 대상 의약품
    drug = models.ForeignKey(
        Drug,
        related_name='reactions',
        on_delete=models.CASCADE
    )

    # 반응을 남긴 사용자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # 사용자 반응 타입
    reaction = models.CharField(
        max_length=10,
        choices=[('helpful', '도움됨'), ('unhelpful', '도움 안됨')]
    )

    # 반응 생성 시각
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 한 사용자는 하나의 의약품에 하나의 반응만 가능
        unique_together = ('user', 'drug')


# ==================================================
# ⭐ 의약품 AI 요약 모델
# ==================================================
class DrugAiSummary(models.Model):
    # 의약품과 1:1 관계
    drug = models.OneToOneField(
        Drug,
        on_delete=models.CASCADE,
        related_name="ai_summary"
    )

    # 한 줄 요약
    one_liner = models.CharField(max_length=255, blank=True, default="")

    # 쉬운 설명 (일반인 대상)
    easy_explain = models.TextField(blank=True, default="")

    # 핵심 포인트 (리스트 형태)
    key_points = models.JSONField(default=list, blank=True)

    # 주의사항 요약 (리스트 형태)
    cautions = models.JSONField(default=list, blank=True)

    # 병원에 가야 하는 경우 (리스트 형태)
    when_to_see_doctor = models.JSONField(default=list, blank=True)

    # 마지막 업데이트 시각
    updated_at = models.DateTimeField(auto_now=True)
