"""Schedule models for GAM Reports - automated report execution."""

from pydantic import BaseModel, Field, model_validator

from .enums import DayOfWeek, Frequency, DeliveryCondition


class TimeOfDay(BaseModel):
    """Time specification for scheduled execution."""

    hours: int = Field(ge=0, le=23, description="Hour (0-23)")
    minutes: int = Field(default=0, ge=0, le=59, description="Minutes (0-59)")
    seconds: int = Field(default=0, ge=0, le=59, description="Seconds (0-59)")

    @classmethod
    def at(cls, hours: int, minutes: int = 0) -> "TimeOfDay":
        """Create time at specified hour and minutes."""
        return cls(hours=hours, minutes=minutes)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
        }


class WeeklySchedule(BaseModel):
    """Weekly recurrence pattern."""

    days_of_week: list[DayOfWeek] = Field(
        alias="daysOfWeek", description="Days to run the report"
    )
    time_zone: str = Field(
        default="America/New_York", alias="timeZone", description="IANA timezone"
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def on_days(
        cls, days: list[DayOfWeek], timezone: str = "America/New_York"
    ) -> "WeeklySchedule":
        """Create schedule for specific days."""
        return cls(days_of_week=days, time_zone=timezone)

    @classmethod
    def weekdays(cls, timezone: str = "America/New_York") -> "WeeklySchedule":
        """Create schedule for weekdays (Mon-Fri)."""
        return cls(
            days_of_week=[
                DayOfWeek.MONDAY,
                DayOfWeek.TUESDAY,
                DayOfWeek.WEDNESDAY,
                DayOfWeek.THURSDAY,
                DayOfWeek.FRIDAY,
            ],
            time_zone=timezone,
        )

    @classmethod
    def every_monday(cls, timezone: str = "America/New_York") -> "WeeklySchedule":
        """Create schedule for every Monday."""
        return cls(days_of_week=[DayOfWeek.MONDAY], time_zone=timezone)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "daysOfWeek": [d.value for d in self.days_of_week],
            "timeZone": self.time_zone,
        }


class MonthlySchedule(BaseModel):
    """Monthly recurrence pattern."""

    day: int = Field(ge=1, le=31, description="Day of month (1-31)")
    time_zone: str = Field(
        default="America/New_York", alias="timeZone", description="IANA timezone"
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def on_day(cls, day: int, timezone: str = "America/New_York") -> "MonthlySchedule":
        """Create schedule for specific day of month."""
        return cls(day=day, time_zone=timezone)

    @classmethod
    def first_of_month(cls, timezone: str = "America/New_York") -> "MonthlySchedule":
        """Create schedule for first day of month."""
        return cls(day=1, time_zone=timezone)

    @classmethod
    def last_day(cls, timezone: str = "America/New_York") -> "MonthlySchedule":
        """Create schedule for last day of month (using day 31)."""
        return cls(day=31, time_zone=timezone)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "day": self.day,
            "timeZone": self.time_zone,
        }


