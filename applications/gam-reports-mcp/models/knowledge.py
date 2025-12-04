"""Domain knowledge models for company context."""

from pydantic import BaseModel, Field


class Domain(BaseModel):
    """A known domain in your network."""

    name: str
    ad_units: list[str] = Field(default_factory=list)


class App(BaseModel):
    """A known mobile app in your network."""

    name: str
    app_id: str = Field(description="Android package name or iOS App Store ID")
    platform: str = Field(description="android or ios")
    ad_units: list[str] = Field(default_factory=list)


class AdStrategy(BaseModel):
    """An ad monetization strategy."""

    name: str
    description: str
    typical_dimensions: list[str] = Field(default_factory=list)
    typical_metrics: list[str] = Field(default_factory=list)


class ReportTemplate(BaseModel):
    """A predefined report template."""

    name: str
    description: str
    dimensions: list[str]
    metrics: list[str]
    default_date_range_days: int = 7


# Default knowledge - customize for your network
KNOWN_DOMAINS: list[Domain] = [
    # Brazil - Portuguese
    Domain(name="easydinheiro.com", ad_units=[]),
    Domain(name="unum.com.br", ad_units=[]),
    Domain(name="vouquitar.com", ad_units=[]),
    Domain(name="solicitecartao.com", ad_units=[]),
    Domain(name="pecaoseu.com", ad_units=[]),
    Domain(name="helpcartao.com", ad_units=[]),
    Domain(name="plusdin.com.br", ad_units=[]),
    Domain(name="sm.com.br", ad_units=[]),
    # Mexico - Spanish
    Domain(name="mejoresopciones.com.mx", ad_units=[]),
    Domain(name="tarjetaahora.com.mx", ad_units=[]),
    # Argentina - Spanish
    Domain(name="tarjetasargentinas.com", ad_units=[]),
    # LatAm/Spanish General
    Domain(name="tarjetaahora.com", ad_units=[]),
    Domain(name="batkredit.com", ad_units=[]),
    Domain(name="kredinow.com", ad_units=[]),
    # US/English
    Domain(name="gotallcards.com", ad_units=[]),
    Domain(name="cardfacil.com", ad_units=[]),
    Domain(name="justgreatcards.com", ad_units=[]),
    Domain(name="availablecards.com", ad_units=[]),
    Domain(name="wheresmycard.com", ad_units=[]),
    Domain(name="cashcardpro.com", ad_units=[]),
    Domain(name="moneycredithub.com", ad_units=[]),
    # Germany - German
    Domain(name="dekreditkarte.com", ad_units=[]),
    Domain(name="dekredit.com", ad_units=[]),
    # Other/Traffic
    Domain(name="ttdtm.com", ad_units=[]),
    Domain(name="athivor.com", ad_units=[]),
    Domain(name="antvora.com", ad_units=[]),
    Domain(name="tenliva.com", ad_units=[]),
]

KNOWN_APPS: list[App] = [
    App(name="Plusdin Android", app_id="br.com.plusdin.plusdin_mobile", platform="android", ad_units=[]),
    App(name="Plusdin iOS", app_id="6443685698", platform="ios", ad_units=[]),
]

# Ad Exchange metrics used for media arbitrage analysis
AD_EXCHANGE_METRICS = [
    "AD_EXCHANGE_AD_REQUESTS",
    "AD_EXCHANGE_IMPRESSIONS",
    "AD_EXCHANGE_CLICKS",
    "AD_EXCHANGE_CTR",
    "AD_EXCHANGE_CPC",
    "AD_EXCHANGE_AVERAGE_ECPM",
    "AD_EXCHANGE_REVENUE",
    "AD_EXCHANGE_MATCH_RATE",
    "AD_EXCHANGE_DELIVERY_RATE",
    "AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE",
    "DROPOFF_RATE",
]

