# undefined 后端项目

## For Users

// TODO: 这里讲解后端配置文件的格式

## For Developers

请先阅读[项目规范](https://qynt1gy8vn.feishu.cn/docs/doccnLXFY9wOriyviGh5fv6NUgd)，然后再继续阅读本部分。

// TODO: 这里讲解怎么跑通 CI/CD

## 数据库模型

### UMS

#### User

+ id: BigAuto, primary_key
+ name: Text, indexed, 不允许重复
+ password: Text (sha256)
+ email: Text, indexed
+ avatar: Text (base64)
+ disabled: Boolean
+ createdAt: Float

#### SessionPool

+ sessionId: Text, indexed
+ user: FK
+ expiredAt: datetime (AUTO DELETE AFTER expiration)

#### Project

+ id: BigAuto, primary_key
+ title: Text, indexed
+ description: Text, indexed (Markdown)
+ disabled: Boolean
+ createdAt: Float

#### UserProjectAssociation

+ user: ForeignKey, indexed
+ project: ForeignKey, indexed
+ role: Text (enum "member", "dev", "qa", "sys")

// User + Project 联合唯一

#### ProjectInvitationAssociation

+ project: FK, ind
+ invitation: Text, ind（邀请码，用户注册使用直接加身份）
+ role: Text (enum role)

### RMS

#### Iteration

+ id: BigAuto, primary_key
+ project: ForeignKey, indexed
+ sid: Integer, 在项目中的 id
+ title: Text, 显示名
+ begin: Float
+ end: Float
+ disabled: Boolean
+ createdAt: Float

#### UserIterationAssociation

+ user: ForeignKey, indexed
+ iteration: ForeignKey, indexed

// user + iteration 联合唯一，代表 iteration 由用户主管

#### IR

+ id: BigAuto, pk
+ project: ForeignKey, indexed
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ rank: Integer // 同一个项目内，IR 按照 rank 顺序升序展示
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### SR

+ id: BA, pk
+ project: FK, indexed
+ title: 同上, indexed
+ description: 同上
+ priority: Integer // 开发工作中这一件事的重要性，方便进行完成进度统计
+ rank: Integer // 同一个 IR 内，SR 按照 rank 顺序升序展示
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### IRSRAssociation

出于一个 SR 可能解决多个 IR，一个 IR 可能对应多个 SR 的考虑，建立多对多联系。

+ IR: FK
+ SR: FK

#### SRIterationAssociation

+ SR: FK
+ iteration: FK

### RDTS

// TODO



## API

### `/ums/`

**所有请求都需要在cookie中包含sessionId，否则一律403 Forbidden** 

#### `[GET] /ums/user/`

Request params:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in
+ data
  + user: model_to_dict(User)
  + projects: filter and model_to_dict(Project)
  + schedule
    + done: {}
    + wip: {}
    + todo: {}

#### `[POST] /ums/login/`

Request Body:

- sessionId: str
- identity: str (username or email)
- password: str (already after md5, sha256 it and check)

Response:

+ code: 0 if success, 1 if already logged in, 2 if invalid identity, 3 if invalid password

#### `[POST] /ums/logout/`

Request Body:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in

#### `[POST] /ums/register/`

Request Body:

+ sessionId: str
+ name: str 
+ password: str (already after md5, sha256 it and check)
+ email: str (Remember to check if contains '@')
+ invitation: [Optional] str

Response:

+ code: 0 if success, 2 invalid invitation, 1 otherwise

#### `[POST] /ums/check_username_available/`

+ name: str

Response:

+ code: 0 if available, 1 otherwise

Explanation:

+ 这里 available 是说没有被占用，用户可以使用这个来注册

#### `[POST] /ums/check_email_available/`

+ email: str

Response:

+ code: 0 if available, 1 otherwise

#### `[POST] /ums/modify_user_role/`

+ project: int, project_id
+ user: int, user_id, user to be modified
+ role: str, the name of the new role, using (member, dev, qa, sys, supermaster)

Response:

+ code 0 if successful, 1 otherwise

#### `[POST] /ums/project/`

+ project: id of the project

Response:

+ code: 0 if successful, 1 otherwise
+ data: 
    + project: proj_to_list
    + users: filter and user_to_list

#### `[POST] /ums/modify_project/`

+ id
+ title
+ desc

Response

+ code 0 if successful else 1

#### `[POST] /ums/refresh_invitation/`

+ project

Response

+ code 0 if successful else 1
+ data 
    + invitation

#### `[POST] /ums/get_invitation/`

+ project

Response

+ code 0 if successful else 1
+ data 
    + invitation




