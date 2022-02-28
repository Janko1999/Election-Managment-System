from flask import Flask, request, Response, jsonify, make_response;
from configurations import Configuration
from models import database, User, UserRole;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from adminDecoration import roleCheck;

application = Flask ( __name__ );
application.config.from_object (Configuration);

@application.route ( "/register", methods = ["POST"] )
def register ( ):
    jmbg = request.json.get ("jmbg", "");
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );
    forename = request.json.get ( "forename", "" );
    surname = request.json.get ( "surname", "" );

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;
    forenameEmpty = len ( forename ) == 0;
    surnameEmpty = len ( surname ) == 0;
    jmbgEmpty = len(jmbg)==0;
    if ( jmbgEmpty):
        return make_response(jsonify ( message="Field jmbg is missing."), 400);
    if ( emailEmpty):
        return make_response(jsonify ( message="Field email is missing."), 400);
    if ( passwordEmpty):
        return make_response(jsonify ( message="Field password is missing."), 400);
    if ( forenameEmpty):
        return make_response(jsonify ( message="Field forename is missing."), 400);
    if ( surnameEmpty):
        return make_response(jsonify ( message="Field surname is missing."), 400);
    if(len(jmbg)!=13):
        return make_response(jsonify ( message="Invalid jmbg."), 400);
    else:
        dan=int(jmbg[0:2]);
        mesec=int(jmbg[2:4]);
        godina=int(jmbg[4:7]);
        region=int(jmbg[7:9]);
        num=int(jmbg[9:12]);
        if(dan<0 or dan>31 or mesec<0 or mesec>12 or godina<0 or godina>999 or region<70 or region>99 or num<0 or num>999):
            return make_response(jsonify ( message="Invalid jmbg."), 400);
    result = parseaddr ( email );
    if ( len ( result[1] ) == 0 ):
        return make_response(jsonify ( message="Invalid Email."), 400);

    #dodati proveru velikog, malog slova i broja
    if(len( password )<8):
        return make_response(jsonify ( message="Invalid password."), 400);
    user = User.query.filter(User.email == email).first();
    if(user is not None):
        return make_response(jsonify(message="Email already exists"), 400);


    user = User ( jmbg=jmbg, email = email, password = password, forename = forename, surname = surname );
    database.session.add ( user );
    database.session.commit ( );

    userRole = UserRole ( userId = user.jmbg, roleId = 2 );
    database.session.add ( userRole );
    database.session.commit ( );

    return make_response(jsonify ( message="Registration successful"), 200);

jwt = JWTManager ( application );

@application.route ( "/login", methods = ["POST"] )
def login ( ):
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;

    if ( emailEmpty):
        return make_response(jsonify ( message="Field email is missing"), 400);
    if(passwordEmpty):
        return make_response(jsonify ( message="Field password is missing"), 400);
    result = parseaddr(email);
    if (len(result[1]) == 0):
        return make_response(jsonify ( message="Invalide email"), 400);
    user = User.query.filter ( and_ ( User.email == email, User.password == password ) ).first ( );

    if ( not user ):
        return make_response(jsonify(message="Invalid credentials"), 400);

    additionalClaims = {
            "jmbg": user.jmbg,
            "forename": user.forename,
            "surname": user.surname,
            "roles": [ str ( role ) for role in user.roles ]
    }

    accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims );
    refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims );

    # return Response ( accessToken, status = 200 );
    return jsonify ( accessToken = accessToken, refreshToken = refreshToken );

@application.route ( "/check", methods = ["POST"] )
@jwt_required ( )
def check ( ):
    return "Token is valid!";

@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):
    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );

    additionalClaims = {
            "jmbg": refreshClaims["jmbg"],
            "forename": refreshClaims["forename"],
            "surname": refreshClaims["surname"],
            "roles": refreshClaims["roles"]
    };

    return Response ( create_access_token ( identity = identity, additional_claims = additionalClaims ), status = 200 );
@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def deleteUser ( ):
    email=request.json.get("email", "");
    emailEmpty=len(email)==0;
    if(emailEmpty):
        return make_response(jsonify ( message="Field email is missing"), 400);
    result = parseaddr(email);
    if (len(result[1]) == 0):
        return make_response(jsonify ( message="Invalid email"), 400);
    user=User.query.filter(User.email==email).first();
    if(user is not None):
        database.session.delete(user);
        database.session.commit();
        return make_response(jsonify ( message="Ok"), 200);
    else:
        return make_response(jsonify ( message="Unknown User"), 400);
@application.route ( "/", methods = ["GET"] )
def index (  ):
    return "Hello world!";
if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, host="0.0.0.0", port = 5002 );
