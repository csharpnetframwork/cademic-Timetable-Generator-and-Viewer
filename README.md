# 📅 Academic Timetable Generator & Viewer

An automated **Academic Timetable Generator** and **Interactive Web Viewer** designed for **colleges and universities** to create, manage, and visualize class schedules while applying special semester-specific rules.

---

## 🚀 Features

✅ Automatic timetable generation from Excel/CSV  
✅ Special rules for **1st, 3rd, and 5th semesters**  
✅ No faculty overlaps & proper module completion  
✅ Configurable university timings and lunch breaks  
✅ Web interface to **filter, view, and analyze** the schedule  
✅ Built with **Python**, **HTML/CSS**, **JavaScript**

---

## 📂 Folder Structure
academic-timetable-generator-viewer/
│
├── backend/ 
│ ├── timetable_generator.py # 📄 Python timetable generator
│ ├── config.json # ⚙️ Configuration file
│ └── sample_data/ # 📝 Sample Excel/CSV inputs
│
├── frontend/
│ ├── index.html # 🌐 Interactive viewer (HTML/JS)
│ └── assets/ # 🎨 Optional assets
│
├── README.md
└── LICENSE


---

## ⚙️ Configuration (`config.json`)

```json
{
  "input": {
    "folder": "C:/Users/YourName/Path/To/Input",
    "filename": "Timetable.xlsx"
  },
  "output": {
    "folder": "C:/Users/YourName/Path/To/Output",
    "filename": "timetable.csv"
  },
  "timetable": {
    "start_date": "2025-07-07",
    "university_start_time": "09:00",
    "university_end_time": "17:00",
    "lunch_time": "13:00-13:30"
  },
  "special_rules": {
    "1st": {
      "Elective_Day": "Friday",
      "Elective_Hours": 4,
      "Remedial": true,
      "General_Education_Hours": 8
    },
    "3rd": {
      "Elective_Day": "Friday",
      "Elective_Hours": 4,
      "Remedial": true,
      "General_Education_Hours": 8
    },
    "5th": {
      "Elective_Day": "Thursday",
      "Elective_Hours": 3,
      "Remedial": false,
      "General_Education_Hours": 8
    }
  }
}
```
---
📝 Sample Input Data (Excel/CSV Format)
| Subject Module | Subject | Hours | Faculty              | Semester | Batch       |
| -------------- | ------- | ----- | -------------------- | -------- | ----------- |
| FMS1101        | English | 20    | John Doe, Jane Smith | 1st      | FMS Batch 1 |
| FMS2101        | Maths   | 30    | Prof. A, Prof. B     | 3rd      | FMS Batch 2 |

▶️ How to Run (Backend)

1️⃣ Install required Python libraries:
pip install pandas openpyxl
2️⃣ Place your Timetable.xlsx in the specified input folder.
3️⃣ Run the timetable generator:
python timetable_generator.py
4️⃣ The generated timetable will be saved in the output folder as timetable.csv.

🌐 How to Use (Frontend Viewer)
1️⃣ Open the file:
frontend/index.html
2️⃣ Upload the generated timetable CSV or click Load Sample Data.

3️⃣ Apply filters by day, subject, faculty, semester, or batch to view the schedule interactively.

📌 Special Rules Implemented

| Semester | Elective Day | Elective Hours | Remedial Classes | General Education Hours |
| -------- | ------------ | -------------- | ---------------- | ----------------------- |
| 1st      | Friday       | 4 hours        | Saturday (8 hrs) | 8 hours/week            |
| 3rd      | Friday       | 4 hours        | Saturday (8 hrs) | 8 hours/week            |
| 5th      | Thursday     | 3 hours        | ❌ No remedial    | 8 hours/week           |

🔥 Example Code (Python Usage)

from timetable_generator import TimetableGenerator

# Load configuration and generate timetable
generator = TimetableGenerator('backend/config.json')
generator.load_data()
generator.generate_timetable()
generator.save_timetable()


📈 Future Enhancements
✅ Classroom allocation
✅ Faculty leave and availability tracking
✅ Export schedules to PDF or printable formats
✅ Mobile-friendly web viewer

📄 License
MIT License © 2025 Vishal Verma & Contributors


