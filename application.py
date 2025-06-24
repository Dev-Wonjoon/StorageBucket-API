from fastapi import FastAPI
from core import settings
from core.config import configure_cors
from core.bootstrap import bootstrap

app = FastAPI(debug=settings.debug, title="StorageBucket", lifespan=bootstrap)
configure_cors(app)