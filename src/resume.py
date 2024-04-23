"""resume.py"""

from datetime import date
from pydantic import BaseModel
from typing import Optional, List


class Location(BaseModel):
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: str
    country_code: str
    region: str


class Profile(BaseModel):
    network: str
    username: str
    url: str


class Basics(BaseModel):
    name: str
    label: Optional[str]
    email: str
    phone: str
    url: Optional[str]
    summary: Optional[str]
    location: Optional[Location]
    profiles: Optional[List[Profile]]


class Work(BaseModel):
    name: str
    position: str
    url: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    summary: Optional[str] = None
    highlights: List[str]
    location: Optional[Location] = None


class Education(BaseModel):
    institution: str
    url: Optional[str] = None
    area: str
    sub_area: Optional[str] = None
    study_type: str
    start_date: date
    end_date: Optional[date] = None
    score: Optional[str] = None
    courses: List[str]
    location: Optional[Location] = None


class Certificate(BaseModel):
    name: str
    date: date
    issuer: str
    summary: str
    url: Optional[str] = None


class Award(BaseModel):
    name: str
    date: date
    awarder: str
    summary: str
    url: Optional[str] = None


class Skill(BaseModel):
    name: str
    level: Optional[str] = None
    keywords: List[str]


class Language(BaseModel):
    language: str
    fluency: str


class Interest(BaseModel):
    name: str
    keywords: List[str]


class Project(BaseModel):
    name: str
    start_date: date
    end_date: Optional[date] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    url_text: Optional[str] = None
    url: Optional[str] = None


class Resume(BaseModel):
    basics: Basics
    work: Optional[List[Work]] = None
    education: Optional[List[Education]] = None
    certificates: Optional[List[Certificate]] = None
    awards: Optional[List[Award]] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    interests: Optional[List[Interest]] = None
    projects: Optional[List[Project]] = None
