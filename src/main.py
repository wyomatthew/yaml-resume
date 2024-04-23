"""main.py"""

from dataclasses import dataclass
from datetime import date
import sys
from typing import Any, List, Optional

from pylatex.base_classes import (
    BaseLaTeXClass,
    Container,
    Environment,
    LatexObject,
    SpecialOptions,
    latex_object,
)
from pylatex.lists import Itemize
from pylatex.utils import bold, italic
from resume import (
    Award,
    Certificate,
    Education,
    Location,
    Project,
    Resume,
    Profile,
    Skill,
    Work,
)
from yaml import load, Loader
from pylatex import (
    Document,
    Figure,
    HFill,
    HorizontalSpace,
    MiniPage,
    NewLine,
    NoEscape,
    Package,
    Section,
    Subsection,
    Tabular,
    Command,
    HugeText,
    LargeText,
    Center,
    TextColor,
    VerticalSpace,
    Hyperref,
)

DETAIL_INDENT = "0.25in"
RESOURCE_MAP = {
    "github": "resources/github.png",
    "linkedin": "resources/in.png",
    "phone": "resources/phone.png",
    "mail": "resources/mail.png",
    "home": "resources/home.png",
    "web": "resources/web.png",
}


class AdjustWidth(Environment):
    packages = [Package("changepage")]

    _repr_attributes_mapping = {"leftmargin": "arguments", "rightmargin": "arguments"}

    def __init__(
        self,
        *,
        leftmargin: Optional[str] = None,
        rightmargin: Optional[str] = None,
        data: str | LatexObject | None = None,
    ):
        arguments = [leftmargin, rightmargin]
        options = SpecialOptions()

        if data is not None:
            if not isinstance(data, list):
                data = [data]
        else:
            data = list()

        super().__init__(arguments=arguments, options=options, data=data)


@dataclass()
class Link(object):
    text: str
    ref: str


class EntryGenerator(object):
    title: str
    context: Optional[str] = None
    location: Optional[Location] = None
    start_date: date
    end_date: Optional[date] = None
    link: Optional[Link] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    is_instant: bool = False

    def __init__(self, title: str, start_date: date):
        self.title = title
        self.start_date = start_date

    def generate(self, doc: Document):
        doc.append(bold(self.title))
        if self.context is not None:
            doc.append(", ")
            doc.append(italic(self.context))
        if self.link is not None:
            doc.append(HorizontalSpace("6pt"))
            doc.append(
                TextColor("blue", Command("href", [self.link.ref, self.link.text]))
            )
        doc.append(Command("hfill"))
        if self.location is not None:
            doc.append(bold(format_location(self.location)))
            doc.append(HorizontalSpace("6pt"))
        doc.append(
            italic(format_time_range(self.start_date, self.end_date, self.is_instant))
        )
        if self.summary is not None or self.highlights is not None:
            with doc.create(AdjustWidth(leftmargin=DETAIL_INDENT, rightmargin="0in")):
                if self.summary is not None:
                    doc.append(self.summary)
                if self.highlights is not None:
                    with doc.create(Itemize()) as itemize:
                        itemize: Itemize
                        for highlight in self.highlights:
                            itemize.add_item(highlight)


def format_location(location: Optional[Location]) -> str:
    if location is None:
        raise RuntimeError()
    return f"{location.city}, {location.region}"


def format_profile(profile: Optional[Profile]):
    if profile is None:
        raise RuntimeError()
    link_text = f"{profile.network}/{profile.username}"
    if profile.network.strip().lower() in RESOURCE_MAP.keys():
        resource_name = profile.network.strip().lower()
    else:
        resource_name = "web"
    return Command(
        "href",
        [
            profile.url,
            NoEscape(
                generate_image_inline(RESOURCE_MAP[resource_name]).dumps()
                + " "
                + link_text
            ),
        ],
    )


def format_time_range(
    start: date, end: Optional[date], is_instant: bool = False
) -> str:
    format_date = lambda format_me: format_me.strftime("%m/%Y")
    if is_instant:
        return format_date(start)
    elif end is None:
        return f"{format_date(start)} - present"
    else:
        return f"{format_date(start)} - {format_date(end)}"


def generate_image_inline(resource_path: str) -> Command:
    """Mutates the input document to include the indicated resource in-line"""
    return Command(
        "includegraphics",
        resource_path,
        NoEscape(r"height=\fontcharht\font`\B"),
    )


def generate_contact_info(doc: Document, resume: Resume):
    """Mutates the input document to include contact information table."""
    with doc.create(Tabular("c | c | c", col_space="6pt")) as table:
        table: Tabular
        table.add_row(
            NoEscape(
                generate_image_inline(RESOURCE_MAP["phone"]).dumps()
                + " "
                + resume.basics.phone
            ),
            NoEscape(
                generate_image_inline(RESOURCE_MAP["mail"]).dumps()
                + " "
                + Command(
                    "href", [f"mailto:{resume.basics.email}", resume.basics.email]
                ).dumps()
            ),
            NoEscape(
                generate_image_inline(RESOURCE_MAP["home"]).dumps()
                + " "
                + format_location(resume.basics.location),
            ),
        )


