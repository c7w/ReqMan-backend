# undefined 后端项目

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
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### SR

+ id: BA, pk
+ project: FK, indexed
+ title: 同上, indexed
+ description: 同上
+ createdBy: FK
+ createdAt: FK
+ IR: FK
+ disabled: Boolean

#### SRIteration Association

+ SR: FK
+ iteration: FK

### RDTS

// TODO



## API

### `/ums/`

#### `[GET] /ums/user`

Request params:

+ sessionId: str

Response:

+ code: 0 if success, -1 if not found, 1 if disabled
+ data
  + user: model_to_dict(User)
  + projects: filter and model_to_dict(Project)
  + schedule
    + done: {}
    + wip: {}
    + todo: {}

#### `[POST] /ums/login`

Request Body:

- sessionId: str
- identity: str (username or email)
- password: str (already after md5, sha256 it and check)

Response:

+ code: 0 if success, 1 if already logged in, 2 if invalid identity, 3 if invalid password

#### `[POST] /ums/logout`

Request Body:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in

#### `[POST] /ums/register`

Request Body:

+ sessionId: str
+ name: str 
+ password: str (already after md5, sha256 it and check)
+ email: str (Remember to check if contains '@')

Response:

+ code: 0 if success, 1 otherwise

#### `[GET] /ums/check_username_available`

+ name: str

Response:

+ code: 0 if available, 1 otherwise

Explanation:

+ 这里 available 是说没有被占用，用户可以使用这个来注册

#### `[GET] /ums/check_email_available`

+ email: str

Response:

+ code: 0 if available, 1 otherwise



// TODO