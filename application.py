from fastapi import FastAPI
from core.config import configure_cors, Settings
from core.bootstrap import bootstrap

settings = Settings()
app = FastAPI(debug=settings.debug, title="StorageBucket", lifespan=bootstrap)
configure_cors(app)