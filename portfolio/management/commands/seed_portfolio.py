"""Seed portfolio content from resume.md. Usage: python manage.py seed_portfolio"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from portfolio.models import BlogPost, Education, Experience, Profile, Project, Skill

SUMMARY = (
    "Computer Science graduate with professional experience in embedded networking "
    "software development using C/C++ and a strong foundation in operating systems, "
    "computer architecture, and computer networking. Skilled in routing protocols, "
    "routing and switching, and low-level systems programming, with working knowledge "
    "of Python. Quick to learn new technologies, with strong analytical and "
    "problem-solving skills, passionate about systems programming and networking."
)

SKILLS = [
    ("language", [("C", 5), ("C++", 4), ("Python", 3)]),
    ("os", [("VxWorks RTOS", 4), ("OS internals / memory management", 4), ("IPC / process synchronization", 4)]),
    ("networking", [("BGP", 4), ("OSPF", 4), ("RIP / RIPng", 4), ("MPLS L3VPN / LDP / VRF", 3), ("VLANs / IPv4+IPv6", 4)]),
    ("framework", [("Django", 3), ("SQL", 3), ("Git", 4), ("AWS foundational", 2), ("PHP", 2)]),
    ("cs", [("Data Structures & Algorithms", 4), ("Computer Networks", 5), ("OOP", 4)]),
]

PROJECTS = [
    {
        "title": "TFTP Server for Windows (C)",
        "summary": "Multithreaded TFTP server in C for Windows (RFC-1350).",
        "description": "Developed a multithreaded TFTP server in C for Windows based on RFC-1350, supporting concurrent file transfers.",
        "techs": ["C"],
    },
    {
        "title": "TFTP on VxWorks (BDCOM)",
        "summary": "Implemented TFTP protocol (RFC 1350) in C for VxWorks.",
        "description": "Implemented the TFTP protocol (RFC 1350) in C for the VxWorks platform as part of the routing team at Shanghai BDCOM.",
        "techs": ["C", "VxWorks RTOS"],
    },
    {
        "title": "Custom 6-bit CPU and ISA Design",
        "summary": "6-bit CPU in Logisim: datapath, control unit, 6 registers, 15-bit ISA.",
        "description": "Designed a custom 6-bit CPU in Logisim with a datapath, control unit, 6-register architecture, 15-bit ISA, Register/Immediate addressing modes, verified through simulation.",
        "techs": [],
    },
    {
        "title": "Safe Distance Monitoring (ESP8266)",
        "summary": "Embedded safe-distance monitor with real-time sensing + mobile alerts.",
        "description": "Developed an ESP8266-based embedded system for safe-distance monitoring with real-time sensor processing and mobile-application alerts.",
        "techs": ["C"],
    },
    {
        "title": "Clustering Web App (Django + K-Means)",
        "summary": "Django platform with custom K-Means and live visualization.",
        "description": "Built a Django-based platform with a customized K-Means algorithm and real-time data visualization for multidimensional dataset analysis.",
        "techs": ["Python", "Django"],
    },
    {
        "title": "Home Value Prediction Platform",
        "summary": "Django app for dataset upload, remote training, price prediction.",
        "description": "Developed a Django web application for dataset upload, remote ML model training, and home value prediction.",
        "techs": ["Python", "Django"],
    },
    {
        "title": "AI Email Analysis (OpenAI API)",
        "summary": "AI-powered email analysis + automated sending with Django.",
        "description": "Developed an AI-powered email analysis system using the OpenAI API with automated email sending via Django.",
        "techs": ["Python", "Django"],
    },
]


class Command(BaseCommand):
    help = "Seed portfolio from resume.md content"

    def handle(self, *args, **options):
        with transaction.atomic():
            profile, _ = Profile.objects.get_or_create(
                full_name="Md Tariqul Islam",
                defaults={
                    "title": "R&D Engineer — Routing / Embedded Networking",
                    "summary": SUMMARY,
                    "location": "Dhaka, Bangladesh",
                    "photo": "profile/photo.jpg",  # replace with real photo via admin
                },
            )

            Education.objects.get_or_create(
                degree="B.Sc. in Computer Science & Engineering",
                institution="Rajshahi University of Engineering & Technology (RUET)",
                defaults={"end": date(2024, 12, 31), "result": "CGPA 3.30/4.00", "order": 0},
            )
            Education.objects.get_or_create(
                degree="Higher Secondary Certificate (HSC)",
                institution="Uttara High School & College",
                defaults={"end": date(2018, 12, 31), "result": "GPA 4.92/5.00", "order": 1},
            )

            Experience.objects.get_or_create(
                role="R&D Engineer — Routing Team",
                company="Shanghai BDCOM",
                defaults={
                    "start": date(2025, 2, 1),
                    "end": date(2026, 7, 31),
                    "order": 0,
                    "bullets": (
                        "Implemented the TFTP protocol (RFC 1350) in C for VxWorks.\n"
                        "Tested and validated the RIP routing protocol implementation.\n"
                        "Tested 6PE/6VPE features across 15+ topologies; found 40+ bugs, investigated root causes.\n"
                        "Resolved BGP protocol issues in BSR series routers.\n"
                        "Low-level systems programming, protocol development, performance optimization."
                    ),
                },
            )
            Experience.objects.get_or_create(
                role="Backend Developer Intern",
                company="",
                defaults={
                    "start": date(2024, 11, 1),
                    "end": date(2025, 1, 31),
                    "order": 1,
                    "bullets": (
                        "AI-powered email analysis system using the OpenAI API.\n"
                        "Automated email sending with Django.\n"
                        "Backend development with Django and SQL."
                    ),
                },
            )

            order = 0
            for category, names in SKILLS:
                for name, level in names:
                    Skill.objects.get_or_create(
                        name=name, defaults={"category": category, "proficiency": level, "order": order}
                    )
                    order += 1

            for i, p in enumerate(PROJECTS):
                proj, _ = Project.objects.get_or_create(
                    title=p["title"],
                    defaults={"summary": p["summary"], "description": p["description"], "order": i, "featured": i < 3},
                )
                for t in p["techs"]:
                    skill = Skill.objects.filter(name=t).first()
                    if skill:
                        proj.technologies.add(skill)

            self.stdout.write(self.style.SUCCESS("Seeded profile, education, experience, skills, projects."))
            self.stdout.write("Next: add your photo via admin (Profile), add BlogPosts with LinkedIn URLs.")
