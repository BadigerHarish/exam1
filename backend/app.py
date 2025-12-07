from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
import os

# Define the base directory for frontend files (project root)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PUBLIC_DIR = os.path.join(FRONTEND_DIR, 'public')

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='/public')
CORS(app)

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "exam_hall_management"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
teachers_collection = db["teachers"]
students_collection = db["students"]
exams_collection = db["exams"]
rooms_collection = db["rooms"]
subjects_collection = db["subjects"]
allocations_collection = db["allocations"]
student_allocations_collection = db["student_allocations"]

# --- Frontend Page Routes ---
@app.route('/')
def serve_root():
    return send_from_directory(FRONTEND_DIR, 'register.html')

@app.route('/register')
def serve_register_page():
    return send_from_directory(FRONTEND_DIR, 'register.html')

@app.route('/login')
def serve_login_page():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/forgot-password')
def serve_forgot_password_page():
    return send_from_directory(PUBLIC_DIR, 'forgot-password.html')

# Routes for pages in public/ (served via Flask static folder)
@app.route('/home')
def serve_home():
    return send_from_directory(app.static_folder, 'home.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/add-teacher')
def serve_add_teacher():
    return send_from_directory(app.static_folder, 'add-teacher.html')

@app.route('/view-teacher')
def serve_view_teacher():
    return send_from_directory(app.static_folder, 'view-teacher.html')

@app.route('/add-student')
def serve_add_student():
    return send_from_directory(app.static_folder, 'add-student.html')

@app.route('/view-student')
def serve_view_student():
    return send_from_directory(app.static_folder, 'view-student.html')

@app.route('/add-exam')
def serve_add_exam():
    return send_from_directory(app.static_folder, 'add-exam.html')

@app.route('/view-exam')
def serve_view_exam():
    return send_from_directory(app.static_folder, 'view-exam.html')

@app.route('/add-room')
def serve_add_room():
    return send_from_directory(app.static_folder, 'add-room.html')

@app.route('/view-room')
def serve_view_room():
    return send_from_directory(app.static_folder, 'view-room.html')

@app.route('/add-subject')
def serve_add_subject():
    return send_from_directory(app.static_folder, 'add-subject.html')

@app.route('/view-subject')
def serve_view_subject():
    return send_from_directory(app.static_folder, 'view-subject.html')

@app.route('/student-allocations')
def serve_student_allocations():
    return send_from_directory(app.static_folder, 'student-allocations.html')

@app.route('/view-student-allocations')
def serve_view_student_allocations():
    return send_from_directory(app.static_folder, 'view-student-allocations.html')

@app.route('/view-allocations')
def serve_view_allocations():
    return send_from_directory(app.static_folder, 'view-allocations.html')

@app.route('/add-allocations')
def serve_add_allocations():
    return send_from_directory(app.static_folder, 'add-allocations.html')

@app.route('/allocations/student-home')
def serve_student_home():
    return send_from_directory(PUBLIC_DIR, 'student-home.html')

@app.route('/allocations/teacher-home')
def serve_teacher_home():
    return send_from_directory(PUBLIC_DIR, 'teacher-home.html')

# --- Static File Serving (for CSS, JS, images, etc.) ---
# This route serves files from the 'public' directory as /static/<filename>
# Flask's static_folder already handles this, so this route is simplified.
@app.route('/static/<path:filename>')
def serve_static_from_public(filename):
    return send_from_directory(app.static_folder, filename)

