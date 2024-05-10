from graphene import Enum

class CreatedWithIn(Enum):
    TWENTY_FOUR_HOURS = 1 * 24
    SEVEN_DAYS = 7 * 24
    MONTH = 1 * 30 * 24
    SIX_MONTH = 6 * 30 * 24
    YEAR = 12 * 30 * 24

class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    NOT_PAID = "NOT_PAID"
    EXPIRED = "EXPIRED"
    
class SubscriptionPlan(Enum):
    STARTER_PLAN = "Starter_Plan"
    BUILDING_PLAN = "Building_Plan"
    GROWTH_PLAN = "Growth_Plan"

class DateFilter(Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    