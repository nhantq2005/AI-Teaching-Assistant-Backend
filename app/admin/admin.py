from fastapi import FastAPI
from app.admin.auth import AdminAuth
from sqladmin import Admin, ModelView
from app.db.session import engine
from app.models import Document
from app.models.user import User
from app.models.subject import Subject

class UserAdmin(ModelView, model=User):
    name = "Người dùng"
    name_plural = "Quản lý Người dùng"
    column_list = [User.id, User.username, User.name, User.email, User.role, User.is_active]
    column_searchable_list = [User.username, User.email, User.name]
    form_excluded_columns = [User.documents, User.attempt_quizzes, User.subjects, User.enrollments, User.notification_reads, User.chat_sessions]
    icon = "fa-solid fa-user"

class SubjectAdmin(ModelView, model=Subject):
    name = "Môn học"
    name_plural = "Quản lý Môn học"
    column_list = [Subject.id, Subject.code, Subject.name, Subject.lecturer_id]
    column_searchable_list = [Subject.code, Subject.name]
    form_excluded_columns = [Subject.notifications, Subject.enrollments, Subject.documents, Subject.quizzes]
    icon = "fa-solid fa-book"

class DocumentAdmin(ModelView, model=Document):
    name = "Tài liệu"
    name_plural = "Quản lý tài liệu"
    column_list = [Document.title, Document.created_date, Document.process_status, Document.file_name]
    column_searchable_list = [Document.title, Document.created_date]
    icon = "fa-solid fa-file-pdf"

def setup_admin(app: FastAPI):
    authentication_backend = AdminAuth(secret_key="super-secret-admin-key")
    admin = Admin(
        app, 
        engine, 
        title="EduAssist",
        authentication_backend=authentication_backend
    )
    admin.add_view(UserAdmin)
    admin.add_view(SubjectAdmin)
    admin.add_view(DocumentAdmin)