# This route serves files directly from the root of the project as /root_static/<filename>
# This is for assets like register.html's own css/js if they are directly in the root
@app.route('/root_static/<path:filename>')
def serve_static_from_root(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_type = data.get('userType')
    user_id = data.get('userId')
    password = data.get('password')

    if not all([user_type, user_id, password]):
        return jsonify({'message': 'Missing credentials'}), 400

    user = users_collection.find_one({'type': user_type, 'id': user_id, 'password': password})

    if user:
        user['_id'] = str(user['_id'])
        return jsonify({'message': 'Login successful', 'user': user}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# --- User Registration Endpoint ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    user_id = data.get('id') # Renamed from 'id' to 'user_id' to avoid conflict with Mongo _id
    password = data.get('password')
    user_type = data.get('type')

    if not all([name, user_id, password, user_type]):
        return jsonify({'message': 'Missing registration details'}), 400

    if users_collection.find_one({'id': user_id, 'type': user_type}):
        return jsonify({'message': f'{user_type.capitalize()} with ID {user_id} already exists.'}), 409

    new_user = {
        'name': name,
        'id': user_id,
        'password': password, # In a real app, hash this password!
        'type': user_type
    }
    users_collection.insert_one(new_user)
    new_user['_id'] = str(new_user['_id'])

    # If it's a student or teacher, also add them to their respective collections
    if user_type == 'student':
        if not students_collection.find_one({'id': user_id}):
            students_collection.insert_one({
                'id': user_id,
                'name': name,
                'email': data.get('email', ''), # Get email from data or default to empty string
                'phone': data.get('phone', ''), # Get phone from data or default to empty string
                'enrollment_date': data.get('enrollment_date', ''), # Add enrollment_date (if available, though not in frontend yet)
                'photo': data.get('photo', ''), # Get photo from data or default to empty string
                'semester': data.get('semester', ''), # Get semester from data or default to empty string
                'branch': data.get('branch', ''), # Get branch from data or default to empty string
                'course': data.get('course', '') # Get course from data or default to empty string
            })
    elif user_type == 'teacher':
        if not teachers_collection.find_one({'id': user_id}):
            teachers_collection.insert_one({
                'id': user_id,
                'name': name,
                'title': data.get('title', ''), # Get title from data or default to empty string
                'email': data.get('email', ''), # Get email from data or default to empty string
                'phone': data.get('phone', ''), # Get phone from data or default to empty string
                'photo': data.get('photo', '')  # Get photo from data or default to empty string
            })

    return jsonify({'message': 'Registration successful', 'user': new_user}), 201

# --- CRUD Endpoints for Teachers ---
@app.route('/teachers', methods=['POST'])
def add_teacher():
    data = request.get_json()
    if not all([data.get('name'), data.get('email'), data.get('phone'), data.get('title'), data.get('id')]):
        return jsonify({'message': 'Missing required teacher details (name, email, phone, title, id)'}), 400

    teacher_id = data.get('id')
    if teachers_collection.find_one({'id': teacher_id}):
        return jsonify({'message': f'Teacher with ID {teacher_id} already exists.'}), 409

    new_teacher = {
        'id': teacher_id,
        'title': data['title'],
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'photo': data.get('photo', '') # Photo is optional
    }
    teachers_collection.insert_one(new_teacher)
    new_teacher['_id'] = str(new_teacher['_id'])
    return jsonify({'message': 'Teacher added successfully', 'teacher': new_teacher}), 201

@app.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = []
    for teacher in teachers_collection.find():
        teacher['_id'] = str(teacher['_id'])
        teachers.append(teacher)
    return jsonify(teachers), 200

@app.route('/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = teachers_collection.find_one({'id': teacher_id})
    if teacher:
        teacher['_id'] = str(teacher['_id'])
        return jsonify(teacher), 200
    return jsonify({'message': 'Teacher not found'}), 404

@app.route('/teachers/<teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    data = request.get_json()
    updated_fields = {}
    
    # Check if a new ID is provided and if it's different from the current ID
    new_id = data.get('id')
    if new_id and new_id != teacher_id:
        # Check if the new ID already exists for another teacher
        if teachers_collection.find_one({'id': new_id}):
            return jsonify({'message': f'Teacher with ID {new_id} already exists.'}), 409
        updated_fields['id'] = new_id

    if 'title' in data: updated_fields['title'] = data['title']
    if 'name' in data: updated_fields['name'] = data['name']
    if 'email' in data: updated_fields['email'] = data['email']
    if 'phone' in data: updated_fields['phone'] = data['phone']
    if 'photo' in data: updated_fields['photo'] = data['photo']

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    result = teachers_collection.update_one({'id': teacher_id}, {'$set': updated_fields})
    if result.matched_count:
        # If the ID was updated, use the new ID to find the teacher
        if 'id' in updated_fields:
            teacher_id = updated_fields['id']
        updated_teacher = teachers_collection.find_one({'id': teacher_id})
        updated_teacher['_id'] = str(updated_teacher['_id'])
        return jsonify({'message': 'Teacher updated successfully', 'teacher': updated_teacher}), 200
    return jsonify({'message': 'Teacher not found'}), 404

@app.route('/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    result = teachers_collection.delete_one({'id': teacher_id})
    if result.deleted_count:
        return jsonify({'message': 'Teacher deleted successfully'}), 200
    return jsonify({'message': 'Teacher not found'}), 404

@app.route('/teachers/reset-password', methods=['POST'])
def reset_teacher_password():
    data = request.get_json()
    teacher_id = data.get('id')
    new_password = data.get('new_password')

    if not all([teacher_id, new_password]):
        return jsonify({'message': 'Missing teacher ID or new password'}), 400

    # Update password in teachers collection
    teacher_result = teachers_collection.update_one(
        {'id': teacher_id},
        {'$set': {'password': new_password}}
    )

    # Update password in users collection
    user_result = users_collection.update_one(
        {'id': teacher_id, 'type': 'teacher'},
        {'$set': {'password': new_password}}
    )

    if teacher_result.matched_count > 0 or user_result.matched_count > 0:
        return jsonify({'message': 'Teacher password reset successfully'}), 200
    else:
        return jsonify({'message': 'Teacher not found'}), 404

# --- CRUD Endpoints for Students ---
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not all([data.get('name'), data.get('email'), data.get('phone'), data.get('enrollment_date'),
                data.get('semester'), data.get('branch'), data.get('course'), data.get('subject')]):
        return jsonify({'message': 'Missing required student details (name, email, phone, enrollment date, semester, branch, course, subject)'}), 400

    # Generate a unique student ID on the backend
    while True:
        student_id = "S" + str(random.randint(1000, 9999))
        if not students_collection.find_one({'id': student_id}):
            break

    new_student = {
        'id': student_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'enrollment_date': data['enrollment_date'],
        'photo': data.get('photo', ''), # Photo is optional
        'password': 'student123', # Default password for new students
        'type': 'student', # Default type for new students
        'semester': data['semester'],
        'branch': data['branch'],
        'course': data['course'],
        'subject': data['subject'] # Add subject to new_student
    }
    students_collection.insert_one(new_student)
    new_student['_id'] = str(new_student['_id'])

    # Also add this student to the users collection for login purposes
    users_collection.insert_one({
        'id': student_id,
        'name': data['name'],
        'password': 'student123', # Keep in sync with new_student password
        'type': 'student'
    })

    return jsonify({'message': 'Student added successfully', 'student': new_student}), 201

@app.route('/students', methods=['GET'])
def get_students():
    students = []
    for student in students_collection.find():
        student['_id'] = str(student['_id'])
        students.append(student)
    return jsonify(students), 200

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = students_collection.find_one({'id': student_id})
    if student:
        student['_id'] = str(student['_id'])
        return jsonify(student), 200
    return jsonify({'message': 'Student not found'}), 404

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    updated_fields = {}
    if 'name' in data: updated_fields['name'] = data['name']
    if 'email' in data: updated_fields['email'] = data['email']
    if 'phone' in data: updated_fields['phone'] = data['phone']
    if 'enrollment_date' in data: updated_fields['enrollment_date'] = data['enrollment_date']
    if 'photo' in data: updated_fields['photo'] = data['photo']
    if 'semester' in data: updated_fields['semester'] = data['semester']
    if 'branch' in data: updated_fields['branch'] = data['branch']
    if 'course' in data: updated_fields['course'] = data['course']
    if 'subject' in data: updated_fields['subject'] = data['subject'] # Add subject to updated_fields

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    result = students_collection.update_one({'id': student_id}, {'$set': updated_fields})
    if result.matched_count:
        updated_student = students_collection.find_one({'id': student_id})
        updated_student['_id'] = str(updated_student['_id'])
        return jsonify({'message': 'Student updated successfully', 'student': updated_student}), 200
    return jsonify({'message': 'Student not found'}), 404

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    # Also delete from users collection
    users_collection.delete_one({'id': student_id, 'type': 'student'})
    result = students_collection.delete_one({'id': student_id})
    if result.deleted_count:
        return jsonify({'message': 'Student deleted successfully'}), 200
    return jsonify({'message': 'Student not found'}), 404

@app.route('/students/reset-password', methods=['POST'])
def reset_student_password():
    data = request.get_json()
    student_id = data.get('id')
    new_password = data.get('new_password')

    if not all([student_id, new_password]):
        return jsonify({'message': 'Missing student ID or new password'}), 400

    # Update password in students collection
    student_result = students_collection.update_one(
        {'id': student_id},
        {'$set': {'password': new_password}}
    )

    # Update password in users collection
    user_result = users_collection.update_one(
        {'id': student_id, 'type': 'student'},
        {'$set': {'password': new_password}}
    )

    if student_result.matched_count > 0 or user_result.matched_count > 0:
        return jsonify({'message': 'Student password reset successfully'}), 200
    else:
        return jsonify({'message': 'Student not found'}), 404

# --- CRUD Endpoints for Exams ---
@app.route('/exams', methods=['POST'])
def add_exam():
    data = request.get_json()
    required_fields = ['exam_name', 'exam_date', 'exam_time', 'semester', 'branch', 'course', 'subject']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing exam details'}), 400

    if exams_collection.find_one({'exam_name': data['exam_name'], 'exam_date': data['exam_date'], 'exam_time': data['exam_time']}):
        return jsonify({'message': 'Exam with this name, date, and time already exists'}), 409

    new_exam = {
        'exam_name': data['exam_name'],
        'exam_date': data['exam_date'],
        'exam_time': data['exam_time'],
        'semester': data['semester'],
        'branch': data['branch'],
        'course': data['course'],
        'subject': data['subject']
    }
    exams_collection.insert_one(new_exam)
    new_exam['_id'] = str(new_exam['_id'])
    return jsonify({'message': 'Exam added successfully', 'exam': new_exam}), 201

@app.route('/exams', methods=['GET'])
def get_exams():
    exams = []
    for exam in exams_collection.find():
        exam['_id'] = str(exam['_id'])
        exams.append(exam)
    return jsonify(exams), 200

@app.route('/exams/<exam_id>', methods=['GET'])
def get_exam(exam_id):
    try:
        exam = exams_collection.find_one({'_id': ObjectId(exam_id)})
    except:
        return jsonify({'message': 'Invalid Exam ID format'}), 400
    if exam:
        exam['_id'] = str(exam['_id'])
        return jsonify(exam), 200
    return jsonify({'message': 'Exam not found'}), 404

@app.route('/exams/<exam_id>', methods=['PUT'])
def update_exam(exam_id):
    data = request.get_json()
    updated_fields = {}
    if 'exam_name' in data: updated_fields['exam_name'] = data['exam_name']
    if 'exam_date' in data: updated_fields['exam_date'] = data['exam_date']
    if 'exam_time' in data: updated_fields['exam_time'] = data['exam_time']
    if 'semester' in data: updated_fields['semester'] = data['semester']
    if 'branch' in data: updated_fields['branch'] = data['branch']
    if 'course' in data: updated_fields['course'] = data['course']
    if 'subject' in data: updated_fields['subject'] = data['subject']

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    try:
        result = exams_collection.update_one({'_id': ObjectId(exam_id)}, {'$set': updated_fields})
    except:
        return jsonify({'message': 'Invalid Exam ID format'}), 400

    if result.matched_count:
        updated_exam = exams_collection.find_one({'_id': ObjectId(exam_id)})
        updated_exam['_id'] = str(updated_exam['_id'])
        return jsonify({'message': 'Exam updated successfully', 'exam': updated_exam}), 200
    return jsonify({'message': 'Exam not found'}), 404

@app.route('/exams/<exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    try:
        result = exams_collection.delete_one({'_id': ObjectId(exam_id)})
    except:
        return jsonify({'message': 'Invalid Exam ID format'}), 400

    if result.deleted_count:
        return jsonify({'message': 'Exam deleted successfully'}), 200
    return jsonify({'message': 'Exam not found'}), 404

# --- CRUD Endpoints for Rooms ---
@app.route('/rooms', methods=['POST'])
def add_room():
    data = request.get_json()
    if not all([data.get('name'), data.get('capacity'), data.get('floor')]):
        return jsonify({'message': 'Missing room name, capacity, or floor'}), 400
    if rooms_collection.find_one({'name': data['name']}):
        return jsonify({'message': 'Room with this name already exists'}), 409

    new_room = {'name': data['name'], 'capacity': data['capacity'], 'floor': data['floor']}
    rooms_collection.insert_one(new_room)
    new_room['_id'] = str(new_room['_id'])
    return jsonify({'message': 'Room added successfully', 'room': new_room}), 201

@app.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = []
    for room in rooms_collection.find():
        room['_id'] = str(room['_id'])
        rooms.append(room)
    return jsonify(rooms), 200

@app.route('/rooms/<room_id>', methods=['GET'])
def get_room(room_id):
    try:
        room = rooms_collection.find_one({'_id': ObjectId(room_id)})
    except:
        return jsonify({'message': 'Invalid Room ID format'}), 400
    if room:
        room['_id'] = str(room['_id'])
        return jsonify(room), 200
    return jsonify({'message': 'Room not found'}), 404

@app.route('/rooms/<room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.get_json()
    updated_fields = {}
    if 'name' in data: updated_fields['name'] = data['name']
    if 'capacity' in data: updated_fields['capacity'] = data['capacity']
    if 'floor' in data: updated_fields['floor'] = data['floor']

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    try:
        result = rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': updated_fields})
    except:
        return jsonify({'message': 'Invalid Room ID format'}), 400

    if result.matched_count:
        updated_room = rooms_collection.find_one({'_id': ObjectId(room_id)})
        updated_room['_id'] = str(updated_room['_id'])
        return jsonify({'message': 'Room updated successfully', 'room': updated_room}), 200
    return jsonify({'message': 'Room not found'}), 404

@app.route('/rooms/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    try:
        result = rooms_collection.delete_one({'_id': ObjectId(room_id)})
    except:
        return jsonify({'message': 'Invalid Room ID format'}), 400

    if result.deleted_count:
        return jsonify({'message': 'Room deleted successfully'}), 200
    return jsonify({'message': 'Room not found'}), 404

# --- CRUD Endpoints for Subjects ---
@app.route('/subjects', methods=['POST'])
def add_subject():
    data = request.get_json()
    if not all([data.get('name'), data.get('code')]):
        return jsonify({'message': 'Missing subject name or code'}), 400
    if subjects_collection.find_one({'code': data['code']}):
        return jsonify({'message': 'Subject with this code already exists'}), 409

    new_subject = {'name': data['name'], 'code': data['code']}
    subjects_collection.insert_one(new_subject)
    new_subject['_id'] = str(new_subject['_id'])
    return jsonify({'message': 'Subject added successfully', 'subject': new_subject}), 201

@app.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = []
    for subject in subjects_collection.find():
        subject['_id'] = str(subject['_id'])
        subjects.append(subject)
    return jsonify(subjects), 200

@app.route('/subjects/<subject_id>', methods=['GET'])
def get_subject(subject_id):
    try:
        subject = subjects_collection.find_one({'_id': ObjectId(subject_id)})
    except:
        return jsonify({'message': 'Invalid Subject ID format'}), 400
    if subject:
        subject['_id'] = str(subject['_id'])
        return jsonify(subject), 200
    return jsonify({'message': 'Subject not found'}), 404

@app.route('/subjects/<subject_id>', methods=['PUT'])
def update_subject(subject_id):
    data = request.get_json()
    updated_fields = {}
    if 'name' in data: updated_fields['name'] = data['name']
    if 'code' in data: updated_fields['code'] = data['code']

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    try:
        result = subjects_collection.update_one({'_id': ObjectId(subject_id)}, {'$set': updated_fields})
    except:
        return jsonify({'message': 'Invalid Subject ID format'}), 400

    if result.matched_count:
        updated_subject = subjects_collection.find_one({'_id': ObjectId(subject_id)})
        updated_subject['_id'] = str(updated_subject['_id'])
        return jsonify({'message': 'Subject updated successfully', 'subject': updated_subject}), 200
    return jsonify({'message': 'Subject not found'}), 404

@app.route('/subjects/<subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    try:
        result = subjects_collection.delete_one({'_id': ObjectId(subject_id)})
    except:
        return jsonify({'message': 'Invalid Subject ID format'}), 400

    if result.deleted_count:
        return jsonify({'message': 'Subject deleted successfully'}), 200
    return jsonify({'message': 'Subject not found'}), 404

# --- CRUD Endpoints for Allocations (Room Allocations) ---
@app.route('/allocations', methods=['POST'])
def add_allocation():
    data = request.get_json()
    required_fields = ['room', 'teacher_id', 'exam_name', 'exam_date', 'subject', 'branch', 'course', 'semester', 'startTime', 'endTime', 'floor']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing allocation details'}), 400

    floor_number = data.get('floor')

    if allocations_collection.find_one({
        'room': data['room'],
        'teacher_id': data['teacher_id'],
        'exam_date': data['exam_date'],
        'startTime': data['startTime']
    }):
        return jsonify({'message': 'An allocation for this room, teacher, date, and start time already exists'}), 409

    new_allocation = {
        'room': data['room'],
        'teacher_id': data['teacher_id'],
        'exam_name': data['exam_name'],
        'exam_date': data['exam_date'],
        'subject': data['subject'],
        'branch': data['branch'],
        'course': data['course'],
        'semester': data['semester'],
        'startTime': data['startTime'],
        'endTime': data['endTime'],
        'floor': floor_number # Add floor number to the allocation
    }
    allocations_collection.insert_one(new_allocation)
    new_allocation['_id'] = str(new_allocation['_id'])
    return jsonify({'message': 'Room allocation added successfully', 'allocation': new_allocation}), 201

@app.route('/allocations', methods=['GET'])
def get_allocations():
    allocations = []
    for allocation in allocations_collection.find():
        allocation['_id'] = str(allocation['_id'])
        # Fetch room details to add floor number
        room_name = allocation.get('room')
        if room_name:
            room_data = rooms_collection.find_one({'name': room_name})
            if room_data:
                allocation['floor'] = room_data.get('floor', 'N/A')
            else:
                allocation['floor'] = 'N/A' # Room not found
        else:
            allocation['floor'] = 'N/A' # No room specified

        allocations.append(allocation)
    return jsonify(allocations), 200

@app.route('/allocations/<allocation_id>', methods=['GET'])
def get_allocation(allocation_id):
    try:
        allocation = allocations_collection.find_one({'_id': ObjectId(allocation_id)})
    except:
        return jsonify({'message': 'Invalid Allocation ID format'}), 400
    if allocation:
        allocation['_id'] = str(allocation['_id'])
        return jsonify(allocation), 200
    return jsonify({'message': 'Allocation not found'}), 404

@app.route('/allocations/<allocation_id>', methods=['PUT'])
def update_allocation(allocation_id):
    data = request.get_json()
    updated_fields = {}
    updatable_fields = ['room', 'teacher_id', 'exam_name', 'exam_date', 'subject',
                        'branch', 'course', 'semester', 'startTime', 'endTime', 'floor']
    for field in updatable_fields:
        if field in data: updated_fields[field] = data[field]

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    try:
        result = allocations_collection.update_one({'_id': ObjectId(allocation_id)}, {'$set': updated_fields})
    except:
        return jsonify({'message': 'Invalid Allocation ID format'}), 400

    if result.matched_count:
        updated_allocation = allocations_collection.find_one({'_id': ObjectId(allocation_id)})
        updated_allocation['_id'] = str(updated_allocation['_id'])
        return jsonify({'message': 'Allocation updated successfully', 'allocation': updated_allocation}), 200
    return jsonify({'message': 'Allocation not found'}), 404

@app.route('/allocations/<allocation_id>', methods=['DELETE'])
def delete_allocation(allocation_id):
    try:
        result = allocations_collection.delete_one({'_id': ObjectId(allocation_id)})
    except:
        return jsonify({'message': 'Invalid Allocation ID format'}), 400

    if result.deleted_count:
        return jsonify({'message': 'Allocation deleted successfully'}), 200
    return jsonify({'message': 'Allocation not found'}), 404

@app.route('/allocations/teacher/<teacher_id>', methods=['GET'])
def get_teacher_allocations(teacher_id):
    allocations = []
    for allocation in allocations_collection.find({'teacher_id': teacher_id}):
        allocation['_id'] = str(allocation['_id'])
        allocations.append(allocation)
    return jsonify(allocations), 200

# --- CRUD Endpoints for Student Allocations ---
@app.route('/student_allocations', methods=['POST'])
def add_student_allocation():
    data = request.get_json()
    required_fields = ['student_name', 'student_id', 'student_semester', 'student_branch', 'student_course', 'room_name', 'room_floor', 'seat_number', 'start_time', 'end_time', 'exam_date', 'subject']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing student allocation details'}), 400

    if student_allocations_collection.find_one({
        'student_id': data['student_id'],
        'room_name': data['room_name'],
        'student_semester': data['student_semester'],
        'seat_number': data['seat_number'],
        'start_time': data['start_time'],
        'end_time': data['end_time'],
        'exam_date': data['exam_date'],
        'subject': data['subject']
    }):
        return jsonify({'message': 'Student allocation for this student, room, semester, seat, start time, end time, exam date and subject already exists'}), 409

    new_student_allocation = {
        'student_name': data['student_name'],
        'student_id': data['student_id'],
        'student_semester': data['student_semester'],
        'student_branch': data['student_branch'],
        'student_course': data['student_course'],
        'room_name': data['room_name'],
        'room_floor': data['room_floor'],
        'seat_number': data['seat_number'],
        'start_time': data['start_time'],
        'end_time': data['end_time'],
        'exam_date': data['exam_date'],
        'subject': data['subject']
    }
    student_allocations_collection.insert_one(new_student_allocation)
    new_student_allocation['_id'] = str(new_student_allocation['_id'])
    return jsonify({'message': 'Student allocation added successfully', 'student_allocation': new_student_allocation}), 201

@app.route('/student_allocations', methods=['GET'])
def get_student_allocations():
    student_allocations = []
    for allocation in student_allocations_collection.find():
        allocation['_id'] = str(allocation['_id'])
        student_allocations.append(allocation)
    return jsonify(student_allocations), 200

@app.route('/student_allocations/<student_allocation_id>', methods=['GET'])
def get_student_allocation(student_allocation_id):
    try:
        allocation = student_allocations_collection.find_one({'_id': ObjectId(student_allocation_id)})
    except:
        return jsonify({'message': 'Invalid Student Allocation ID format'}), 400
    if allocation:
        allocation['_id'] = str(allocation['_id'])
        return jsonify(allocation), 200
    return jsonify({'message': 'Student allocation not found'}), 404

@app.route('/student_allocations/<student_allocation_id>', methods=['PUT'])
def update_student_allocation(student_allocation_id):
    data = request.get_json()
    updated_fields = {}
    updatable_fields = ['student_name', 'student_id', 'student_semester', 'student_branch', 'student_course', 'room_name', 'room_floor', 'seat_number', 'start_time', 'end_time', 'exam_date', 'subject']
    for field in updatable_fields:
        if field in data: updated_fields[field] = data[field]

    print(f"Received student_allocation_id for update: {student_allocation_id}")
    print(f"Received updated_fields: {updated_fields}")

    if not updated_fields:
        return jsonify({'message': 'No fields to update'}), 400

    try:
        result = student_allocations_collection.update_one({'_id': ObjectId(student_allocation_id)}, {'$set': updated_fields})
    except:
        return jsonify({'message': 'Invalid Student Allocation ID format'}), 400

    if result.matched_count:
        updated_allocation = student_allocations_collection.find_one({'_id': ObjectId(student_allocation_id)})
        updated_allocation['_id'] = str(updated_allocation['_id'])
        return jsonify({'message': 'Student allocation updated successfully', 'student_allocation': updated_allocation}), 200
    return jsonify({'message': 'Student allocation not found'}), 404

@app.route('/student_allocations/<student_allocation_id>', methods=['DELETE'])
def delete_student_allocation(student_allocation_id):
    try:
        result = student_allocations_collection.delete_one({'_id': ObjectId(student_allocation_id)})
    except:
        return jsonify({'message': 'Invalid Student Allocation ID format'}), 400

    if result.deleted_count:
        return jsonify({'message': 'Student allocation deleted successfully'}), 200
    return jsonify({'message': 'Student allocation not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
@app.route('/login_teacher', methods=['POST'])
def login_teacher():
    data = request.get_json()
    teacher_name = data.get('teacherName')
    teacher_id = data.get('teacherId')

    if not all([teacher_name, teacher_id]):
        return jsonify({'message': 'Missing teacher name or ID'}), 400

    teacher = teachers_collection.find_one({'name': teacher_name, 'id': teacher_id})

    if teacher:
        teacher['_id'] = str(teacher['_id'])
        user_entry = users_collection.find_one({'id': teacher_id, 'type': 'teacher'})
        if not user_entry:
            users_collection.insert_one({
                'id': teacher_id,
                'name': teacher_name,
                'password': 'teacher123', # Default password
                'type': 'teacher'
            })
        return jsonify({'message': 'Teacher login successful', 'name': teacher['name'], 'id': teacher['id'], 'type': 'teacher'}), 200
    else:
        return jsonify({'message': 'Invalid teacher name or ID'}), 401

