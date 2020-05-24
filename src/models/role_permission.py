from src.models.Model import db


class RolePermissionModel(db.Model):
    __tablename__ = 'role_permission'

    id = db.Column(db.Integer, primary_key=True)
    roleid = db.Column(db.Integer)
    permissionid = db.Column(db.Integer)


    def __init__(self, roleid, permissionid):
        self.roleid = roleid
        self.permissionid = permissionid


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()