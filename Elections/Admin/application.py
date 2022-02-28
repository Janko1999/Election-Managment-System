from flask import Flask, request, Response, jsonify, make_response;
from Configurations import Configuration;
from models import database, Participant, Election, ParticipantElection;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from adminDecoration import roleCheck;
application = Flask ( __name__ );
application.config.from_object ( Configuration );
import re;
import datetime;

jwt = JWTManager ( application );
@application.route("/createParticipant", methods=["Post"])
@roleCheck(role="admin")
def createParticipant():
    name=request.json.get("name","");
    individual=request.json.get("individual", "");
    nameEmpty=len(name)==0;
    if(nameEmpty):
        return jsonify(message="Field name is missing");
    participant=Participant(name=name, individual=individual);
    database.session.add(participant);
    database.session.commit();
    return jsonify(id=participant.id);
@application.route("/getParticipants", methods=["GET"])
@roleCheck(role="admin")
def getParticipants():
    participants=Participant.query.all();
    part=str(participants);
    return f"participants : {part}";

@application.route("/getElections", methods=["Get"])
@roleCheck(role="admin")
def getElections():
    elections=Election.query.all();
    return f"Elections: {str(elections)}";
@application.route("/createElection", methods=["POST"])
@roleCheck(role="admin")
def createElection():
    start =request.json.get("start");
    end=request.json.get("end");
    individual=request.json.get("individual");
    participants=request.json.get("participants");
    startEmpty=len(start)==0;
    endEmpty=len(end)==0;
    participantsEmpty=len(participants)==0;
    if(startEmpty):
        return make_response(jsonify(message="Field start is missing"), 400);
    if (endEmpty):
        return make_response(jsonify(message="Field end is missing"), 400);
    if (participantsEmpty):
        return make_response(jsonify(message="Field participants is missing"), 400);
    if(re.search("^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d$",start) is None):
        return(make_response(jsonify(message="Invalid date and time start")));
    if (re.search("^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d$", end) is None):
        return (make_response(jsonify(message="Invalid date and time end")));
    start=datetime.datetime.fromisoformat(start);
    end=datetime.datetime.fromisoformat(end);
    if(start>end):
        return make_response(jsonify(message="Invalid date and time"), 400);
    elections=Election.query.all();
    for election in elections:
        if(election.start<=start and election.end>=end):
            return make_response(jsonify(message="Invalid date and time"), 400);
    if(len(participants)<2):
        return make_response(jsonify(message="Invalid participants"), 400);
    i = 1;
    for participant in participants:
        part = Participant.query.filter(
                and_(Participant.id == participant,  Participant.individual==individual)).first();
        if(part is None):
            return make_response(jsonify(message="Invalid Participant"), 400);
    election = Election(start=start, end=end, individual=individual);
    database.session.add(election);
    database.session.commit();
    for participant in participants:
        database.session.add(ParticipantElection(participantId=participant, electionId=election.id, pollNumber=i, result=0.00));
        i=i+1;
    database.session.commit();
    pollNumbers=[];

    for i in range(len(participants)):
        j=i+1;
        pollNumbers.append(j);

    return make_response(jsonify(pollNumbers=pollNumbers), 200);
@application.route ( "/", methods = ["GET"] )
def index ( ):
    return "Hello world!";
if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, host = "0.0.0.0", port = 5003 );
