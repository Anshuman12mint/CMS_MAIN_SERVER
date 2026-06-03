from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CourseWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    course_code: str | None = Field(default=None, validation_alias=AliasChoices("courseCode", "course_code"))
    course_name: str | None = Field(default=None, validation_alias=AliasChoices("courseName", "course_name"))
    course_description: str | None = Field(
        default=None,
        validation_alias=AliasChoices("courseDescription", "course_description"),
    )


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    course_code: str | None = Field(default=None, serialization_alias="courseCode")
    course_name: str | None = Field(default=None, serialization_alias="courseName")
    course_description: str | None = Field(default=None, serialization_alias="courseDescription")

