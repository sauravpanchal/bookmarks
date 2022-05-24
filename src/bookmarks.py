from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.consts.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from src.database import Bookmarks, db

bookmarks = Blueprint("bookmarks", 
                __name__, 
                url_prefix = "/api/v1/bookmarks")

# @bookmarks.get("/")
# def get_all():
#     return {"bookmarks": []}

@bookmarks.route("/", methods = ["POST", "GET"]) #route & endpoints are same
@jwt_required()
def get_or_post_bookmarks():
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

        data = list()

        for bookmarks in bookmarks_list:
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
                    "page": bookmarks.page,
                    "pages": bookmarks.pages,
                    "total_count": bookmarks.total,
                    "prev_page": bookmarks.prev_num,
                    "next_page": bookmarks.next_num,
                    "has_prev": bookmarks.has_prev,
                    "has_next": bookmarks.has_next,
                  }

        return jsonify({"data": data, "meta": current}), HTTP_200_OK
        
                          