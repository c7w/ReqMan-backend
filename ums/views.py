from rest_framework.decorators import action, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from utils.exceptions import ParamErr
from ums.models import *
from utils.sessions import *
from ums.utils import *
from utils.permissions import GeneralPermission, project_rights, require_login
from django.conf import settings
import hashlib
from utils.model_date import get_timestamp
from rdts.models import Repository

DEFAULT_INVITED_ROLE = "member"

SUCC = Response({"code": 0})
FAIL = Response({"code": 1})


def STATUS(code: int):
    return Response({"code": code})


class UserViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]
    # throttle_classes = [GeneralThrottle]
    permission_classes = [GeneralPermission]

    @action(detail=False, methods=["POST"])
    def check_username_available(self, req: Request):
        name = require(req.data, "name")
        return Response({"code": 1 if name_exist(name) else 0})

    @action(detail=False, methods=["POST"])
    def check_email_available(self, req: Request):
        email = require(req.data, "email")
        return Response({"code": 1 if email_exist(email) else 0})

    @action(
        detail=False,
        methods=["POST"],
        #    throttle_classes=throttle_classes + [SpecialThrottle("register")],
    )
    def register(self, req: Request):
        if req.user:
            return FAIL

        name = require(req.data, "name")
        password = require(req.data, "password")
        email = require(req.data, "email")
        invitation = req.data.get("invitation")
        relation = None
        if invitation:
            relation = ProjectInvitationAssociation.objects.filter(
                invitation=invitation
            ).first()
            if not relation:
                return Response({"code": 2})

        # print(name_valid(name))
        if (
            name_valid(name)
            and not name_exist(name)
            and email_valid(email)
            and not email_exist(email)
        ):

            usr = User.objects.create(name=name, password=password, email=email)
            if relation:
                UserProjectAssociation.objects.create(
                    project=relation.project, user=usr, role=relation.role
                )
            bind_session_id(get_session_id(req), usr)
            return SUCC

        return Response({"code": 1})

    @action(detail=False, methods=["POST"])
    def login(self, req: Request):
        if req.user:
            return Response({"code": 1})

        identity = require(req.data, "identity")
        password = require(req.data, "password")

        if name_valid(identity):
            usr = name_exist(identity)
            if usr and usr.name == identity:
                if usr.password == password:
                    bind_session_id(req.auth["sessionId"], usr)
                    return SUCC
                else:
                    return Response({"code": 3})
            else:
                return Response({"code": 2})
        elif email_valid(identity):
            usr = get_user_by_major_email(identity)
            if usr:
                if usr.password == password:
                    bind_session_id(get_session_id(req), usr)
                    return SUCC
                else:
                    return Response({"code": 3})
            else:
                return Response({"code": 2})
        else:
            return Response({"code": 2})

    @action(detail=False, methods=["POST"])
    def logout(self, req: Request):
        if not req.user:
            return Response({"code": 1})  # convention in API

        disable_session_id(req.auth["sessionId"])
        return Response({"code": 0})

    @action(detail=False)
    @require_login
    def user(self, req: Request):
        return Response(
            {
                "code": 0,
                "data": {
                    "schedule": {"done": [], "wip": [], "todo": []},
                    **user_and_projects(req.user),
                },
            }
        )

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def modify_user_role(self, req: Request):
        relation = proj_user_assoc(req)["relation"]
        if not relation:
            return FAIL

        role = require(req.data, "role")
        if role not in Role:
            return FAIL

        relation.role = role
        relation.save()

        return SUCC

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def project_rm_user(self, req: Request):
        relation = proj_user_assoc(req)["relation"]
        if not relation:
            return FAIL

        relation.delete()
        return SUCC

    @project_rights([Role.SUPERMASTER, Role.SYS])
    @action(detail=False, methods=["POST"])
    def project_add_user(self, req: Request):
        info = proj_user_assoc(req)

        role = require(req.data, "role")
        if role not in Role:
            return FAIL

        if not info["user"]:
            return STATUS(3)

        # cannot add a user that already exist
        if info["relation"]:
            return FAIL

        UserProjectAssociation.objects.create(
            user=info["user"], project=info["proj"], role=role
        )
        return SUCC

    @action(detail=False, methods=["POST"])
    @require_login
    def create_project(self, req: Request):
        title = require(req.data, "title")
        description = require(req.data, "description")
        avatar = req.data.get("avatar")

        # check length
        if len(title) > PROJECT_TITLE_LEN:
            return STATUS(1)

        if len(description) > PROJECT_DESC_LEN:
            return STATUS(2)

        proj = Project.objects.create(
            title=title, description=description, avatar=avatar if avatar else ""
        )
        UserProjectAssociation.objects.create(
            project=proj, user=req.user, role="supermaster"
        )
        return SUCC

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"], url_path="project")
    def show_project_detail(self, req: Request):
        proj = req.auth["proj"]
        avatar = proj.avatar
        users = [user_to_list(u, proj) for u in all_users().filter(project=proj)]
        proj = proj_to_list(proj)

        return Response(
            {"code": 0, "data": {"project": proj, "users": users, "avatar": avatar}}
        )

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def modify_project(self, req: Request):
        proj = req.auth["proj"]

        title = require(req.data, "title")
        desc = require(req.data, "description")

        # check length
        if len(title) > PROJECT_TITLE_LEN:
            return STATUS(1)

        if len(desc) > PROJECT_DESC_LEN:
            return STATUS(2)

        proj.title = title
        proj.description = desc
        proj.save()

        return SUCC

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def upload_project_avatar(self, req: Request):
        proj = req.auth["proj"]
        # print(req.data)
        avatar = require(req.data, "avatar")

        proj.avatar = avatar
        proj.save()
        return SUCC

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def refresh_invitation(self, req: Request):
        proj = req.auth["proj"]
        inv = invitation_exist(proj, DEFAULT_INVITED_ROLE)

        if inv:
            inv.invitation = gen_invitation()
            inv.save()
        else:
            inv = ProjectInvitationAssociation.objects.create(
                project=proj, role=DEFAULT_INVITED_ROLE, invitation=gen_invitation()
            )

        return Response({"code": 0, "data": {"invitation": inv.invitation}})

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def get_invitation(self, req: Request):
        proj = req.auth["proj"]

        inv = invitation_exist(proj, DEFAULT_INVITED_ROLE)
        if not inv:
            inv = create_inv(proj, DEFAULT_INVITED_ROLE)

        return Response({"code": 0, "data": {"invitation": inv.invitation}})

    @action(detail=False, methods=["POST"])
    @require_login
    def modify_password(self, req: Request):
        prev = require(req.data, "prev")
        curr = require(req.data, "curr")

        if prev != req.user.password:
            return Response({"code": 2})

        req.user.password = curr
        req.user.save()
        return SUCC

    @action(detail=False, methods=["POST"])
    @require_login
    def upload_user_avatar(self, req: Request):
        avatar = require(req.data, "avatar")

        req.user.avatar = avatar
        # TODO: safety check: size

        req.user.save()
        return SUCC

    @action(detail=False, methods=["POST"])
    @require_login
    def user_join_project_invitation(self, req: Request):
        invitation = require(req.data, "invitation")

        relation = ProjectInvitationAssociation.objects.filter(
            invitation=invitation
        ).first()
        if not relation:
            return Response({"code": 2})

        if (
            UserProjectAssociation.objects.filter(
                user=req.user, project=relation.project
            ).first()
            is not None
        ):
            return Response({"code": 1})

        UserProjectAssociation.objects.create(
            user=req.user, project=relation.project, role=relation.role
        )

        return SUCC

    @project_rights([Role.SUPERMASTER, Role.SYS])
    @action(detail=False, methods=["POST"])
    def user_exist(self, req: Request):
        identity = require(req.data, "identity")

        supported = ["id", "name", "email"]
        print(req.data)
        print(identity, type(identity))
        if type(identity) is not dict or "type" not in identity:
            raise ParamErr("no identity type")
        if identity["type"] not in supported:
            raise ParamErr("invalid identity type, only support " + supported.__str__())
        if "key" not in identity:
            raise ParamErr("no identity key")

        user = None
        try:
            if identity["type"] == "id":
                user = all_users().filter(id=intify(identity["key"])).first()
            elif identity["type"] == "name":
                user = all_users().filter(name=str(identity["key"])).first()
            elif identity["type"] == "email":
                user = all_users().filter(email=str(identity["key"]).lower()).first()
        except Exception as e:
            raise ParamErr("unmatched type and key" + e.__str__())

        if user and not user.disabled:
            return Response(
                {"code": 0, "data": {"exist": True, **user_and_projects(user)}}
            )
        else:
            return Response({"code": 0, "data": {"exist": False}})

    @action(detail=False, methods=["POST"])
    @require_login
    def email_request(self, req: Request):  # add and verify or simply verify
        email = require(req.data, "email").lower()  # to be stripped by frontend
        op = require(req.data, "op")

        # parameter check
        email_type = require(req.data, "type")

        if email_type not in ["major", "minor"]:
            raise ParamErr("invalid email type")

        if not email_valid(email):
            return STATUS(6)  # invalid email %%%

        # major email
        if email_type == "major":

            def send_verify_major():
                state, info = new_verify_email(req.user, req.user.email, major=True)
                if not state and info == "freq_exceed":
                    return STATUS(2)  # 2: frequency exceed %%%
                if state:
                    return SUCC
                return FAIL  # mail service unavailable

            if op == "modify":
                if email == req.user.email:
                    return STATUS(8)

                if email_exist(email):
                    return STATUS(12)

                req.user.email = email
                req.user.email_verified = False
                req.user.save()
                req.user.refresh_from_db()
                return send_verify_major()  # already a response

            if op == "verify":
                if req.user.email_verified:
                    return STATUS(7)  # already verified %%%
                return send_verify_major()

            raise ParamErr("unsupported operation for major email")

        # minor email
        def rm(e):
            relation = UserMinorEmailAssociation.objects.filter(
                email=e, user=req.user
            ).first()
            if not relation:
                return 5  # 5: non-exist
            relation.delete()
            return 0

        def add(e):
            if email == req.user.email:
                return 3  # 3: minor and major should not be the same %%%
            relation = UserMinorEmailAssociation.objects.filter(email=email).first()
            if relation:
                return 4  # 4: minor already exist %%%

            UserMinorEmailAssociation.objects.create(user=req.user, email=email)
            state, info = new_verify_email(req.user, e)
            if not state and info == "freq_exceed":
                return 2  # 2: frequency exceed
            if state:
                return 0
            return 1  # mail service unavailable

        if op == "add":
            return STATUS(add(email))
        elif op == "rm":
            return STATUS(rm(email))
        elif op == "modify":
            prev = require(req.data, "previous")

            # email check
            if not email_valid(prev):
                return STATUS(6)

            # remove
            rm_state = rm(prev)
            if rm_state != 0:
                return STATUS(rm_state)

            # then add
            add_state = add(email)
            return STATUS(add_state)

        elif op == "verify":
            minor_relation = UserMinorEmailAssociation.objects.filter(
                email=email
            ).first()
            if not minor_relation:
                return STATUS(10)

            if minor_relation.verified:
                return STATUS(7)  # already verified

            state, info = new_verify_email(req.user, email)
            if not state and info == "freq_exceed":
                return STATUS(2)  # 2: frequency exceed
            if state:
                return SUCC
            return FAIL  # mail service unavailable

        raise ParamErr("unsupported operation for minor email")

    @action(detail=False, methods=["POST"])
    def email_verify_callback(self, req: Request):
        hashcode = require(req.data, "hash")
        relation = PendingVerifyEmail.objects.filter(hash=hashcode).first()
        if not relation:
            return FAIL

        now = get_timestamp()
        if now - relation.createdAt > EMAIL_EXPIRE_SECONDS:
            return STATUS(2)

        # major email
        if relation.is_major:
            if relation.email != relation.user.email:
                relation.delete()
                return STATUS(3)  # record inconsistent with user table
            relation.user.email_verified = True
            relation.user.save()
            relation.delete()
            return SUCC

        # minor email
        minor_relation = UserMinorEmailAssociation.objects.filter(
            email=relation.email
        ).first()
        if not minor_relation:
            return STATUS(3)
        minor_relation.verified = True
        minor_relation.save()
        relation.delete()
        return SUCC

    @action(detail=False, methods=["POST"])
    def email_modify_password_request(self, req: Request):
        email = require(req.data, "email").lower()
        user = all_users().filter(email=email).first()
        if user and user.email_verified:
            hash1 = hashlib.sha256(str(get_timestamp()).encode()).hexdigest()
            PendingModifyPasswordEmail.objects.create(
                user=user,
                email=email,
                hash1=hash1,
            )
            if email_password_reset(email, hash1):
                return SUCC
            return FAIL  # mail service unavailable

        return STATUS(2)

    @action(detail=False, methods=["POST"])
    def email_modify_password_callback(self, req: Request):
        stage = intify(require(req.data, "stage"))

        if stage == 1:
            hash1 = require(req.data, "hash1")
            relation: PendingModifyPasswordEmail = (
                PendingModifyPasswordEmail.objects.filter(hash1=hash1).first()
            )

            if not relation or relation.hash1_verified:
                return STATUS(1)  # 1: invalid hash1 or verified hash1

            now = get_timestamp()
            stat = (now - relation.createdAt) > EMAIL_EXPIRE_SECONDS
            if stat:
                return STATUS(2)  # 2: expired

            hash2 = hashlib.sha256(str(get_timestamp()).encode()).hexdigest()
            relation.hash1_verified = True
            relation.hash2 = hash2
            relation.beginAt = get_timestamp()
            relation.save()
            return Response({"code": 0, "data": {"hash2": hash2}})

        elif stage == 2:
            hash1 = require(req.data, "hash1")
            hash2 = require(req.data, "hash2")
            curr_password = require(req.data, "password")

            relation: PendingModifyPasswordEmail = (
                PendingModifyPasswordEmail.objects.filter(
                    hash1=hash1, hash2=hash2
                ).first()
            )

            if not relation:
                return STATUS(1)

            now = get_timestamp()

            if (now - relation.beginAt) > RESETTING_STATUS_EXPIRE_SECONDS:
                return STATUS(2)  # 2: expired

            relation.user.password = curr_password
            relation.user.save()
            relation.delete()

            # sessions deleted after password modification
            SessionPool.objects.filter(user=relation.user).delete()

            return SUCC

        raise ParamErr("invalid stage")

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def set_remote_username(self, req: Request):
        repo = require(req.data, "repo", int)
        remote_name = require(req.data, "remote_name")

        repo = Repository.objects.filter(id=repo, disabled=False).first()

        if not repo or repo.project.id != req.auth["proj"].id:
            return STATUS(2)

        if len(remote_name) > 255:
            return STATUS(1)

        relation = UserRemoteUsernameAssociation.objects.filter(
            user=req.user, repository=repo
        ).first()

        if relation:
            relation.remote_name = remote_name
            relation.save()
        else:
            UserRemoteUsernameAssociation.objects.create(
                user=req.user, repository=repo, remote_name=remote_name
            )

        return SUCC
