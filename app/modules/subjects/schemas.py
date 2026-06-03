from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SubjectWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject_name: str | None = Field(default=None, validation_alias=AliasChoices("subjectName", "subject_name"))
    subject_code: str | None = Field(default=None, validation_alias=AliasChoices("subjectCode", "subject_code"))
    course_code: str | None = Field(default=None, validation_alias=AliasChoices("courseCode", "course_code"))
    subject_description: str | None = Field(
        default=None,
        validation_alias=AliasChoices("subjectDescription", "subject_description"),
    )


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    subject_id: int | None = Field(default=None, serialization_alias="subjectId")
    subject_name: str | None = Field(default=None, serialization_alias="subjectName")
    subject_code: str | None = Field(default=None, serialization_alias="subjectCode")
    course_code: str | None = Field(default=None, serialization_alias="courseCode")
    subject_description: str | None = Field(default=None, serialization_alias="subjectDescription")

