from flask import Flask, request, Response, jsonify, make_response;
from Configurations import Configuration;
from models import database, Vote, Election, ParticipantElection, Participant;
from flask_jwt_extended import verify_jwt_in_request, get_jwt;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity;
import csv;
from sqlalchemy import and_;
import io;
import json;
from redis import Redis;
import datetime;

application = Flask(__name__);
application.config.from_object(Configuration);

jwt = JWTManager(application);


@application.route("/vote", methods=["POST"])
@jwt_required()
def vote():
    today = datetime.datetime.now();
    try:
        file = request.files["file"];
    except:
        return make_response(jsonify(message="Field file missing"));
    content = file.stream.read().decode("utf-8");
    stream = io.StringIO(content);
    reader = csv.reader(stream);
    verify_jwt_in_request();
    claims = get_jwt();
    if ("jmbg" in claims):
        jmbg = claims["jmbg"];
    votes = [];
    i = 0;
    for row in reader:
        if (len(row) != 2):
            return make_response(jsonify(message=f"Incorrect number of values on line {i}"), 400);
        if (int(row[1]) < 0):
            return make_response(jsonify(message=f"Incorrect poll number on line {i}"), 400);
        vot = Vote(guid=int(row[0]), participant=int(row[1]), date=today, election=0, invalid=False, jmbg=jmbg);
        votes.append(vot);
        i = i + 1;

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for vot in votes:
            redis.rpush(Configuration.REDIS_VOTES_LIST, str(vot));

    return str(Vote.query.all());


@application.route("/getResults", methods=["GET"])
@jwt_required()
def getResults():
    try:
        id = request.args["ELECTION_ID"];
    except:
        return make_response(jsonify(message="Field id is missing"), 400);
    election = Election.query.filter(Election.id == id).first();
    if (election is None):
        return make_response(jsonify(message="Election does not exist"), 400);
    # if(election.end>date.today()):
    #     return make_response(jsonify(message="Election is ongoing"),400);
    participants = [];
    if (election.individual == True):
        for participant in election.participants:
            pe = ParticipantElection.query.filter(and_(
                ParticipantElection.participantId == participant.id,
                ParticipantElection.electionId == election.id
            )).first();
            votes = Vote.query.filter(
                Vote.election == election.id
            ).all();
            myV = Vote.query.filter(
                and_(
                    Vote.election == election.id,
                    Vote.participant == pe.pollNumber
                )
            ).all();
            myVotes = len(myV);
            allVotes = len(votes);
            result = myVotes / allVotes;
            jsonStr = {'pollNumber': str(pe.pollNumber), 'name': str(participant.name), 'result': str(result)};
            participants.append(json.dumps(jsonStr));
    else:
        participants = ParticipantElection.query.filter(
            ParticipantElection.electionId == election.id
        ).all();
        first = True;
        for p in participants:
            if (p.result != 0):
                first = False;
        if (first):
            for i in range(250):
                quotient = 0;
                id = 0;
                for participant in participants:
                    myVotes = Vote.query.filter(and_(
                        participant.pollNumber == Vote.participant,
                        participant.electionId == Vote.election
                    )).all();
                    myVotescnt = len(myVotes);
                    myQuotient = myVotescnt / (participant.result + 1);
                    if (myQuotient > quotient):
                        quotient = myQuotient;
                        id = participant.id;
                pe = ParticipantElection.query.filter(and_(ParticipantElection.participantId == id,
                                                           ParticipantElection.electionId == election.id)).first();
                pe.result = pe.result + 1;
                database.session.add(pe);
                database.session.commit();
        invalidVotes = Vote.query.filter(and_(Vote.election == election.id, Vote.invalid == True)).all();
        return f"participants={str(participants)}, invalidVotes={str(invalidVotes)}";


@application.route("/", methods=["GET"])
def index():
    return "Hello world!";


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5004);
