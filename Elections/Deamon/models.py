from flask_sqlalchemy import SQLAlchemy;
from flask import jsonify;
import json;

database =SQLAlchemy ( );

class ParticipantElection (database.Model):
    __tablename__ = "participantelection";

    id = database.Column(database.Integer, primary_key=True);
    participantId= database.Column(database.Integer, database.ForeignKey("participant.id"), nullable=False);
    electionId = database.Column(database.Integer, database.ForeignKey("election.id"), nullable=False);
    result = database.Column(database.Float, nullable=False);
    pollNumber = database.Column(database.Integer, nullable=False);
    def __repr__(self):
        return f"pollNumber:{self.pollNumber},results:{self.result}"
class Election (database.Model):

    __tablename__ = "election";
    id = database.Column(database.Integer, primary_key=True);
    start = database.Column(database.DateTime, nullable=False);
    end = database.Column(database.DateTime, nullable=False);
    individual=database.Column(database.Boolean, nullable=False);
    participants=database.relationship("Participant", secondary=ParticipantElection.__table__, back_populates="elections");

    def __repr__(self):
        data_set = {"id": self.id, "start": str(self.start),"end":str(self.end), "individual": self.individual,"participants":str(self.participants)};
        json_dump = json.dumps(data_set, indent=4);
        return json_dump;
class Participant (database.Model):

    __tablename__ = "participant";
    id= database.Column(database.Integer, primary_key=True);
    name=database.Column(database.String(256), nullable=False);
    individual=database.Column(database.Boolean, nullable=False);
    elections = database.relationship("Election", secondary=ParticipantElection.__table__, back_populates="participants");
    def __repr__ ( self ):
        data_set = {"id":self.id, "name": self.name, "individual": self.individual};
        json_dump = json.dumps(data_set, indent=4);
        return json_dump;

class Vote(database.Model):
    __tablename__="vote";
    jmbg=database.Column(database.Integer, nullable=False);
    guid=database.Column(database.Integer, primary_key=True);
    participant=database.Column(database.Integer, nullable=False);
    date=database.Column(database.DateTime, nullable=False);
    election=database.Column(database.Integer, nullable=False);
    invalid=database.Column(database.Boolean, nullable=False);
    reason=database.Column(database.String(256));
    def __repr__(self):
        return f"{self.guid},{self.participant},{self.date},{self.election},{self.jmbg}";