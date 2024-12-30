from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, func, SmallInteger, BigInteger, Float
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import DeferredReflection
from typing import Optional


class BaseDB(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_url: Mapped[str] = mapped_column(String)
    remark: Mapped[str] = mapped_column(String)
    creator: Mapped[str] = mapped_column(String, default='')
    create_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=func.now())
    updater: Mapped[str] = mapped_column(String, default='')
    update_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=func.now())
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0)
    tenant_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    name_vector: Mapped[Vector] = mapped_column(Vector)
    search_vector: Mapped[TSVECTOR] = mapped_column(TSVECTOR)
    instructor_name: Mapped[str] = mapped_column(String)


class USCCourseDB(BaseDB):
    __abstract__ = False
    __tablename__ = 'usc_courses'
    section: Mapped[str] = mapped_column(String)
    units: Mapped[str] = mapped_column(String)
    offering_title: Mapped[str] = mapped_column(String)
    days: Mapped[str] = mapped_column(String)
    time: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    grade_scheme: Mapped[str] = mapped_column(String)
    registered: Mapped[str] = mapped_column(String)
    total_seats: Mapped[str] = mapped_column(String)


class USFCourseDB(BaseDB):
    __tablename__ = 'usf_courses'
    term: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, doc="The term of the course")
    time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    classroom: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_range: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    schedule_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, doc="The schedule type of the course")
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    course_type: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True)
    course_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, doc="The course code")
    section: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, doc="The section of the course")
    campus: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="The campus where the course is offered")
    instructional_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, doc="The instructional method used in the course")
    credits: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The number of credits for the course")
    capacity: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The capacity of the course")
    actual: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The actual number of enrolled students")
    remaining: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The remaining seats available")
    waitlist_capacity: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The capacity of the waitlist")
    waitlist_actual: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The actual number of students on the waitlist")
    waitlist_remaining: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The remaining spots on the waitlist")
    field_of_study: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="The field of study of the course")
    prerequisite_course: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, doc="The prerequisite course code")
    minimum_grade: Mapped[Optional[str]] = mapped_column(
        String(2), nullable=True, doc="The minimum grade required")
