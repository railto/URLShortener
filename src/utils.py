import string
import random

from flask import jsonify
from sqlalchemy.exc import IntegrityError
from flask_login import current_user

from src import db
from src.models import Link


def create_link(params):
    try:
        if "link" in params and len(params["link"]) > 0:
            link = params["link"]
        else:
            link = link_generator()
        item = Link(
            link=link,
            visits="0",
            url=params["url"],
            user_id=current_user.id,
            notes=params["notes"],
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(success=True, link=link)
    except IntegrityError:
        return jsonify(success=False)


def link_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))
