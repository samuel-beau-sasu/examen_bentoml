# src/service.py
import numpy as np
import bentoml
from pydantic import BaseModel, Field, ConfigDict
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from datetime import datetime, timedelta

# Ne pas hardcoder les secrets en production
JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"

USERS = {
    "user123": "password123",
    "user456": "password456",
}

class Credentials(BaseModel):
    username: str
    password: str

class InputModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    Serial_No: int
    GRE_Score: int
    TOEFL_Score: int
    University_Rating: int
    SOP: float
    LOR: float
    CGPA: float
    Research: int
    #Chance_of_Admit: float

def create_jwt_token(user_id: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": user_id, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.endswith("/predict"):
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})
            try:
                token = token.split()[1]  # Bearer <token>
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
            request.state.user = payload.get("sub")
        return await call_next(request)

@bentoml.service
class RFModelService:
    def __init__(self):
        self.model = bentoml.sklearn.load_model("admission_gb:latest")

    @bentoml.api
    def predict_array(self, features: list[float]) -> list[float]:
        x = np.array(features, dtype=float).reshape(1, -1)
        pred = self.model.predict(x)
        return pred.tolist()

@bentoml.service(
    # Dire à Swagger qu'on utilise Bearer JWT
    http={
        "security_schemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "security": [{"BearerAuth": []}]
    }
)
class RFClassifierService:
    model_service = bentoml.depends(RFModelService)

    @bentoml.api(route="/login")
    def login(self, credentials: Credentials):
        if USERS.get(credentials.username) == credentials.password:
            token = create_jwt_token(credentials.username)
            return {"token": token}
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    @bentoml.api(route="/predict")
    def predict(self, input_data: InputModel):
        features = [
            input_data.Serial_No, input_data.GRE_Score, input_data.TOEFL_Score,
            input_data.University_Rating, input_data.SOP, input_data.LOR,
            input_data.CGPA, input_data.Research,
        ]
        pred = self.model_service.predict_array(features)
        return {"prediction": pred}

RFClassifierService.add_asgi_middleware(JWTAuthMiddleware)
