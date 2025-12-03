"""Size model for GAM Reports - ad unit, creative, and line item dimensions."""

from enum import Enum
from pydantic import BaseModel, Field


class SizeType(str, Enum):
    """How ad dimensions are interpreted."""

    SIZE_TYPE_UNSPECIFIED = "SIZE_TYPE_UNSPECIFIED"
    PIXEL = "PIXEL"  # Actual height and width in pixels
    ASPECT_RATIO = "ASPECT_RATIO"  # Dimensions as ratio (e.g., 4:1)
    INTERSTITIAL = "INTERSTITIAL"  # Out-of-page ad, requires 1x1
    IGNORED = "IGNORED"  # Size disregarded, requires 1x1
    NATIVE = "NATIVE"  # Rendering-dependent, requires 1x1
    FLUID = "FLUID"  # Auto-sized filling column width, requires 1x1
    AUDIO = "AUDIO"  # Audio ad format, requires 1x1


class Size(BaseModel):
    """
    Dimensions of an AdUnit, LineItem, or Creative.

    For INTERSTITIAL, IGNORED, NATIVE, FLUID, and AUDIO types,
    width and height must be 1x1.
    """

    width: int = Field(description="Width of the ad unit/creative/line item")
    height: int = Field(description="Height of the ad unit/creative/line item")
    size_type: SizeType = Field(
        default=SizeType.PIXEL,
        alias="sizeType",
        description="How dimensions are interpreted",
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def pixel(cls, width: int, height: int) -> "Size":
        """Create a pixel-based size."""
        return cls(width=width, height=height, size_type=SizeType.PIXEL)

    @classmethod
    def aspect_ratio(cls, width: int, height: int) -> "Size":
        """Create an aspect ratio size (e.g., 4:1)."""
        return cls(width=width, height=height, size_type=SizeType.ASPECT_RATIO)

    @classmethod
    def interstitial(cls) -> "Size":
        """Create an interstitial (out-of-page) size."""
        return cls(width=1, height=1, size_type=SizeType.INTERSTITIAL)

    @classmethod
    def native(cls) -> "Size":
        """Create a native ad size."""
        return cls(width=1, height=1, size_type=SizeType.NATIVE)

    @classmethod
    def fluid(cls) -> "Size":
        """Create a fluid (responsive) size."""
        return cls(width=1, height=1, size_type=SizeType.FLUID)

    @classmethod
    def audio(cls) -> "Size":
        """Create an audio ad size."""
        return cls(width=1, height=1, size_type=SizeType.AUDIO)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "width": self.width,
            "height": self.height,
            "sizeType": self.size_type.value,
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        if self.size_type == SizeType.PIXEL:
            return f"{self.width}x{self.height}"
        elif self.size_type == SizeType.ASPECT_RATIO:
            return f"{self.width}:{self.height}"
        return self.size_type.value


# Common ad sizes
COMMON_SIZES = {
    # Display
    "MEDIUM_RECTANGLE": Size.pixel(300, 250),
    "LEADERBOARD": Size.pixel(728, 90),
    "WIDE_SKYSCRAPER": Size.pixel(160, 600),
    "HALF_PAGE": Size.pixel(300, 600),
    "LARGE_RECTANGLE": Size.pixel(336, 280),
    "BILLBOARD": Size.pixel(970, 250),
    # Mobile
    "MOBILE_BANNER": Size.pixel(320, 50),
    "LARGE_MOBILE_BANNER": Size.pixel(320, 100),
    "MOBILE_INTERSTITIAL": Size.interstitial(),
    # Video
    "VIDEO_INLINE": Size.pixel(640, 360),
    # Special
    "NATIVE": Size.native(),
    "FLUID": Size.fluid(),
}
