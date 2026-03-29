from typing import Literal, Any
from pydantic import BaseModel, Field, field_validator, model_validator


YesNo = Literal["Yes", "No"]
Gender = Literal["Male", "Female"]
SeniorCitizenFlag = Literal[0, 1]

MultipleLinesType = Literal["Yes", "No", "No phone service"]
InternetServiceType = Literal["DSL", "Fiber optic", "No"]
InternetAddonType = Literal["Yes", "No", "No internet service"]

ContractType = Literal["Month-to-month", "One year", "Two year"]

PaymentMethodType = Literal[
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]


class ScoreRequest(BaseModel):
    customerID: str | None = None

    gender: Gender
    SeniorCitizen: SeniorCitizenFlag
    Partner: YesNo
    Dependents: YesNo

    tenure: int = Field(ge=0, le=72)

    PhoneService: YesNo
    MultipleLines: MultipleLinesType
    InternetService: InternetServiceType

    OnlineSecurity: InternetAddonType
    OnlineBackup: InternetAddonType
    DeviceProtection: InternetAddonType
    TechSupport: InternetAddonType
    StreamingTV: InternetAddonType
    StreamingMovies: InternetAddonType

    Contract: ContractType
    PaperlessBilling: YesNo
    PaymentMethod: PaymentMethodType

    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float | None = Field(default=None, ge=0)

    # NORMALIZATION LAYER
    @field_validator(
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "Contract",
        "PaperlessBilling",
        "PaymentMethod",
        mode="before",
    )
    @classmethod
    def normalize_string_fields(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        cleaned = " ".join(value.strip().split())
        lowered = cleaned.lower()

        mapping = {
            "male": "Male",
            "female": "Female",
            "yes": "Yes",
            "no": "No",
            "no phone service": "No phone service",
            "dsl": "DSL",
            "fiber optic": "Fiber optic",
            "no internet service": "No internet service",
            "month-to-month": "Month-to-month",
            "one year": "One year",
            "two year": "Two year",
            "electronic check": "Electronic check",
            "mailed check": "Mailed check",
            "bank transfer (automatic)": "Bank transfer (automatic)",
            "credit card (automatic)": "Credit card (automatic)",
        }

        return mapping.get(lowered, cleaned)


    # CROSS-FIELD VALIDATION
    @model_validator(mode="after")
    def validate_dependencies(self):
        # PhoneService → MultipleLines
        if self.PhoneService == "No" and self.MultipleLines != "No phone service":
            raise ValueError(
                "MultipleLines must be 'No phone service' when PhoneService is 'No'"
            )

        if self.PhoneService == "Yes" and self.MultipleLines == "No phone service":
            raise ValueError(
                "MultipleLines cannot be 'No phone service' when PhoneService is 'Yes'"
            )

        # InternetService → all dependent services
        internet_dependent_fields = [
            self.OnlineSecurity,
            self.OnlineBackup,
            self.DeviceProtection,
            self.TechSupport,
            self.StreamingTV,
            self.StreamingMovies,
        ]

        if self.InternetService == "No":
            if any(v == "Yes" for v in internet_dependent_fields):
                raise ValueError(
                    "Internet-dependent services cannot be 'Yes' when InternetService is 'No'"
                )

        if self.InternetService != "No":
            if any(v == "No internet service" for v in internet_dependent_fields):
                raise ValueError(
                    "Internet-dependent services cannot be 'No internet service' when InternetService is not 'No'"
                )

        return self


class ScoreResponse(BaseModel):
    model_name: str
    model_version: str
    probability: float = Field(ge=0, le=1)
    prediction: Literal[0, 1]
    threshold: float = Field(ge=0, le=1)