def generate_profiles(doc: Document, resume: Resume):
    """Mutates the input document to include all social profiles."""
    if resume.basics.profiles is not None:
        profile_count = len(resume.basics.profiles)
        with doc.create(Tabular(" | ".join(["c"] * profile_count))) as table:
            table: Tabular
            table.add_row(
                [
                    format_profile(resume.basics.profiles[i])
                    for i in range(profile_count)
                ]
            )


def generate_header(doc: Document, resume: Resume):
    """Mutates the input document to have all necessary header info."""
    doc.append(Command("makecvtitle"))
    with doc.create(Center()):
        with doc.create(HugeText()):
            doc.append(Command("textbf", resume.basics.name))
        doc.append(Command("break"))

        generate_contact_info(doc, resume)
        doc.append(Command("break"))

        generate_profiles(doc, resume)


def generate_section_title(doc: Document, section_name: str):
    """Mutates the input document to include the input section name."""
    doc.append(VerticalSpace(".1in"))
    with doc.create(LargeText()):
        doc.append(Command("textbf", section_name))
    doc.append(VerticalSpace(".05in"))
    doc.append(Command("hrule"))
    doc.append(VerticalSpace("0.05in"))


def generate_education(doc: Document, education_list: List[Education]):
    """Mutates input document to include education section."""
    with doc.create(Section("Education")):
        generate_section_title(doc, "Education")

        for education in education_list:
            generator = EntryGenerator(education.study_type, education.start_date)
            generator.context = education.institution
            generator.location = education.location
            generator.end_date = education.end_date
            generator.summary = "\n".join(
                [
                    f"Area of study: {education.area}",
                    f"Concentration: {education.sub_area}",
                    f"Final result: {education.score}",
                    f"Relevant coursework: {', '.join(education.courses)}",
                ]
            )
            generator.generate(doc)


def generate_experience(doc: Document, work_list: List[Work]):
    """Mutates input document to include experience section."""
    with doc.create(Section("Experience")):
        generate_section_title(doc, "Experience")

        for work in work_list:
            generator = EntryGenerator(work.position, work.start_date)
            generator.context = work.name
            generator.location = work.location
            generator.end_date = work.end_date
            generator.highlights = work.highlights
            generator.generate(doc)


def generate_projects(doc: Document, projects: List[Project]):
    """Mutates input document to include projects section."""
    with doc.create(Section("Projects")):
        generate_section_title(doc, "Projects")

        for project in projects:
            generator = EntryGenerator(project.name, project.start_date)
            generator.end_date = project.end_date
            generator.summary = project.summary
            if project.url is not None:
                link_text = "(link)" if project.url_text is None else project.url_text
                generator.link = Link(link_text, project.url)
            generator.generate(doc)


def generate_certifications_and_awards(
    doc: Document,
    certifications: Optional[List[Certificate]],
    awards: Optional[List[Award]],
):
    """Mutates input document to include certifications section."""
    with doc.create(Section("Certifications & Awards")):
        to_process: List[Certificate | Award] = list()
        if certifications is None:
            section_title = "Certifications"
        elif awards is None:
            section_title = "Awards"
        else:
            section_title = "Certifications & Awards"
        generate_section_title(doc, section_title)

        if certifications is not None:
            to_process.extend(certifications)
        if awards is not None:
            to_process.extend(awards)

        for item in to_process:
            if isinstance(item, Certificate):
                generator = EntryGenerator(item.name, item.date)
                generator.is_instant = True
                generator.summary = item.summary
                generator.generate(doc)
            else:
                generator = EntryGenerator(item.name, item.date)
                generator.is_instant = True
                generator.summary = item.summary
                generator.generate(doc)


def generate_skills(doc: Document, skills: List[Skill]):
    with doc.create(Section("Skills")):
        generate_section_title(doc, "Skills")

        for skill in skills:
            doc.append(italic(skill.name))
            doc.append(": ")
            doc.append(", ".join(skill.keywords))
            doc.append(NewLine())


def generate_body(doc: Document, resume: Resume):
    """Mutates input document to include body information."""
    if resume.education is not None:
        generate_education(doc, resume.education)
    if resume.work is not None:
        generate_experience(doc, resume.work)
    if resume.projects is not None:
        generate_projects(doc, resume.projects)
    if resume.certificates is not None or resume.awards is not None:
        generate_certifications_and_awards(doc, resume.certificates, resume.awards)
    if resume.skills is not None:
        generate_skills(doc, resume.skills)


def generate_doc(resume: Resume) -> Document:
    document_options = ["10pt", "letterpaper"]
    geometry_options = {
        "lmargin": "0.5in",
        "rmargin": "0.5in",
        "tmargin": "0.5in",
        "bmargin": "0.5in",
    }
    name_command = Command("name", resume.basics.name.split())
    custom_preamble = [
        Command("moderncvstyle", "empty"),
        Command("moderncvcolor", "black"),
        name_command,
    ]

    out = Document(
        documentclass="moderncv",
        geometry_options=geometry_options,
        document_options=document_options,
    )
    out.preamble.extend(custom_preamble)

    generate_header(out, resume)
    generate_body(out, resume)

    return out


def main():
    path = sys.argv[1]
    print(f"Parsing {path}...")

    with open(path, "r") as fp:
        contents = load(fp.read(), Loader)

    my_resume: Resume = Resume.model_validate(contents)
    generated_doc = generate_doc(my_resume)

    with open("out.tex", "w") as fp:
        generated_doc.dump(fp)


if __name__ == "__main__":
    main()