class Schedule(BaseModel):
    """
    Schedule configuration for automated report execution.

    Use either weekly_schedule or monthly_schedule, not both.
    """

    frequency: Frequency = Field(description="How often to run")
    time_of_day: TimeOfDay = Field(alias="timeOfDay", description="When to run")
    weekly_schedule: WeeklySchedule | None = Field(
        default=None, alias="weeklySchedule", description="Weekly pattern"
    )
    monthly_schedule: MonthlySchedule | None = Field(
        default=None, alias="monthlySchedule", description="Monthly pattern"
    )
    start_time: str | None = Field(
        default=None, alias="startTime", description="ISO timestamp when schedule starts"
    )
    end_time: str | None = Field(
        default=None, alias="endTime", description="ISO timestamp when schedule ends"
    )

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_schedule_type(self) -> "Schedule":
        """Validate schedule configuration matches frequency."""
        if self.frequency == Frequency.WEEKLY and self.weekly_schedule is None:
            raise ValueError("weekly_schedule required for WEEKLY frequency")
        if self.frequency == Frequency.MONTHLY and self.monthly_schedule is None:
            raise ValueError("monthly_schedule required for MONTHLY frequency")
        return self

    @classmethod
    def daily_at(cls, hours: int, minutes: int = 0) -> "Schedule":
        """Create daily schedule at specified time."""
        return cls(
            frequency=Frequency.DAILY,
            time_of_day=TimeOfDay.at(hours, minutes),
        )

    @classmethod
    def weekly_on(
        cls,
        days: list[DayOfWeek],
        hours: int,
        minutes: int = 0,
        timezone: str = "America/New_York",
    ) -> "Schedule":
        """Create weekly schedule on specified days and time."""
        return cls(
            frequency=Frequency.WEEKLY,
            time_of_day=TimeOfDay.at(hours, minutes),
            weekly_schedule=WeeklySchedule.on_days(days, timezone),
        )

    @classmethod
    def monthly_on_day(
        cls,
        day: int,
        hours: int,
        minutes: int = 0,
        timezone: str = "America/New_York",
    ) -> "Schedule":
        """Create monthly schedule on specified day and time."""
        return cls(
            frequency=Frequency.MONTHLY,
            time_of_day=TimeOfDay.at(hours, minutes),
            monthly_schedule=MonthlySchedule.on_day(day, timezone),
        )

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        result = {
            "frequency": self.frequency.value,
            "timeOfDay": self.time_of_day.to_gam_format(),
        }
        if self.weekly_schedule:
            result["weeklySchedule"] = self.weekly_schedule.to_gam_format()
        if self.monthly_schedule:
            result["monthlySchedule"] = self.monthly_schedule.to_gam_format()
        if self.start_time:
            result["startTime"] = self.start_time
        if self.end_time:
            result["endTime"] = self.end_time
        return result


class ScheduleOptions(BaseModel):
    """
    Complete scheduling configuration for automated report delivery.

    Examples:
        # Daily report at 6 AM
        options = ScheduleOptions(
            schedule=Schedule.daily_at(6),
            delivery_conditions=[DeliveryCondition.REPORT_HAS_DATA],
        )

        # Weekly report every Monday at 8 AM, only if data exists
        options = ScheduleOptions(
            schedule=Schedule.weekly_on([DayOfWeek.MONDAY], 8),
            delivery_conditions=[DeliveryCondition.REPORT_HAS_DATA],
            evaluate_delivery_conditions_as_and=True,
        )
    """

    schedule: Schedule = Field(description="When to run the report")
    delivery_conditions: list[DeliveryCondition] = Field(
        default_factory=list,
        alias="deliveryConditions",
        description="Conditions that must be met for delivery",
    )
    evaluate_delivery_conditions_as_and: bool = Field(
        default=True,
        alias="evaluateDeliveryConditionsAsAnd",
        description="If True, ALL conditions must be met. If False, ANY condition.",
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def daily(
        cls, hours: int, minutes: int = 0, only_with_data: bool = True
    ) -> "ScheduleOptions":
        """Create daily schedule options."""
        conditions = [DeliveryCondition.REPORT_HAS_DATA] if only_with_data else []
        return cls(
            schedule=Schedule.daily_at(hours, minutes),
            delivery_conditions=conditions,
        )

    @classmethod
    def weekly(
        cls,
        days: list[DayOfWeek],
        hours: int,
        minutes: int = 0,
        only_with_data: bool = True,
    ) -> "ScheduleOptions":
        """Create weekly schedule options."""
        conditions = [DeliveryCondition.REPORT_HAS_DATA] if only_with_data else []
        return cls(
            schedule=Schedule.weekly_on(days, hours, minutes),
            delivery_conditions=conditions,
        )

    @classmethod
    def monthly(
        cls, day: int, hours: int, minutes: int = 0, only_with_data: bool = True
    ) -> "ScheduleOptions":
        """Create monthly schedule options."""
        conditions = [DeliveryCondition.REPORT_HAS_DATA] if only_with_data else []
        return cls(
            schedule=Schedule.monthly_on_day(day, hours, minutes),
            delivery_conditions=conditions,
        )

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        result = {
            "schedule": self.schedule.to_gam_format(),
        }
        if self.delivery_conditions:
            result["deliveryConditions"] = [c.value for c in self.delivery_conditions]
            result["evaluateDeliveryConditionsAsAnd"] = (
                self.evaluate_delivery_conditions_as_and
            )
        return result
