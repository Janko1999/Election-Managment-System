from datetime import timedelta;
import os;

databaseUrl = os.environ["DATABASE_URL"];


class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/elections";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta ( minutes = 60 );
    JWT_REFRESH_TOKEN_EXPIRES = timedelta ( days = 30 );
    REDIS_HOST="localhost";
    REDIS_VOTES_LIST="votes";
