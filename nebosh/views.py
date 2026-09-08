from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.shortcuts import redirect, render, get_object_or_404
from nebosh.models import ExamRecord

# Create your views here.

def dashboard(request):
    exam_records = ExamRecord.objects.all()
    care_of_applied = "care_of" in request.GET
    care_of_filter = request.GET.get("care_of", "")
    if care_of_applied:
        exam_records = exam_records.filter(care_of=care_of_filter)
    
    search_query = request.GET.get("q", "").strip()
    if search_query:
        exam_records = exam_records.filter(
            Q(learner_name__icontains=search_query)
            | Q(learner_number__icontains=search_query)
            | Q(writer__icontains=search_query)
        )
    care_of = ExamRecord.CareOf.choices
    
    # Count of writers (records) grouped by care_of, in a stable, labeled order
    care_of_labels = dict(ExamRecord.CareOf.choices)
    raw_counts = dict(
        ExamRecord.objects.values_list("care_of").annotate(count=Count("id"))
    )
    care_of_counts = [
        {
            "value": value,
            "label": label,
            "count": raw_counts.get(value, 0),
        }
        for value, label in ExamRecord.CareOf.choices
    ]
    
    return render(request, "dashboard.html", {"exam_records": exam_records, "care_of": care_of,"selected_care_of": care_of_filter, "care_of_applied": care_of_applied,"care_of_counts": care_of_counts,"search_query": search_query})

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