# Mediation metrics for mobile app revenue analysis
APP_MEDIATION_METRICS = [
    "YIELD_GROUP_IMPRESSIONS",
    "YIELD_GROUP_ESTIMATED_REVENUE",
    "YIELD_GROUP_MEDIATION_FILL_RATE",
    "YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM",
]

AD_STRATEGIES: list[AdStrategy] = [
    AdStrategy(
        name="media_arbitrage",
        description="Media arbitrage: buy traffic via paid media, monetize with 100% Open Auction/Ad Exchange. Track performance by traffic source (src key-value) and URL to optimize ROI.",
        typical_dimensions=["DATE", "CUSTOM_CRITERIA", "URL_NAME", "AD_UNIT_NAME"],
        typical_metrics=AD_EXCHANGE_METRICS,
    ),
    AdStrategy(
        name="open_auction",
        description="100% Open Auction monetization via Ad Exchange - focus on programmatic demand optimization",
        typical_dimensions=["DATE", "AD_UNIT_NAME", "DEMAND_CHANNEL_NAME"],
        typical_metrics=AD_EXCHANGE_METRICS,
    ),
    AdStrategy(
        name="app_mediation",
        description="Mobile app mediation: monetize apps through multiple ad networks (AdMob, Meta, Unity, etc.) via waterfall or bidding. Track revenue by network and yield group.",
        typical_dimensions=["DATE", "MOBILE_APP_ID", "YIELD_PARTNER_NAME", "YIELD_GROUP_NAME", "AD_UNIT_NAME"],
        typical_metrics=APP_MEDIATION_METRICS,
    ),
]

REPORT_TEMPLATES: list[ReportTemplate] = [
    ReportTemplate(
        name="media_arbitrage_daily",
        description="Daily performance by Traffic Source → URL → Ad Unit. Primary report for media arbitrage optimization - compare traffic sources ROI.",
        dimensions=["DATE", "CUSTOM_CRITERIA", "URL_NAME", "AD_UNIT_NAME"],
        metrics=AD_EXCHANGE_METRICS,
        default_date_range_days=7,
    ),
    ReportTemplate(
        name="url_performance",
        description="Daily URL → Ad Unit performance without traffic source breakdown. Use for trend analysis - comparing URL performance over time.",
        dimensions=["DATE", "URL_NAME", "AD_UNIT_NAME"],
        metrics=AD_EXCHANGE_METRICS,
        default_date_range_days=7,
    ),
    ReportTemplate(
        name="traffic_source_comparison",
        description="Compare traffic source (src) performance across all URLs. Use to identify best performing sources for scaling.",
        dimensions=["DATE", "CUSTOM_CRITERIA"],
        metrics=AD_EXCHANGE_METRICS,
        default_date_range_days=7,
    ),
    ReportTemplate(
        name="ad_unit_breakdown",
        description="Performance by ad unit placement. Analyze which positions perform best (Topo = above-fold, etc).",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=AD_EXCHANGE_METRICS,
        default_date_range_days=7,
    ),
    ReportTemplate(
        name="app_performance",
        description="Mobile app performance report. Use MOBILE_APP_ID dimension to filter: Android=br.com.plusdin.plusdin_mobile, iOS=6443685698",
        dimensions=["DATE", "MOBILE_APP_ID", "MOBILE_APP_NAME", "AD_UNIT_NAME"],
        metrics=AD_EXCHANGE_METRICS,
        default_date_range_days=7,
    ),
    ReportTemplate(
        name="app_mediation",
        description="App mediation revenue by network. Track revenue from AdMob, Meta, Unity, etc. Filter by MOBILE_APP_ID: Android=br.com.plusdin.plusdin_mobile, iOS=6443685698",
        dimensions=["DATE", "MOBILE_APP_ID", "YIELD_PARTNER_NAME", "YIELD_GROUP_NAME", "AD_UNIT_NAME"],
        metrics=APP_MEDIATION_METRICS,
        default_date_range_days=7,
    ),
]
