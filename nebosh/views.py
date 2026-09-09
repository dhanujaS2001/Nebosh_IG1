from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.shortcuts import redirect, render, get_object_or_404
from nebosh.models import ExamRecord


def dashboard(request):
    care_of_applied = "care_of" in request.GET
    care_of_filter = request.GET.get("care_of", "")

    search_query = request.GET.get("q", "").strip()

    # Base queryset respects the OTHER active filters (care_of, search)
    # but not the submitted filter itself — this is what the submitted-status
    # counts are calculated against, so the numbers on the cards stay accurate
    # no matter which submitted-status card is currently selected.
    base_qs = ExamRecord.objects.all().order_by("id")
    if care_of_applied:
        base_qs = base_qs.filter(care_of=care_of_filter)
    if search_query:
        base_qs = base_qs.filter(
            Q(learner_name__icontains=search_query)
            | Q(learner_number__icontains=search_query)
            | Q(writer__icontains=search_query)
        )

    submitted_filter = request.GET.get("submitted", "")
    exam_records = base_qs
    if submitted_filter == "yes":
        exam_records = exam_records.filter(submitted=True)
    elif submitted_filter == "no":
        exam_records = exam_records.filter(submitted=False)

    submitted_count = base_qs.filter(submitted=True).count()
    not_submitted_count = base_qs.filter(submitted=False).count()
    base_total = base_qs.count()

    care_of = ExamRecord.CareOf.choices
    raw_counts = dict(
        ExamRecord.objects.values_list("care_of").annotate(count=Count("id"))
    )
    care_of_counts = [
        {"value": value, "label": label, "count": raw_counts.get(value, 0)}
        for value, label in ExamRecord.CareOf.choices
    ]
    total_count = ExamRecord.objects.count()

    return render(
        request,
        "dashboard.html",
        {
            "exam_records": exam_records,
            "care_of": care_of,
            "selected_care_of": care_of_filter,
            "care_of_applied": care_of_applied,
            "care_of_counts": care_of_counts,
            "total_count": total_count,
            "search_query": search_query,
            "selected_submitted": submitted_filter,
            "submitted_applied": submitted_filter != "",
            "submitted_count": submitted_count,
            "not_submitted_count": not_submitted_count,
            "base_total": base_total,
        },
    )
def add_record(request):
    if request.method == "POST":
        learner_number = request.POST.get("learner_number")
        learner_name = request.POST.get("learner_name")
        writer = request.POST.get("writer")
        care_of = request.POST.get("care_of")
        submitted = request.POST.get("submitted") == "on"
        print("Submitted:", submitted)  # Debugging line
        uploaded = request.POST.get("uploaded") == "on"
        print("Uploaded:", uploaded)  # Debugging line

        ExamRecord.objects.create(
            learner_number=learner_number,
            learner_name=learner_name,
            writer=writer,
            care_of=care_of,
            submitted=submitted,
            uploaded=uploaded,
            mark= None,
            result=ExamRecord.Result.PENDING,
            )

    return redirect("dashboard")

def update_record(request, record_id):
    if request.method == "POST":
        record = get_object_or_404(ExamRecord, id=record_id)

        record.learner_number = request.POST.get("learner_number")
        record.learner_name = request.POST.get("learner_name")
        record.writer = request.POST.get("writer")
        record.care_of = request.POST.get("care_of")
        record.submitted = request.POST.get("submitted") == "on"
        record.uploaded = request.POST.get("uploaded") == "on"

        mark = request.POST.get("mark")
        record.mark = int(mark) if mark not in (None, "") else None
        record.result = ExamRecord.Result.PENDING

        record.save()

    return redirect("dashboard")

def delete_record(request, record_id):
    if request.method == "POST":
        record = get_object_or_404(ExamRecord, id=record_id)
        record.delete()

    return redirect("dashboard")

import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST


@require_POST
def inline_update(request, record_id):
    record = get_object_or_404(ExamRecord, id=record_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    field = data.get("field")
    value = data.get("value")
    

    if field == "learner_name":
        value = (value or "").strip()
        if not value:
            return JsonResponse({"error": "Name cannot be empty"}, status=400)
        record.learner_name = value
    
    elif field == "writer":
        value = (value or "").strip()
        if not value:
            return JsonResponse({"error": "Writer cannot be empty"}, status=400)
        record.writer = value
        
    elif field == "learner_number":
        value = (value or "").strip()
        if not value:
            return JsonResponse({"error": "Learner number cannot be empty"}, status=400)
        record.learner_number = value

    elif field in ("submitted", "uploaded"):
        setattr(record, field, bool(value))

    else:
        return HttpResponseBadRequest("Invalid field")

    record.save()

    return JsonResponse({
        "success": True,
        "field": field,
        "value": getattr(record, field),
        "result": record.result,
    })