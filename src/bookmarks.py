from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.consts.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from src.database import Bookmarks, db

bookmarks = Blueprint("bookmarks", 
                __name__, 
                url_prefix = "/api/v1/bookmarks")

# @bookmarks.get("/")
# def get_all():
#     return {"bookmarks": []}

@bookmarks.route("/", methods = ["POST", "GET"]) #route & endpoints are same
@jwt_required() # comment this line while testing server side errorhandler's behaviour
def get_or_post_bookmarks():
    # print(some_variable) # create server side error like name error then change flask environvent to production then you can see 500 or other server side error handling by our error handler
    user = get_jwt_identity()
    if request.method == "POST":
        body = request.get_json().get("body", "")
        url = request.get_json().get("url", "")

        if not validators.url(url):
            return jsonify({
                            "error": "Not valid URL !"
                          }), HTTP_400_BAD_REQUEST

        if Bookmarks.query.filter_by(url = url).first():
            return jsonify({
                            "error": "URL already exist"
                          }), HTTP_409_CONFLICT

        bookmarks = Bookmarks(url = url, body = body, user_id = user)
        db.session.add(bookmarks)
        db.session.commit()

        return jsonify({
                        "id": bookmarks.id,
                        "url": bookmarks.url,
                        "short_url": bookmarks.short_url,
                        "visit": bookmarks.visits,
                        "body": bookmarks.body,
                        "creted_at": bookmarks.created_at,
                        "updated_at": bookmarks.updated_at,
                      }), HTTP_201_CREATED
    else:
        page = request.args.get("page", 1, type = int) # by default it'll send user to first page if there's no page specified in URL
        per_page = request.args.get("per_page", 5, type = int)

        bookmarks_list = Bookmarks.query.filter_by(user_id = user).paginate(page = page, per_page = per_page)

        data = []

        for bookmarks in bookmarks_list.items:
            data.append({
                        "id": bookmarks.id,
                        "url": bookmarks.url,
                        "short_url": bookmarks.short_url,
                        "visit": bookmarks.visits,
                        "body": bookmarks.body,
                        "creted_at": bookmarks.created_at,
                        "updated_at": bookmarks.updated_at,
                       })
        
        current = {
                    "page": bookmarks_list.page,
                    "pages": bookmarks_list.pages,
                    "total_count": bookmarks_list.total,
                    "prev_page": bookmarks_list.prev_num,
                    "next_page": bookmarks_list.next_num,
                    "has_prev": bookmarks_list.has_prev,
                    "has_next": bookmarks_list.has_next,
                }

        return jsonify({"data": data, "meta": current}), HTTP_200_OK
        
@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    user = get_jwt_identity()

    bookmark = Bookmarks.query.filter_by(user_id = user, id = id).first()
    
    if not bookmark:
        return jsonify({"message": "Bookmark not found !"}), HTTP_404_NOT_FOUND
    
    return jsonify({
                    "id": bookmark.id,
                    "url": bookmark.url,
                    "short_url": bookmark.short_url,
                    "visit": bookmark.visits,
                    "body": bookmark.body,
                    "creted_at": bookmark.created_at,
                    "updated_at": bookmark.updated_at,
                    }), HTTP_200_OK
    
@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def edit_bookmarks(id):
    user = get_jwt_identity()

    bookmark = Bookmarks.query.filter_by(user_id = user, id = id).first()

    if not bookmark:
        return jsonify({'message': "Bookmark not found !"}), HTTP_404_NOT_FOUND
    
    body = request.get_json().get("body", "")
    url = request.get_json().get("url", "")

    # validating URL
    if not validators.url(url):
        return jsonify({
                        "error": "Not valid URL !"
                        }), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
                        "id": bookmark.id,
                        "url": bookmark.url,
                        "short_url": bookmark.short_url,
                        "visit": bookmark.visits,
                        "body": bookmark.body,
                        "creted_at": bookmark.created_at,
                        "updated_at": bookmark.updated_at,
                      }), HTTP_200_OK

@bookmarks.get("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    user = get_jwt_identity()

    bookmark = Bookmarks.query.filter_by(user_id = user, id = id).first()
    
    if not bookmark:
        return jsonify({"message": "Bookmark not found !"}), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@bookmarks.get("/linkstats")
@jwt_required()
def get_linkstats():
    user = get_jwt_identity()
    data = list()

    bookmark = Bookmarks.query.filter_by(user_id = user).all()