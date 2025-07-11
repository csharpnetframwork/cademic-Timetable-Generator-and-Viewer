import pandas as pd
from datetime import datetime, timedelta
import json
import os
import re

# ===================== Load Configuration =====================
with open('Config.json', 'r') as f:
    config = json.load(f)

input_file = os.path.join(config["input"]["folder"], config["input"]["filename"])
output_file = os.path.join(config["output"]["folder"], config["output"]["filename"])
start_date_str = config["timetable"]["start_date"]
university_start_str = config["timetable"]["university_start_time"]
university_end_str = config["timetable"]["university_end_time"]
lunch_time = config["timetable"]["lunch_time"]
special_rules = config["special_rules"]

start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
uni_start_dt = datetime.strptime(university_start_str, "%H:%M")
uni_end_dt = datetime.strptime(university_end_str, "%H:%M")

total_hours_per_day = (uni_end_dt - uni_start_dt).seconds // 3600

# Lunch
lunch_start, lunch_end = lunch_time.split('-')
lunch_start_dt = datetime.strptime(lunch_start.strip(), "%H:%M")
lunch_end_dt = datetime.strptime(lunch_end.strip(), "%H:%M")
lunch_hours = (lunch_end_dt - lunch_start_dt).seconds // 3600
total_hours_per_day -= lunch_hours

# ===================== Load Input File =====================
try:
    df = pd.read_excel(input_file) if input_file.endswith('.xlsx') else pd.read_csv(input_file)
except Exception as e:
    print(f"❌ File read error: {e}")
    exit()

# ===================== Column Mapping =====================
column_map_raw = {col.strip().lower().replace(" ", "").replace("/", "").replace("_", ""): col for col in df.columns}
expected_mapping = {
    'module': ['subjectmodule', 'subjectmodulecode', 'module'],
    'subject': ['subject', 'subjectmodule'],
    'hours': ['modulehours', 'hours'],
    'faculty': ['faculty'],
    'semester': ['semester'],
    'batch': ['batch']
}

column_mapping = {}
for key, names in expected_mapping.items():
    for name in names:
        for actual, original in column_map_raw.items():
            if name in actual:
                column_mapping[key] = original
                break
        if key in column_mapping:
            break

for col in ['module', 'hours', 'faculty', 'semester', 'batch']:
    if col not in column_mapping:
        print(f"❌ Missing required column: {col}")
        exit()

# ===================== Expand Batches =====================
expanded_modules = []
for rec in df.to_dict(orient="records"):
    batches = re.split(r',|and|&', str(rec[column_mapping['batch']]))
    for batch in batches:
        clean_batch = batch.strip().title()
        if clean_batch:
            rec_copy = rec.copy()
            rec_copy[column_mapping['batch']] = clean_batch
            expanded_modules.append(rec_copy)

# Group by (Batch, Semester)
batch_sem_module_map = {}
for rec in expanded_modules:
    batch = str(rec[column_mapping['batch']]).strip()
    semester = str(rec[column_mapping['semester']]).strip()
    key = (batch, semester)
    batch_sem_module_map.setdefault(key, []).append(rec)

# ===================== Timetable Generation =====================
timetable = []
current_date = start_date
max_days = 1000

for _ in range(max_days):
    if all(not modules for modules in batch_sem_module_map.values()):
        break

    if current_date.weekday() >= 6:
        current_date += timedelta(days=1)
        continue

    day_name = current_date.strftime('%A')
    faculty_today = set()
    batch_times = {key: uni_start_dt for key in batch_sem_module_map}
    remaining_hours = total_hours_per_day
    day_entries = []

    semesters_today = list({sem for _, sem in batch_sem_module_map.keys()})

    # Apply Special Rules First
    for (batch, sem), modules in batch_sem_module_map.items():
        sem_str = str(sem).lower()
        batch_key = (batch, sem)
        start_time = batch_times[batch_key]
        scheduled_hours = 0

        # Skip if no modules left
        if not modules:
            continue

        rules = special_rules.get(sem_str, {})

        # Check Remedial (Saturday)
        if day_name == 'Saturday' and rules.get('Remedial', False):
            faculty = "Remedial Faculty"
            subject = "Remedial Class"
            hours = 8
            end_time = start_time + timedelta(hours=hours)
            entry = {
                'Date': current_date.strftime('%Y-%m-%d'),
                'Day': day_name,
                'Start_Time': start_time.strftime('%I:%M %p'),
                'End_Time': end_time.strftime('%I:%M %p'),
                'Subject': subject,
                'Module': 'RMC',
                'Faculty': faculty,
                'Batch': batch,
                'Semester': sem,
                'Hours_Scheduled': hours,
                'Lunch_Break': lunch_time
            }
            day_entries.append(entry)
            faculty_today.add(faculty)
            continue

        # Check Open Elective
        elective_day = rules.get('Elective_Day', '')
        elective_hours = rules.get('Elective_Hours', 0)

        if elective_day == day_name:
            faculty = "OE Faculty"
            subject = "Open Elective"
            hours = elective_hours
            elective_start = lunch_end_dt
            elective_end = elective_start + timedelta(hours=hours)
            entry = {
                'Date': current_date.strftime('%Y-%m-%d'),
                'Day': day_name,
                'Start_Time': elective_start.strftime('%I:%M %p'),
                'End_Time': elective_end.strftime('%I:%M %p'),
                'Subject': subject,
                'Module': 'OE',
                'Faculty': faculty,
                'Batch': batch,
                'Semester': sem,
                'Hours_Scheduled': hours,
                'Lunch_Break': lunch_time
            }
            day_entries.append(entry)
            faculty_today.add(faculty)
            continue

    # Allocate Remaining Modules
    for (batch, sem), modules in batch_sem_module_map.items():
        if not modules:
            continue

        module = modules[0]
        faculty = str(module[column_mapping['faculty']]).strip()
        subject = str(module.get(column_mapping.get('subject', ''), '')).strip()
        module_code = str(module[column_mapping['module']]).strip()

        if faculty in faculty_today:
            continue

        try:
            hours_left = int(float(module[column_mapping['hours']]))
        except:
            hours_left = 0

        if hours_left <= 0:
            batch_sem_module_map[(batch, sem)].pop(0)
            continue

        available_hours = min(hours_left, remaining_hours)
        start_time = batch_times[(batch, sem)]
        end_time = start_time + timedelta(hours=available_hours)

        entry = {
            'Date': current_date.strftime('%Y-%m-%d'),
            'Day': day_name,
            'Start_Time': start_time.strftime('%I:%M %p'),
            'End_Time': end_time.strftime('%I:%M %p'),
            'Subject': subject,
            'Module': module_code,
            'Faculty': faculty,
            'Batch': batch,
            'Semester': sem,
            'Hours_Scheduled': available_hours,
            'Lunch_Break': lunch_time
        }

        day_entries.append(entry)
        module[column_mapping['hours']] -= available_hours
        batch_times[(batch, sem)] = end_time
        faculty_today.add(faculty)
        remaining_hours -= available_hours

        if module[column_mapping['hours']] <= 0:
            batch_sem_module_map[(batch, sem)].pop(0)

        if remaining_hours <= 0:
            break

    timetable.extend(day_entries)
    current_date += timedelta(days=1)

# ===================== Export =====================
if timetable:
    os.makedirs(config["output"]["folder"], exist_ok=True)
    df_out = pd.DataFrame(timetable).sort_values(by=['Date', 'Start_Time'])
    df_out.to_csv(output_file, index=False)
    print(f"✅ Timetable generated: {os.path.abspath(output_file)}")
else:
    print("❌ No timetable generated.")
