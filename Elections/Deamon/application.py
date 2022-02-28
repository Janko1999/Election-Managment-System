from flask import Flask, request, Response, jsonify, make_response;
from Configurations import Configuration;
from models import database, Vote, Election, ParticipantElection, Participant;

from flask_jwt_extended import JWTManager;
import datetime;
from redis import Redis;

application = Flask(__name__);
application.config.from_object(Configuration);

jwt = JWTManager(application);



@application.route("/", methods=["GET"])
def index():
    while(True):
        with Redis(host=Configuration.REDIS_HOST) as redis:
            vote=redis.lpop(Configuration.REDIS_VOTES_LIST);
            if(vote is not None):
                inf=str(vote).split(",");
                id=inf[0];
                pollNumber=inf[1];
                dateTime=inf[2];
                jmbg=inf[4];
                date=datetime.datetime.fromisoformat(dateTime);
                elections=Election.query.all();
                found=False;
                electionId=-1;
                el=None;
                for election in elections:
                    if(election.start<=date and election.end>=date):
                        found=True;
                        el=election;
                if(found):
                    votes=Vote.query.all();
                    foundGuid=False;
                    for vo in votes:
                        if vo.guid==id:
                            foundGuid=True;
                    if(foundGuid):
                        v=Vote(jmbg=jmbg, guid=id, participant=pollNumber, date=date, election=electionId, invalid=True, reason="DuplicateBallot");
                        database.session.add(v);
                        database.session.commit();
                    else:
                        foundPoll=False;
                        for polls in el.participants:
                            if(polls==pollNumber):
                                foundPoll=True;
                        if(foundPoll==False):
                            v = Vote(jmbg=jmbg, guid=id, participant=pollNumber, date=date, election=electionId,
                                     invalid=True, reason="Invalid poll Number");
                            database.session.add(v);
                            database.session.commit();
                        else:
                            v = Vote(jmbg=jmbg, guid=id, participant=pollNumber, date=date, election=electionId,
                                     invalid=False, reason="");
                            database.session.add(v);
                            database.session.commit();



if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5005);
