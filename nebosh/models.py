from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ExamRecord(models.Model):
    """
    A single learner's entry in the assessment register:
    who wrote it, whether it's been submitted/uploaded, and the
    resulting mark and pass/fail outcome.
    """

    class CareOf(models.TextChoices):
        NONE = "", "No relation"
        SAIDALI = "SAIDALI", "Saidali"
        SAHAD = "SAHAD", "Sahad"
        SABIN = "SABIN", "Sabin"
        YOUSUF = "YOUSUF", "Yousuf"
        MARIYAM = "MARIYAM", "Mariyam"
        ADIL = "ADIL", "Adil"

    class Result(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PASS_ = "PASS", "Pass"
        FAIL = "FAIL", "Fail"

    # --- Learner ---
    learner_number = models.CharField(max_length=50, unique=True)
    learner_name = models.CharField(max_length=150)

    # --- Writer ---
    writer = models.CharField(
        max_length=150,
        help_text="Name of the person who wrote/prepared this submission.",
    )
    care_of = models.CharField(
        max_length=20,
        choices=CareOf.choices,
        default=CareOf.NONE,
        blank=True,
        verbose_name="C/O (referred by)",
        help_text="Whether the writer is connected to someone (friend, relative, etc.).",
    )

    # --- Status ---
    submitted = models.BooleanField(default=False)
    uploaded = models.BooleanField(default=False)

    # --- Outcome ---
    mark = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
    )
    result = models.CharField(
        max_length=10,
        choices=Result.choices,
        default=Result.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Exam Record"
        verbose_name_plural = "Exam Records"

    def __str__(self):
        return f"{self.learner_name} ({self.learner_number})"

    def save(self, *args, **kwargs):
        # Keep result consistent with mark when a mark is set but result
        # hasn't been explicitly decided yet — adjust the threshold as needed.
        if self.mark is not None and self.result == self.Result.PENDING:
            self.result = self.Result.PASS_ if self.mark >= 50 else self.Result.FAIL
        super().save(*args, **kwargs)